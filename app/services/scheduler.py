from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from app.services.notifier import send_email, send_whatsapp_message, make_voice_call
from datetime import datetime
from dateutil.parser import parse
import diskcache
import pytz
import os

# Timezone
IST = pytz.timezone("Asia/Kolkata")

# Shared ID counter cache (namespaced by sender_id)
id_cache = diskcache.Cache("id_cache")

# Scheduler setup
scheduler = BackgroundScheduler()
scheduler.start()


# ✅ Helper: Get status_cache for a specific sender_id (separate DB)
def get_status_cache(sender_id):
    path = os.path.join("status_cache", sender_id)
    os.makedirs(path, exist_ok=True)
    return diskcache.Cache(directory=path)


# ✅ Schedule a new job
def schedule_job(sender_id, task):
    time = parse(task["time"])
    status_cache = get_status_cache(sender_id)

    # Initialize ID if not already present
    if "ids" not in id_cache:
        id_cache["ids"] = 1000  # or any base number you want

    # Get user's status data
    status_data = status_cache.get("status", {})

    def add_job(job_type, func, args):
        id_cache["ids"] += 1
        job_id = str(id_cache["ids"])
        scheduler.add_job(
            func,
            'date',
            run_date=time,
            args=args,
            id=job_id
        )
        status_data[job_id] = {
            "task": task["task"],
            "type": job_type,
            "schedule_time": datetime.now(IST).isoformat(),
            "event_time": time.isoformat(),
            "status": "pending"
        }

    if "whatsapp" in task["type"]:
        add_job("whatsapp", send_whatsapp_message, [sender_id, task["reminder_message"]])

    if "email" in task["type"]:
        add_job("email", send_email, [task["email"], task["email_subject"], task["email_body"]])

    if "call" in task["type"]:
        add_job("call", make_voice_call, [task["mobile_no"], task["call_message"]])

    status_cache["status"] = status_data


# ✅ Delete a job (per sender)
def delete_task(sender_id, job_id):
    try:
        scheduler.remove_job(job_id)
        status_cache = get_status_cache(sender_id)
        status_data = status_cache.get("status", {})
        if job_id in status_data:
            status_data[job_id]["status"] = "deleted"
            status_cache["status"] = status_data
        return True
    except Exception as e:
        print(f"Error deleting job {job_id}: {e}")
        return False


# ✅ Get all pending tasks for a sender
def get_pending_tasks(sender_id):
    status_cache = get_status_cache(sender_id)
    return status_cache.get("status", {})


# ✅ Background listener to track job execution results
def job_listener(event):
    job_id = str(event.job_id)
    base_path = "status_cache"

    # Scan each user's DB to find the matching job_id
    for sender_id in os.listdir(base_path):
        user_path = os.path.join(base_path, sender_id)
        if not os.path.isdir(user_path):
            continue

        status_cache = diskcache.Cache(user_path)
        status_data = status_cache.get("status", {})

        if job_id in status_data:
            status_data[job_id]["status"] = "failed" if event.exception else "completed"
            status_cache["status"] = status_data
            break


# Attach the job listener to monitor execution
scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
