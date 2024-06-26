from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import base64
import io
from PIL import Image
import google.generativeai as genai
import os
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure Google Generative AI (replace with your actual API key)
genai.configure(api_key='AIzaSyDpSs5G9QzHoc3r0Y85M_bLuy3eTdEg8mE')

# Mock user data (replace with your actual user authentication logic)
mock_users = {'admin': {'password': 'admin'}}  # Replace with actual user database or integration

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# User class for Flask-Login (replace with your actual User model if using a database)
class User(UserMixin):
    pass

# Callback to reload the user object from the user ID stored in the session
@login_manager.user_loader
def load_user(user_id):
    if user_id in mock_users:
        user = User()
        user.id = user_id
        return user
    return None

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('snap'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in mock_users and request.form['password'] == mock_users[username]['password']:
            user = User()
            user.id = username
            login_user(user)
            return redirect(url_for('snap'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/snap')
@login_required
def snap():
    return render_template('snap.html')

@app.route('/generate-response', methods=['POST'])
@login_required
def generate_response():
    try:
        data = request.get_json()
        imageDataUrl = data.get('image')
        base64_data = imageDataUrl.split(',')[1]
        byte_data = base64.b64decode(base64_data)

        image = Image.open(io.BytesIO(byte_data))
        model = genai.GenerativeModel('gemini-pro-vision')
        response = model.generate_content([
            "First, give a thorough explanation of the person's clothing, concentrating on a single item. Consider how it looks in light of the newest fashions. For conciseness and clarity, use bullet points. Second, please provide additional fashion advice based on what the wearer is now wearing. These should be divided into separate sections with titles that read **_Feedback:_** and **_Recommendations_** ,(Also consider current weather)(only give results on outfit)",
            image
        ])

        feedback_text = response.text  # Extract the actual text
        print(feedback_text)  # Log the response text

        return jsonify({'feedback': feedback_text})

    except Exception as e:
        print(f"Error processing image: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/feedback')
@login_required
def feedback():
    return render_template('feedback.html')

if __name__ == '__main__':
    app.run(debug=True)
