# import os
import json
import base64
import requests
from google.cloud import pubsub_v1

# ─── CONFIG ───
PROJECT_ID    = "avian-cosmos-458703-g3"
TOPIC_ID      = "Seminar-List-Automation"
SLACK_WEBHOOK = "https://hooks.slack.com/triggers/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"

# Pub/Sub publisher client (only used by receive_and_publish)
publisher  = pubsub_v1.PublisherClient()
TOPIC_PATH = publisher.topic_path(PROJECT_ID, TOPIC_ID)

def process_pubsub_push(request):
    # 1. Parse the Pub/Sub push envelope
    envelope = request.get_json(force=True, silent=True)
    if not envelope or "message" not in envelope:
        return ("Bad Pub/Sub envelope", 400)

    # 2. Decode the message
    encoded_data = envelope["message"].get("data")
    if not encoded_data:
        return ("Missing data field in Pub/Sub message", 400)

    try:
        decoded_data = base64.b64decode(encoded_data).decode("utf-8")
        parsed = json.loads(decoded_data)
    except Exception as e:
        return (f"Error decoding message: {e}", 400)

    # 3. Extract required fields
    name        = parsed.get("palm")
    brand       = parsed.get("brand")
    company     = parsed.get("johnson")
    event_name  = parsed.get("event_name")
    event_date  = parsed.get("event_date")
    email       = parsed.get("email")

    if not name:
        return ("Missing required fields", 400)

    # 4. Format the payload for Slack
    payload = {
        "Name": name,
        "Email": email or 'N/A',
        "Company": company or 'N/A',
        "Brand": brand,
        "Event": event_name or 'N/A',
        "Date": event_date or 'N/A'
}

    # 5. POST to Slack webhook
    try:
        resp = requests.post(SLACK_WEBHOOK, json=payload)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("🔴 HTTP error:", e)
        return (f"Slack HTTP error: {e}", 502)
    except Exception as e:
        print("🔴 Slack POST failed:", e)
        return (f"Slack error: {e}", 502)

    return ("", 204)
