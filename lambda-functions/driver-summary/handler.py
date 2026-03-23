import json
import os

import requests

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def handler(event, context):
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        driver_number = config.get("driver_number")
        session_key = config.get("session_key")
    except (FileNotFoundError, json.JSONDecodeError):
        driver_number = None
        session_key = None

    if not driver_number or not session_key:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "driver_number and session_key are required in config.json"}),
        }

    try:
        driver_resp = requests.get(
            f"https://api.openf1.org/v1/drivers?driver_number={driver_number}&session_key={session_key}"
        )
        driver_resp.raise_for_status()

        laps_resp = requests.get(
            f"https://api.openf1.org/v1/laps?driver_number={driver_number}&session_key={session_key}"
        )
        laps_resp.raise_for_status()

        position_resp = requests.get(
            f"https://api.openf1.org/v1/position?driver_number={driver_number}&session_key={session_key}"
        )
        position_resp.raise_for_status()

    except requests.RequestException as e:
        return {
            "statusCode": 502,
            "body": json.dumps({"error": f"OpenF1 API call failed: {str(e)}"}),
        }

    drivers = driver_resp.json()
    if not drivers:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "Driver not found for the given driver_number and session_key"}),
        }

    driver = drivers[0]
    laps = laps_resp.json()
    positions = position_resp.json()

    valid_laps = [lap for lap in laps if lap.get("lap_duration") is not None]
    fastest_lap = min(valid_laps, key=lambda x: x["lap_duration"]) if valid_laps else None
    last_position = positions[-1].get("position") if positions else None

    return {
        "statusCode": 200,
        "body": json.dumps({
            "driver_number": int(driver_number),
            "full_name": driver.get("full_name"),
            "team_name": driver.get("team_name"),
            "country_code": driver.get("country_code"),
            "session_key": int(session_key),
            "total_laps": len(laps),
            "fastest_lap_duration": fastest_lap.get("lap_duration") if fastest_lap else None,
            "fastest_lap_number": fastest_lap.get("lap_number") if fastest_lap else None,
            "final_position": last_position,
        }),
    }
