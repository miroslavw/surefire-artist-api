from flask import Flask, jsonify
import requests, os

app = Flask(__name__)

AIRTABLE_API_KEY = os.environ["AIRTABLE_API_KEY"]
BASE_ID           = os.environ["BASE_ID"]
TABLE_ID          = os.environ["TABLE_ID"]
VIEW_NAME         = os.environ.get("VIEW_NAME", "SOCIALS")
URL               = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"
HEADERS           = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

@app.route("/artists", methods=["GET"])
def get_artists():
    resp = requests.get(URL, headers=HEADERS, params={"view": VIEW_NAME})
    if resp.status_code != 200:
        return jsonify({"error": resp.text}), resp.status_code

    data = []
    for r in resp.json().get("records", []):
        f = r.get("fields", {})
        data.append({
            "artist":         f.get("Artist"),
            "instagram":      f.get("Instagram"),
            "twitter":        f.get("Twitter (X)"),
            "agent":          f.get("Responsible Agent (RA)"),
            "representation": f.get("Representation"),
            "website":        f.get("Artist Website")
        })
    return jsonify(data)

@app.route("/")
def index():
    return "Surefire Artist API is running."