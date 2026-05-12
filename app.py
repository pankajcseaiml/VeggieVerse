from flask import Flask, render_template, request, jsonify, session
import json
import uuid
import re
from datetime import datetime
import chatbot
import db

app = Flask(__name__)
app.secret_key = 'LOAD_FROM_ENVIRONMENT_VARIABLE'

# Load intents
intents_path = 'data/intents.json'
with open(intents_path, 'r', encoding='utf-8') as f:
    intents = json.load(f)

# Try to load model
model_loaded = chatbot.load_chatbot_data()

@app.route('/')
def home():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    if 'order_state' not in session:
        session['order_state'] = {'step': 0}
    if 'reservation_state' not in session:
        session['reservation_state'] = {'step': 0}
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    # Reload model data if it was trained while app was running
    global model_loaded
    if not model_loaded:
        model_loaded = chatbot.load_chatbot_data()
        
    if not model_loaded:
        return jsonify({"response": "The chatbot model hasn't been trained yet. Please run train.py first!"})

    user_message = request.json.get('message', '').strip()
    if not user_message:
        return jsonify({"response": "Please enter a message."})

    session_id = session.get('session_id', str(uuid.uuid4()))
    
    # Handle cancellation
    if user_message.lower() in ['cancel', 'stop', 'quit', 'exit', 'nevermind', 'abort']:
        session['order_state'] = {'step': 0}
        session['reservation_state'] = {'step': 0}
        return jsonify({"response": "Okay, I've cancelled that. How else can I help you today?"})
    
    # Handle ongoing multi-turn flows
    order_state = session.get('order_state', {'step': 0})
    reservation_state = session.get('reservation_state', {'step': 0})
    
    bot_reply = ""
    intent_tag = "unknown"

    if order_state['step'] > 0:
        bot_reply, next_step = handle_order_flow(user_message, order_state)
        session['order_state'] = next_step
        intent_tag = "place_order_flow"
        
    elif reservation_state['step'] > 0:
        bot_reply, next_step = handle_reservation_flow(user_message, reservation_state)
        session['reservation_state'] = next_step
        intent_tag = "reservation_flow"
        
    else:
        ints = chatbot.predict_class(user_message)
        intent_tag = ints[0]['intent']
        
        if intent_tag == 'view_menu':
            bot_reply = db.get_full_menu()
            
        elif intent_tag == 'item_info':
            match = re.search(r'(about|in)\s+(.*)', user_message.lower())
            if match:
                item_name = match.group(2).strip("?")
                bot_reply = db.get_item_info(item_name)
            else:
                bot_reply = "Which item would you like to know about?"
                
        elif intent_tag == 'place_order':
            session['order_state'] = {'step': 1}
            bot_reply = "I'd be happy to take your order! May I have your name?"
            
        elif intent_tag == 'reservation':
            session['reservation_state'] = {'step': 1}
            bot_reply = "I can help you book a table. What name should the reservation be under?"
            
        else:
            bot_reply, _ = chatbot.get_response(ints, intents)

    # Convert newlines to HTML line breaks for rendering
    bot_reply = bot_reply.replace('\n', '<br>')
    
    db.log_chat(session_id, user_message, bot_reply, intent_tag)
    
    return jsonify({"response": bot_reply})

def handle_order_flow(message, state):
    step = state['step']
    if step == 1:
        state['name'] = message
        state['step'] = 2
        return f"Thanks {message}. What's your phone number?", state
    elif step == 2:
        state['phone'] = message
        state['step'] = 3
        return "Great. What would you like to order? (e.g., '2 Paneer Tikka, 1 Mango Lassi')", state
    elif step == 3:
        items_list = []
        parts = message.split(',')
        for part in parts:
            match = re.search(r'(\d+)\s+(.*)', part.strip())
            if match:
                items_list.append((match.group(2).strip(), int(match.group(1))))
            else:
                items_list.append((part.strip(), 1))
                
        state['items'] = items_list
        order_id, msg = db.save_order(state['name'], state['phone'], items_list)
        state['step'] = 0 
        return msg, state
    
    return "Something went wrong with the order flow.", {'step': 0}

def handle_reservation_flow(message, state):
    step = state['step']
    if step == 1:
        state['name'] = message
        state['step'] = 2
        return f"Thanks {message}. What's your phone number?", state
    elif step == 2:
        state['phone'] = message
        state['step'] = 3
        return "For how many guests?", state
    elif step == 3:
        try:
            guests = int(re.search(r'\d+', message).group())
        except:
            guests = 2
        state['guests'] = guests
        state['step'] = 4
        return "When would you like to reserve? Please use format YYYY-MM-DD HH:MM (e.g., 2026-05-15 19:00)", state
    elif step == 4:
        try:
            dt = datetime.strptime(message.strip(), "%Y-%m-%d %H:%M")
            dt_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            res_id, msg = db.save_reservation(state['name'], state['phone'], dt_str, state['guests'])
            state['step'] = 0
            return msg, state
        except ValueError:
            return "Please enter the date and time in the exact format: YYYY-MM-DD HH:MM (e.g., 2026-05-15 19:00) or type 'cancel' to exit.", state

if __name__ == '__main__':
    app.run(debug=True)
