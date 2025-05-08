from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

AIRTABLE_API_KEY = os.environ["AIRTABLE_API_KEY"]
BASE_ID = os.environ["BASE_ID"]
TABLE_NAME = os.environ.get("TABLE_NAME", "Active Artists")

AIRTABLE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"

HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

@app.route("/artists", methods=["GET"])
def get_artists():
    params = {
        "view": "SOCIALS"  # Assuming you're syncing from that view
    }
    response = requests.get(AIRTABLE_URL, headers=HEADERS, params=params)

    if response.status_code != 200:
        return jsonify({"error": response.text}), response.status_code

    records = response.json().get("records", [])
    result = []
    for rec in records:
        fields = rec.get("fields", {})
        result.append({
            "artist": fields.get("Artist"),
            "instagram": fields.get("Instagram"),
            "twitter": fields.get("Twitter (X)"),
            "agent": fields.get("Responsible Agent (RA)"),
            "representation": fields.get("Representation"),
            "website": fields.get("Artist Website")
        })
    return jsonify(result)

@app.route("/")
def index():
    return "Surefire Artist API is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)