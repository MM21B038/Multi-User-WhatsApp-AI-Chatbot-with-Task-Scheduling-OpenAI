import sys
import os
from dotenv import load_dotenv
import logging


def load_configurations(app):
    load_dotenv()
    app.config["ACCESS_TOKEN"] = os.getenv("ACCESS_TOKEN")
    app.config["YOUR_PHONE_NUMBER"] = os.getenv("YOUR_PHONE_NUMBER")
    app.config["APP_ID"] = os.getenv("APP_ID")
    app.config["APP_SECRET"] = os.getenv("APP_SECRET")
    app.config["RECIPIENT_WAID"] = os.getenv("RECIPIENT_WAID")
    app.config["VERSION"] = os.getenv("VERSION")
    app.config["PHONE_NUMBER_ID"] = os.getenv("PHONE_NUMBER_ID")
    app.config["VERIFY_TOKEN"] = os.getenv("VERIFY_TOKEN")
    app.config["TOGETHER_API_KEY"] = os.getenv("TOGETHER_API_KEY")
    app.config["OPENAI_API_KEY"] = os.getenv("CHATGPT_API_KEY")
    app.config["SMTP_EMAIL"] = os.getenv("SMTP_EMAIL")
    app.config["SMTP_PASSWORD"] = os.getenv("SMTP_PASSWORD")
    app.config["TWILIO_SID"] = os.getenv("TWILIO_SID")
    app.config["TWILIO_AUTH_TOKEN"] = os.getenv("TWILIO_AUTH_TOKEN")
    app.config["TWILIO_PHONE_NUMBER"] = os.getenv("TWILIO_PHONE_NUMBER")
    app.config["OPENAI_ASSISTANT_ID"] = os.getenv("OPENAI_ASSISTANT_ID")
    

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
