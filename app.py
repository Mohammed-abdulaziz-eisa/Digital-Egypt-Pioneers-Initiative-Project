from flask import Flask, request, jsonify, render_template
import tensorflow as tf
import numpy as np
import pandas as pd
import pickle
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Ensure NLTK resources are downloaded
nltk.download('punkt')
nltk.download('stopwords')
# Initialize Flask app
app = Flask(__name__)
# Load the trained model
model = tf.keras.models.load_model('model/text_classification_model.h5')

# Load the tokenizer
with open('model/tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

# Load data to create label map
bbc_text = pd.read_csv('bbc-text.csv')  # Ensure this file is accessible
categories = bbc_text['category'].unique()  # Get unique categories

# Assuming the following mapping
label_map = {
    0: 'tech',
    1: 'business',
    2: 'sport',
    3: 'entertainment',
    4: 'politics'
}
# Function to preprocess input text
def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text)  # Tokenize
    tokens = [word for word in tokens if word.lower() not in stop_words]  # Remove stopwords
    return ' '.join(tokens)
# Home route to render input form
@app.route('/')
def home():
    return render_template('index.html')

# Prediction route
@app.route('/predict', methods=['POST'])
def predict():
    # Get input text from the form
    input_text = request.form.get('text')
    # Input validation
    if not input_text or len(input_text.strip()) < 3:
        return jsonify({'error': 'Please enter a valid text with at least 3 characters.'})
    # Preprocess the input text
    processed_text = preprocess_text(input_text)
    # Tokenize and preprocess the text
    sequences = tokenizer.texts_to_matrix([processed_text], mode='binary')  # Ensure this matches your tokenizer training
    # Get the prediction
    predictions = model.predict(sequences)
    predicted_class_index = np.argmax(predictions[0])
    predicted_probability = predictions[0][predicted_class_index]  # Get probability of the predicted class

    # Map the predicted class to the category name
    predicted_category = label_map.get(predicted_class_index, "Unknown")

    return jsonify({
        'input_text': input_text,
        'predicted_category': predicted_category,
        'predicted_probability': float(predicted_probability)  # Convert to float for JSON serialization
    })

if __name__ == '__main__':
    app.run(debug=True)