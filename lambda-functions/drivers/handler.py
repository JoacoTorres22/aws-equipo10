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
            f"https://api.openf1.org/v1/drivers?session_key={session_key}"
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return {
            "statusCode": 502,
            "body": json.dumps({"error": f"OpenF1 API call failed: {str(e)}"}),
        }

    drivers = response.json()

    if not drivers:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "No drivers found for the given session key"}),
        }

    drivers_list = [
        {
            "driver_number": driver.get("driver_number"),
            "full_name": driver.get("full_name"),
            "team_name": driver.get("team_name"),
            "country_code": driver.get("country_code"),
        }
        for driver in drivers
    ]

    return {
        "statusCode": 200,
        "body": json.dumps({
            "session_key": int(session_key),
            "driver_count": len(drivers_list),
            "drivers": drivers_list,
        }),
    }
