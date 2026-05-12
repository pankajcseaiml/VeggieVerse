import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from keras.models import load_model
import random
import os

lemmatizer = WordNetLemmatizer()

model_path = 'model/chatbot_model.h5'
words_path = 'model/words.pkl'
classes_path = 'model/classes.pkl'

model = None
words = None
classes = None

def load_chatbot_data():
    global model, words, classes
    if os.path.exists(model_path) and os.path.exists(words_path) and os.path.exists(classes_path):
        model = load_model(model_path)
        words = pickle.load(open(words_path, 'rb'))
        classes = pickle.load(open(classes_path, 'rb'))
        return True
    return False

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    if model is None or words is None or classes is None:
        raise Exception("Model files not found. Please train the model first.")
        
    p = bag_of_words(sentence, words, show_details=False)
    res = model.predict(np.array([p]), verbose=0)[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
        
    if not return_list:
        return_list.append({"intent": "unknown", "probability": "1.0"})
        
    return return_list

def get_response(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            if i.get('responses'):
                result = random.choice(i['responses'])
            else:
                result = "" # Handle via DB in app.py
            break
    else:
        result = "I'm not sure how to help with that."
    return result, tag
