# app.py

import os
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv

# Load local .env when running locally
load_dotenv()

app = Flask(__name__)

# --- Airtable setup ---
AIRTABLE_API_KEY = os.environ["AIRTABLE_API_KEY"]
BASE_ID          = os.environ["BASE_ID"]
TABLE_ID         = os.environ["TABLE_ID"]
VIEW_ID          = os.environ["VIEW_ID"]

AIRTABLE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"

HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

@app.route("/artists", methods=["GET"])
def get_artists():
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

@app.route("/artists/update", methods=["PATCH"])
def update_artist():
    payload = request.json
    artist_name = payload.get("artist")

    if not artist_name:
        return jsonify({"error": "Missing artist name"}), 400

    formula = f"{{Artist}}='{artist_name}'"
    search_resp = requests.get(
        AIRTABLE_URL,
        headers=HEADERS,
        params={"filterByFormula": formula}
    )

    if search_resp.status_code != 200:
        return jsonify({"error": "Error fetching artist"}), search_resp.status_code

    records = search_resp.json().get("records", [])
    if not records:
        return jsonify({"error": "Artist not found"}), 404

    record_id = records[0]["id"]

    editable_fields = {
        "Instagram": payload.get("instagram"),
        "Twitter (X)": payload.get("twitter"),
        "Facebook": payload.get("facebook"),
        "Soundcloud": payload.get("soundcloud"),
        "Bandcamp": payload.get("bandcamp"),
        "Artist Website": payload.get("artistWebsite"),
        "MusicBrainz URL": payload.get("musicbrainzUrl"),
        "Deezer": payload.get("deezer"),
        "Apple Music": payload.get("appleMusic")
    }

    update_fields = {k: v for k, v in editable_fields.items() if v is not None}

    patch_resp = requests.patch(
        f"{AIRTABLE_URL}/{record_id}",
        headers=HEADERS,
        json={"fields": update_fields}
    )

    if patch_resp.status_code != 200:
        return jsonify({"error": patch_resp.text}), patch_resp.status_code

    return jsonify({"success": True, "updatedFields": update_fields})

@app.route("/", methods=["GET"])
def index():
    return "Surefire Artist API is running."

# --- Instagram Graph API ---
IG_USER_ID      = os.getenv("IG_USER_ID")
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
BASE_URL        = "https://graph.facebook.com/v17.0"

def ig_get(path, params=None):
    params = params or {}
    params["access_token"] = IG_ACCESS_TOKEN
    resp = requests.get(f"{BASE_URL}/{path}", params=params)
    resp.raise_for_status()
    return resp.json()

@app.route("/api/instagram/account_insights")
def account_insights():
    start = request.args.get("start_date")
    end   = request.args.get("end_date")
    metrics = "impressions,reach,profile_views,website_clicks"
    data = ig_get(f"{IG_USER_ID}/insights", {
        "metric": metrics,
        "since":  start,
        "until":  end
    })
    return jsonify(data)

@app.route("/api/instagram/post_metrics", methods=["POST"])
def post_metrics():
    post_ids = request.json.get("post_ids", [])
    out = {}
    for pid in post_ids:
        out[pid] = ig_get(pid, {
            "fields": "reach,impressions,engagements,save_count,comments_count,share_count"
        })
    return jsonify(out)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
