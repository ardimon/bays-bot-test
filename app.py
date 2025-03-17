from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///farmorsdata.db'
db = SQLAlchemy(app)

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Database model for senere brug
class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    last_message = db.Column(db.Text)
    preferences = db.Column(db.Text)

with app.app_context():
    db.create_all()

# Web forsiden
@app.route('/')
def index():
    return render_template('chat.html')

# API endpoint til at chatte
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    
    intro = (
        "Du er en venlig, tålmodig og pædagogisk hjælper, som guider Marianne, der er 73 år. "
        "Du taler roligt og letforståeligt dansk. Du giver trin-for-trin forklaringer ét skridt ad gangen. "
        "Du opmuntrer indimellem og minder om, at samtalen er privat."
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": intro},
            {"role": "user", "content": user_input}
        ]
    )

    reply = response.choices[0].message.content
    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run(debug=True)
