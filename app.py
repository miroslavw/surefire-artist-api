from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

# Environment variables
AIRTABLE_API_KEY = os.environ["AIRTABLE_API_KEY"]
BASE_ID          = os.environ["BASE_ID"]
TABLE_ID         = os.environ["TABLE_ID"]
VIEW_ID          = os.environ["VIEW_ID"]   # Use View ID instead of name

# Airtable endpoint
AIRTABLE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"

HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

@app.route("/artists", methods=["GET"])
def get_artists():
    # Query the specific view by ID
    resp = requests.get(
        AIRTABLE_URL,
        headers=HEADERS,
        params={"view": VIEW_ID}
    )

    if resp.status_code != 200:
        return jsonify({"error": resp.text}), resp.status_code

    data = []
    for record in resp.json().get("records", []):
        fields = record.get("fields", {})
        data.append({
            "artist":         fields.get("Artist"),
            "instagram":      fields.get("Instagram"),
            "twitter":        fields.get("Twitter (X)"),
            "agent":          fields.get("Responsible Agent (RA)"),
            "representation": fields.get("Representation"),
            "website":        fields.get("Artist Website")
        })

    return jsonify(data)

@app.route("/", methods=["GET"])
def index():
    return "Surefire Artist API is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
