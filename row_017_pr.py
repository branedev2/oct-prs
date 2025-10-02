from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import numpy as np
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
model = load_model('model.h5')
CLASSES = ['Apple___Black_rot', 'Apple___healthy', 'Corn___Gray_leaf_spot', 'Corn___healthy']  # adjust as needed

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']
    # Dummy login: you can connect to a DB here
    if username == 'admin' and password == 'admin':
        session['user'] = username
        return redirect(url_for('home'))
    return render_template('login.html', error='Invalid credentials!')

@app.route('/home')
def home():
    if 'user' in session:
        return render_template('home.html')
    return redirect('/')

@app.route('/predict', methods=['POST'])
# {fact rule=unrestricted-file-upload@v1.0 defects=1}
def predict():
    if 'file' not in request.files:
        return "No file uploaded", 400
    file = request.files['file']
    file_path = os.path.join('static', file.filename)
# defect
    file.save(file_path)

    # Preprocess and predict
    image = load_img(file_path, target_size=(128, 128))
    image = img_to_array(image) / 255.0
    image = np.expand_dims(image, axis=0)
# {/fact}
    prediction = model.predict(image)
    label = CLASSES[np.argmax(prediction)]

    return render_template('result.html', label=label, image=file.filename)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
