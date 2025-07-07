from openai import OpenAI
import shelve
from dotenv import load_dotenv
import os
import time
import logging
import json
from app.services.scheduler import schedule_job, delete_task
from app.utils.time_handler import get_location_from_ip, get_current_datetime_by_timezone
from app.utils.pending_task import get_pending_tasks

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def upload_file(path):
    # Upload a file with an "assistants" purpose
    file = client.files.create(
        file=open("../../data/airbnb-faq.pdf", "rb"), purpose="assistants"
    )

system_prompt = """
You are a friendly and helpful WhatsApp AI assistant.

Your responsibilities:

1. Detect whether the user is:
    - Engaged in a **casual conversation** ("normal chat")
    - Making a **scheduling request** via WhatsApp, email, or call

2. If it's a **normal chat**, respond conversationally.
    - Always return the response in this JSON format:
    {
        "type": [],
        "message": "your conversational reply here"
    }

3. If it's a **scheduling request follow-up**, follow this behavior:
    - All responses MUST use this format:
    {
        "type": [],
        "message": "your question or message here"
    }
    - Always ask for via whatsapp, email, or call if not mentioned.

4. If user wants to delete a scheduled task:
    - Call `get_pending_tasks` to list all current pending jobs.
    - Ask the user which one to delete based on task name, type, or time.
    - Confirm with the user before calling `delete_task`.

5. If user wants to reschedule a task:
    - Follow deletion flow as above.
    - After successful deletion, ask for the new time and then call `schedule_job` again.

Only return this JSON (with correct keys) if the user confirms. Do not include any extra text.
"""

tools = [
    {
        "type": "function",
        "function": {
            "name": "schedule_job",
            "description": "Schedules a task on WhatsApp, email, call or any combination of these three.",
            "parameters": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Channels to use: whatsapp, email, call"
                    },
                    "task": {"type": "string"},
                    "time": {"type": "string", "format": "date-time"},
                    "reminder_message": {"type": "string"},
                    "email": {"type": "string"},
                    "email_subject": {"type": "string"},
                    "email_body": {"type": "string"},
                    "mobile_no": {"type": "string"},
                    "call_message": {"type": "string"}
                },
                "required": ["type", "task", "time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Deletes a scheduled task by job_id",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "The ID of the job to delete"
                    }
                },
                "required": ["job_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_pending_tasks",
            "description": "Fetches all pending tasks for a user.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]

def create_assistant():
    assistant = client.beta.assistants.create(
        name="WhatsApp AI Assistant",
        instructions=system_prompt,
        tools=tools,
        model="gpt-4o-mini-2024-07-18",
    )
    return assistant

OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

if not OPENAI_ASSISTANT_ID:
    assistant = create_assistant()
    OPENAI_ASSISTANT_ID = assistant.id
    
    # Optionally write to .env or print it
    print("🔑 New Assistant Created:", OPENAI_ASSISTANT_ID)

def check_if_thread_exists(wa_id):
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(wa_id, None)

def store_thread(wa_id, thread_id):
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = thread_id

def wait_for_active_run_to_finish(thread_id, timeout=60):
    """Check for active run in a thread and wait until it's done."""
    runs = client.beta.threads.runs.list(thread_id=thread_id)
    active_run = next((r for r in runs.data if r.status == "in_progress"), None)

    if active_run:
        logging.info(f"🕒 Waiting for active run {active_run.id} to finish...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=active_run.id)
            if run.status in ["completed", "failed", "cancelled", "expired"]:
                return True
            time.sleep(1)
        logging.warning("⚠️ Timeout while waiting for previous run to finish.")
        return False
    return True

def run_assistant(thread):
    assistant = client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID)

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    while run.status not in ["completed", "failed"]:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    new_message = messages.data[0].content[0].text.value
    logging.info(f"🔁 Assistant response: {new_message}")
    return new_message

def generate_response(message_body, wa_id, name):
    thread_id = check_if_thread_exists(wa_id)
    if thread_id is None:
        logging.info(f"🧵 Creating new thread for {name} ({wa_id})")
        thread = client.beta.threads.create()
        store_thread(wa_id, thread.id)
    else:
        logging.info(f"📦 Retrieving existing thread for {name} ({wa_id})")
        thread = client.beta.threads.retrieve(thread_id)

    # 🛑 Wait if a run is still active
    if not wait_for_active_run_to_finish(thread.id):
        logging.warning("⏳ Run still active. Skipping new message.")
        return {"type": [], "message": "Please wait, I'm still working on your last request."}
    
    t = get_current_datetime_by_timezone(get_location_from_ip()["timezone"])["current_time"]
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f'{t}\n' + message_body,
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=OPENAI_ASSISTANT_ID,
    )

    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        if run.status == "completed":
            break

        if run.status == "requires_action":
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []

            for call in tool_calls:
                fn_name = call.function.name
                arguments = json.loads(call.function.arguments)

                if fn_name == "get_pending_tasks":
                    result = get_pending_tasks(wa_id)
                elif fn_name == "delete_task":
                    result = delete_task(wa_id, arguments["job_id"])
                elif fn_name == "schedule_job":
                    result = schedule_job(wa_id, arguments)
                else:
                    result = {"error": f"Unknown function: {fn_name}"}

                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": json.dumps(result),
                })

            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )

        elif run.status in ["failed", "cancelled"]:
            return {"type": [], "message": "❌ Something went wrong."}

        time.sleep(1)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    assistant_reply = messages.data[0].content[0].text.value

    try:
        parsed = json.loads(assistant_reply)
        return parsed.get("message", "🙂 I'm here to help!")
    except json.JSONDecodeError:
        return assistant_reply
