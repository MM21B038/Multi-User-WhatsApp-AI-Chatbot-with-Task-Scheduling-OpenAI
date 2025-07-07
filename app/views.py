import logging
import json
from flask import Blueprint, request, jsonify, current_app
from .decorators.security import signature_required
from .utils.whatsapp_utils import (
    process_whatsapp_message,
    is_valid_whatsapp_message,
)
from .utils.voice_handler import handle_voice_message

webhook_blueprint = Blueprint("webhook", __name__)


def handle_message():
    body = request.get_json()

    # Handle WhatsApp status events (e.g., delivered, read)
    if (
        body.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("statuses")
    ):
        logging.info("📬 Received a WhatsApp status update.")
        return jsonify({"status": "ok"}), 200

    try:
        if is_valid_whatsapp_message(body):
            message = body["entry"][0]["changes"][0]["value"]["messages"][0]
            msg_type = message.get("type")
            logging.info(f"📥 Received message type: {msg_type}")

            if msg_type == "audio":
                transcribed_text = handle_voice_message(message)
                if not transcribed_text:
                    return jsonify({"status": "error", "message": "Voice transcription failed"}), 500

                # Convert it to text message for downstream processing
                message["type"] = "text"
                message["text"] = {"body": transcribed_text}
                logging.info(f"🔊 Voice message transcribed as: {transcribed_text}")

            process_whatsapp_message(body)
            return jsonify({"status": "ok"}), 200

        else:
            logging.warning("❌ Not a valid WhatsApp API event")
            return jsonify({"status": "error", "message": "Not a WhatsApp API event"}), 404

    except json.JSONDecodeError:
        logging.error("❌ Failed to decode JSON")
        return jsonify({"status": "error", "message": "Invalid JSON provided"}), 400
    except Exception as e:
        logging.exception("💥 Unhandled error in handle_message")
        return jsonify({"status": "error", "message": str(e)}), 500


def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == current_app.config["VERIFY_TOKEN"]:
            logging.info("✅ WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            logging.warning("❌ VERIFICATION_FAILED")
            return jsonify({"status": "error", "message": "Verification failed"}), 403
    else:
        logging.warning("❌ MISSING_PARAMETER")
        return jsonify({"status": "error", "message": "Missing parameters"}), 400


@webhook_blueprint.route("/webhook", methods=["GET"])
def webhook_get():
    return verify()


@webhook_blueprint.route("/webhook", methods=["POST"])
@signature_required
def webhook_post():
    return handle_message()