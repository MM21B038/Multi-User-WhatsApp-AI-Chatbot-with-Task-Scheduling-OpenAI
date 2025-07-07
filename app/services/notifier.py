import smtplib
import re
import requests
from email.message import EmailMessage
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import os
from dotenv import load_dotenv

# Load from .env
load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERSION = os.getenv("VERSION")
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

def send_whatsapp_message(to: str, message: str):
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"📤 WhatsApp: {response.status_code} - {response.text}")

def send_email(to_email: str, subject: str, body: str):
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SMTP_EMAIL
        msg["To"] = to_email
        msg.set_content(body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SMTP_EMAIL, SMTP_PASSWORD)
            smtp.send_message(msg)
        print("✅ Email sent to", to_email)
    except Exception as e:
        print("❌ Email error:", e)

def make_voice_call(to_number: str, message: str):
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        cleaned_number = re.sub(r"[^\d+]", "", to_number)
        voice = VoiceResponse()
        voice.say(message)

        call = client.calls.create(
            to=cleaned_number,
            from_=TWILIO_PHONE_NUMBER,
            twiml=str(voice)
        )
        print(f"📞 Voice call started to {cleaned_number}, SID: {call.sid}")
    except Exception as e:
        print("❌ Voice call error:", e)