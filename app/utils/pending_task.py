import os
import diskcache

def get_pending_tasks(sender_id):
    # Load the specific sender's status cache
    status_path = os.path.join("status_cache", sender_id)
    status_cache = diskcache.Cache(status_path)

    # Get all statuses stored in this sender's DB
    status_data = status_cache.get("status", {})

    # Filter only pending tasks
    pending_tasks = {
        job_id: info
        for job_id, info in status_data.items()
        if info.get("status") == "pending"
    }

    return pending_tasks

"""def get_tasks(sender_id):
    # Load the specific sender's status cache
    status_path = os.path.join("status_cache", sender_id)
    status_cache = diskcache.Cache(status_path)

    # Get all statuses stored in this sender's DB
    status_data = status_cache.get("status", {})

    # Filter only pending tasks
    pending_tasks = {
        job_id: info
        for job_id, info in status_data.items()
    }

    return pending_tasks

import os
import diskcache"""

def get_tasks(sender_id):
    status_path = os.path.join("status_cache", sender_id)
    status_cache = diskcache.Cache(status_path)
    return status_cache.get("status", {})