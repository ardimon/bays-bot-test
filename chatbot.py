import requests
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load .env filen med API-nøgle
load_dotenv()

# Hent API-nøglen fra miljøvariabler
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

user_id = "marianne123"

def get_user_data(user_id):
    response = requests.get(f"http://127.0.0.1:5000/get_user_data/{user_id}")
    if response.status_code == 200:
        return response.json()
    else:
        return {}

def save_user_data(user_id, last_message, preferences):
    payload = {
        "user_id": user_id,
        "last_message": last_message,
        "preferences": preferences
    }
    response = requests.post("http://127.0.0.1:5000/save_user_data", json=payload)
    if response.status_code == 200:
        print("Data gemt i API")
    else:
        print("Noget gik galt ved gemning")

def chat_with_farmor(user_data):
    intro = (
        "Du er Farmors Chatbot, en venlig, tålmodig og pædagogisk hjælper, som guider Marianne, der er 73 år og ikke er vant til computere, telefoner eller teknologi..."
    )

    user_input = input("Marianne siger: ")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": intro},
            {"role": "user", "content": user_input}
        ]
    )

    reply = response.choices[0].message.content
    print("Farmor svarer:", reply)

    save_user_data(user_id, user_input, user_data.get('preferences', ''))

if __name__ == "__main__":
    print("API-nøgle der bruges lige nu:", os.getenv('OPENAI_API_KEY'))
    data = get_user_data(user_id)
    chat_with_farmor(data)
