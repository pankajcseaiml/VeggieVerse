# Vegetarian Restaurant Chatbot (Green Bites 🌿)

A complete, AI-driven chatbot for a vegetarian restaurant. Built with Flask, TensorFlow/Keras, NLTK, and MySQL.

## Features
- **NLP Intent Classification**: Trained using a custom neural network via Keras.
- **MySQL Integration**: Live fetching of menu items and saving of orders/reservations.
- **Session-aware Multi-turn Flows**: Handles step-by-step ordering and booking.
- **Modern UI**: Responsive, animated, dark-green themed frontend.

## Prerequisites
- Python 3.10+
- MySQL Server running locally on port 3306

## Setup Instructions

1. **Set up the Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows use:
   venv\Scripts\activate
   # On macOS/Linux use:
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Database Setup**
   Ensure your MySQL server is running (e.g., via XAMPP, WAMP, or standalone).
   Execute the `database/schema.sql` script to create the `veg_restaurant_db` database and its tables:
   ```bash
   mysql -u root -p < database/schema.sql
   ```
   *Note: If your MySQL root user has a password, update the `db.py` file inside the `get_connection()` function to include your password.*

3. **Train the NLP Model**
   Run the training script to generate the model files (`chatbot_model.h5`, `words.pkl`, `classes.pkl`).
   ```bash
   python train.py
   ```

4. **Run the Application**
   Start the Flask server.
   ```bash
   python app.py
   ```

5. **Test the Chatbot**
   Open your browser and navigate to `http://localhost:5000`.
