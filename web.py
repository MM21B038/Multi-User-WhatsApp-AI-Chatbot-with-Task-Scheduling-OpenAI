from flask import Flask, render_template, request
import pandas as pd
from app.utils.pending_task import get_tasks
import os

app = Flask(__name__)

# Discover available WhatsApp IDs (status_cache/<wa_id>/)
def list_wa_ids():
    base_path = "status_cache"
    if not os.path.exists(base_path):
        return []
    return [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]

@app.route('/')
def dashboard():
    wa_id = request.args.get("wa_id")
    wa_ids = list_wa_ids()

    if wa_id:
        try:
            data = get_tasks(wa_id)
            df = pd.DataFrame.from_dict(data, orient='index')
            df.index.name = 'ID'
            df = df.reset_index()
            table = df.to_html(classes="table table-striped table-bordered", index=False)
        except Exception as e:
            table = f"<p>Error loading data for {wa_id}: {e}</p>"
    else:
        table = "<p>Please select a WhatsApp ID from the dropdown.</p>"

    return render_template("dashboard.html", table=table, wa_ids=wa_ids, selected_wa_id=wa_id)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
