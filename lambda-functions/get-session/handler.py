import json
import os

import requests

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def handler(event, context):
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        session_key = config.get("session_key")
    except (FileNotFoundError, json.JSONDecodeError):
        session_key = None

    if not session_key:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "session_key not found in config.json"}),
        }

    try:
        response = requests.get(
            f"https://api.openf1.org/v1/sessions?session_key={session_key}"
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return {
            "statusCode": 502,
            "body": json.dumps({"error": f"OpenF1 API call failed: {str(e)}"}),
        }

    sessions = response.json()

    if not sessions:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "No session found for the given session key"}),
        }

    session = sessions[0]

    return {
        "statusCode": 200,
        "body": json.dumps({
            "session_key": int(session_key),
            "session_name": session.get("session_name"),
            "session_type": session.get("session_type"),
            "date_start": session.get("date_start"),
            "date_end": session.get("date_end"),
            "country_name": session.get("country_name"),
            "circuit_short_name": session.get("circuit_short_name"),
            "year": session.get("year"),
        }),
    }
