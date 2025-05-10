# import os
import json
# import base64
# import requests
from google.cloud import pubsub_v1

# ─── CONFIG ───
PROJECT_ID    = "avian-cosmos-458703-g3"
TOPIC_ID      = "Seminar-List-Automation"
SLACK_WEBHOOK = "https://webhook.site/5297a000-62ea-435d-8530-745122adb05b"

publisher  = pubsub_v1.PublisherClient()
TOPIC_PATH = publisher.topic_path(PROJECT_ID, TOPIC_ID)

# ─── FORM ID TO BRAND MAPPING ───
# ─── FORM ID TO BRAND MAPPING ───
FORM_ID_TO_BRAND = {
    "681ea1dd75c61440f40537c0": "ECE",
    "681e9dc9d9b9d5e9e10682e6": "TPRA",
    "681ea2f102d69c6ac50c7478": "JPI",
    "681eaad5ca75e9229d0aa8e0": "AEAS",
    "681ea9e8939646b8df09df67": "JPI"
}

# Extract brand based on form ID

def receive_and_publish(request):
    if request.method != "POST":
        return ("Only POST allowed", 405)

    data = request.get_json(force=True, silent=True)
    if not data:
        return ("Invalid JSON", 400)

    # Extract values from form data
    def extract_value(field_title):
        return next(
            (item.get("value") for item in data.get("data", [])
             if item.get("title") == field_title),
            None
        )

    name        = extract_value("Name")
    company     = extract_value("Company")
    event_name  = extract_value("INPUT: Event Name")
    event_date  = extract_value("INPUT: Event Date")
    form_id = data.get("form_id", "").strip()
    brand = FORM_ID_TO_BRAND.get(form_id, "UNKNOWN")
    email       = extract_value("Email")

    if not name or not form_id:
        return ("Missing name or form_id", 400)

    # Construct payload
    payload = json.dumps({
        "name": name,
        "brand": brand,
        "company": company,
        "event_name": event_name,
        "event_date": event_date,
        "email": email
    })

    try:
        publisher.publish(TOPIC_PATH, payload.encode("utf-8"))
    except Exception as e:
        print("🔴 Pub/Sub publish failed:", e)
        return (f"Publish error: {e}", 500)

    return ("Accepted", 202)
