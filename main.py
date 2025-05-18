from flask import Flask, request, jsonify
import os
import json
import base64
import requests
from google.cloud import pubsub_v1
import functions_framework

# ─── CONFIG ───
PROJECT_ID    = "avian-cosmos-458703-g3"
TOPIC_ID      = "enquiry-form-submissions"

publisher  = pubsub_v1.PublisherClient()
TOPIC_PATH = publisher.topic_path(PROJECT_ID, TOPIC_ID)

# ─── FORM ID TO BRAND MAPPING ───
FORM_ID_TO_BRAND = {
    "681ea1dd75c61440f40537c0": "ECE",
    "681e9dc9d9b9d5e9e10682e6": "TPRA",
    "681ea2f102d69c6ac50c7478": "JPI",
    "681eaad5ca75e9229d0aa8e0": "AEAS",
    "681ea9e8939646b8df09df67": "JPI"
}

# @app.route("/", methods=["POST"])
@functions_framework.http
def receive_and_publish(request):
    if request.method != "POST":
        return ("Only POST allowed", 405)

    data = request.get_json(force=True, silent=True)
    if not data:
        return ("Invalid JSON", 400)

    def extract_value(field_title):
        return next(
            (item.get("value") for item in data.get("data", [])
             if item.get("type") == field_title),
            None
        )

    email       = extract_value("email")

    if not email:
        return ("Missing email", 400)

    payload = json.dumps({
        "email": email
    })

    try:
        publisher.publish(TOPIC_PATH, payload.encode("utf-8"))
    except Exception as e:
        print("🔴 Pub/Sub publish failed:", e)
        return (f"Publish error: {e}", 500)

    return ("Accepted", 202)
