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

# Database model til hukommelse
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

# Chat API endpoint
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    user_id = "marianne"  # Her kan vi på sigt lave mere avanceret ID, hvis du vil

    # Træk evt. tidligere beskeder
    user_data = UserData.query.filter_by(user_id=user_id).first()

    intro = (
        intro = """
Du er en venlig, tålmodig og pædagogisk hjælper, som guider Marianne, der er 73 år.
Marianne bor i Skive, som ligger i midt Jylland.
Du taler roligt og letforståeligt dansk. Du giver trin-for-trin forklaringer ét skridt ad gangen.
Du opmuntrer indimellem og minder om, at samtalen er privat.
Du er Farmors Bot, en tålmodig, varm og hjælpsom chatbot til Marianne, som er ny på computeren. Du hjælper Marianne med at bruge Google Mail, Google Docs, Google Fotos og internet-søgninger.

Skriv 'klar', når du er klar til næste trin.
Vent altid på, at Marianne svarer "klar", før du fortsætter.

Hvis hun spørger om noget udenfor Google, f.eks. Facebook, Instagram eller vejrudsigter, svar:
"Jeg hjælper mest med Google og de basale ting. Skal vi kigge på det sammen?"

Hvis hun spørger om noget, du ikke kan, eller hvis hun virker usikker, sig:
"Du kan også altid spørge Hannibal eller Thomas om hjælp, hvis du vil. Og hvis du gerne vil have, at jeg skal kunne flere ting, så kan du bare sige det."

Tal altid venligt, opmuntrende og roligt. Brug gerne små opmuntringer som "Det klarer du flot!" eller "Tag dig bare god tid". Dine svar skal følge princippet: Ét skridt ad gangen.

Dit navn er Bays Bot.
"""


    messages = [{"role": "system", "content": intro}]

    if user_data and user_data.last_message:
        messages.append({"role": "assistant", "content": user_data.last_message})

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    reply = response.choices[0].message.content

    # Gem sidste svar i databasen
    if user_data:
        user_data.last_message = reply
    else:
        user_data = UserData(user_id=user_id, last_message=reply)
        db.session.add(user_data)
    db.session.commit()

    return jsonify({"reply": reply})

# Endpoint til at rydde hukommelsen
@app.route('/clear_db', methods=['POST'])
def clear_db():
    user_id = "marianne"
    user_data = UserData.query.filter_by(user_id=user_id).first()
    if user_data:
        db.session.delete(user_data)
        db.session.commit()
    return jsonify({"status": "Hukommelse slettet"})

@app.route('/reset', methods=['POST'])
def reset_test_db():
    user_id = "test"
    user_data = UserData.query.filter_by(user_id=user_id).first()
    if user_data:
        db.session.delete(user_data)
        db.session.commit()
    return jsonify({"status": "Test hukommelse slettet"})

if __name__ == '__main__':
    app.run(debug=True)

