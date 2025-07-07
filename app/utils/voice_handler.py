import os
import requests
import logging
import whisper
from flask import current_app

whisper_model = whisper.load_model("base")

def get_media_url(media_id):
    version = current_app.config["VERSION"]
    access_token = current_app.config["ACCESS_TOKEN"]
    url = f"https://graph.facebook.com/{version}/{media_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.json().get("url")

def download_audio(media_url, media_id):
    headers = {"Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}"}
    response = requests.get(media_url, headers=headers)
    
    tmp_dir = os.path.join(os.getcwd(), "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    filepath = os.path.join(tmp_dir, f"voice_{media_id}.ogg")
    with open(filepath, "wb") as f:
        f.write(response.content)

    logging.info(f"✅ Saved audio to: {filepath}")
    return filepath

def transcribe_audio(file_path):
    result = whisper_model.transcribe(file_path, task="translate")
    logging.info(f"✅ Transcription result: {result['text']}")
    return result['text']

def handle_voice_message(message):
    media_id = message["audio"]["id"]
    media_url = get_media_url(media_id)
    if not media_url:
        logging.error("❌ Failed to get media URL")
        return None

    file_path = download_audio(media_url, media_id)
    return transcribe_audio(file_path)