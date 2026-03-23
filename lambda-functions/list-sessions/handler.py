import json
import os

import requests

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def handler(event, context):
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        year = config.get("year")
    except (FileNotFoundError, json.JSONDecodeError):
        year = None

    if not year:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "year not found in config.json"}),
        }

    try:
        response = requests.get(
            f"https://api.openf1.org/v1/sessions?year={year}"
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
            "body": json.dumps({"error": "No sessions found for the given year"}),
        }

    sessions_list = [
        {
            "session_key": session.get("session_key"),
            "session_name": session.get("session_name"),
            "session_type": session.get("session_type"),
            "date_start": session.get("date_start"),
            "country_name": session.get("country_name"),
            "circuit_short_name": session.get("circuit_short_name"),
        }
        for session in sessions
    ]

    return {
        "statusCode": 200,
        "body": json.dumps({
            "year": int(year),
            "session_count": len(sessions_list),
            "sessions": sessions_list,
        }),
    }
