import logging
from flask import current_app, jsonify
import json
import requests
from app.services.openai_service import generate_response
import re

def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )



def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        return response


def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text


"""def process_whatsapp_message(body):
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    user_input = message["text"]["body"]

    # Log user message
    log_time()
    log_user_input(user_input)

    # Classify user intent using LLM
    task = classify_intent(data_status=False)
    print(task)
    task = json.loads(task)
    print(type(task))

    if task["type"]:
        if "fetching_pending_scheduled_tasks" in task["type"]:
            log_time()
            log_bot_response(task["message"])
            send_message(get_text_message_input(current_app.config["RECIPIENT_WAID"], task["message"]))
            task = classify_intent(data_status=True)
            task = json.loads(task)
            log_time()
            log_bot_response(task["message"])
            send_message(get_text_message_input(current_app.config["RECIPIENT_WAID"], task["message"]))
        else:
            print("scheduling job ...")
            unique_id = 10
            schedule_job(current_app.config["RECIPIENT_WAID"], task, unique_id)
            log_time()
            log_bot_response("Bot: I have successfully scheduled your reminder. Can I do anything else for you?")
            send_message(get_text_message_input(current_app.config["RECIPIENT_WAID"], "I have successfully scheduled your reminder\nCan I do anything else for you?"))
            print("scheduled job")                
            unique_id = unique_id + 10
    else:
        log_time()
        log_bot_response(task["message"])
        send_message(get_text_message_input(current_app.config["RECIPIENT_WAID"], task["message"]))
"""
def process_whatsapp_message(body):
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_body = message["text"]["body"]

    # OpenAI Integration
    response = generate_response(message_body, wa_id, name)
    response = process_text_for_whatsapp(response)
    data = get_text_message_input(wa_id, response)
    send_message(data)


def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )
