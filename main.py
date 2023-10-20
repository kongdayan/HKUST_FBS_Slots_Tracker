# -*- coding: UTF-8 -*-
from datetime import datetime, timedelta, time
import json
import requests
from config import location, data_config, notify_config, time_filter
from dotenv import dotenv_values
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

config = dotenv_values(".env")

platforms = config["PLATFORMS"].split(",")

if "alumni" in platforms:
    alumni_header = {
        "User-Agent": config["ALUMNI_USER_AGENT"],
        "Authorization": config["ALUMNI_AUTHORIZATION"],
    }


def configure_notifications():
    """
    Configure push notifications channels and tokens.
    """
    push_channels = config["PUSH_CHANNEL"].split(",")
    tokens = {}

    for channel in push_channels:
        if channel == "pushdeer":
            tokens["pushdeer"] = config["PUSHDEER_TOKEN"].split(",")
        elif channel == "larkbot":
            tokens["larkbot"] = config["LARKBOT_TOKEN"]
        elif channel == "feishubot":
            tokens["feishubot"] = config["FEISHUBOT_TOKEN"]
        else:
            logging.warning(f"Unsupported push channel: {channel}")

    return push_channels, tokens


push_channels, notification_tokens = configure_notifications()
pushdeer_user_tokens = notification_tokens.get("pushdeer", [])
larkbot_token = notification_tokens.get("larkbot")
feishubot_token = notification_tokens.get("feishubot")


today = datetime.today()
start_date = datetime.strftime(today, "%Y-%m-%d")
end_date = datetime.strftime(today + timedelta(days=7), "%Y-%m-%d")
START_TIME_OBJ = time(hour=time_filter["START"], minute=0)
END_TIME_OBJ = time(hour=time_filter["END"], minute=0)


def fetch_data(daterange):
    """
    Fetch data from the API and parse it to extract available slots.

    Args:
        daterange (dict): Contains the start and end date for fetching data.

    Returns:
        List: Contains the available slots in the specified time range.
    """
    ava_slots = []

    for code, string in location.items():
        try:
            response = requests.get(
                data_config["alumni"]["FETCH_URL"].format(
                    id=code, startdate=daterange["S"], enddate=daterange["E"]
                ),
                headers=alumni_header,
                timeout=5,
            )
            response.raise_for_status()  # raises exception when not a 2xx response

            res = response.json()

            if res["meta"]["code"] == 200:
                ava_slots.extend(
                    parse_available_slots(res["data"]["facility_timeslots"], string)
                )
            else:
                # handle API expiration or other API issues
                # print(res)
                # send_mantain_notify()
                break

        except requests.RequestException as e:
            # Handle the error accordingly. For now, just print the error
            print(f"Error fetching data for code {code}: {e}")
            mainten_notify()

    return ava_slots


def parse_available_slots(data, location_string):
    """
    Parse the slots to get the available ones within the specified time range.

    Args:
        data (list): List of slots from the API.
        location_string (str): Location string for the slots.

    Returns:
        List: Contains the available slots in the specified time range.
    """
    slots = []

    for i in data:
        if i["status"] == "Available":
            time_obj = datetime.strptime(i["start_time"], "%H:%M").time()
            if START_TIME_OBJ <= time_obj <= END_TIME_OBJ:
                datetime_obj = datetime.strptime(
                    i["date"] + " " + i["start_time"], "%Y-%m-%d %H:%M"
                )
                formatted_datetime = datetime_obj.strftime("%m月%d日%H时")
                booking_data = formatted_datetime + location_string
                slots.append(booking_data)

    return slots


def _push_to_pushdeer(_content):
    """
    Send notification to Pushdeer users.

    Args:
    - _content (str): The content of the notification to be sent.

    Note:
    This function will send the notification to all tokens in the pushdeer_user_tokens list.
    """
    for token in pushdeer_user_tokens:
        notify_url = notify_config["pushdeer"]["BASE_URL"].format(
            token=token, text=("[抢场地]" + str(_content))
        )
        try:
            requests.get(notify_url, timeout=2)
        except requests.RequestException:
            print(f"Error sending notification with pushdeer using token {token}")


def _push_to_feishubot(_content):
    """
    Send notification to Feishubot users.

    Args:
    - _content (str): The content of the notification to be sent.
    """
    notify_url = notify_config["feishubot"]["BASE_URL"].format(token=feishubot_token)
    payload = {"msg_type": "text", "content": {"text": f"[捡球场]{_content}"}}
    body = json.dumps(payload)
    try:
        requests.post(notify_url, data=body, timeout=2)
    except requests.RequestException:
        print("Error sending notification with feishubot")


def _push_to_larkbot(_content):
    """
    Send notification to Larkbot users.

    Args:
    - _content (str): The content of the notification to be sent.
    """
    notify_url = notify_config["larkbot"]["BASE_URL"].format(token=larkbot_token)
    payload = {"msg_type": "text", "content": {"text": f"[捡球场]{_content}"}}
    body = json.dumps(payload)
    try:
        requests.post(notify_url, data=body, timeout=2)
    except requests.RequestException:
        print("Error sending notification with larkbot")


def push_notify(content):
    """
    Send notifications based on the specified channels.

    Args:
    - content (str): The content of the notification to be sent to each channel.

    Note:
    This function will determine which channels to use based on the push_channels list and then call
    the corresponding notification function for each channel.
    """
    notify_mapping = {
        "pushdeer": _push_to_pushdeer,
        "feishubot": _push_to_feishubot,
        "larkbot": _push_to_larkbot,
    }
    for way in push_channels:
        notify_func = notify_mapping.get(way)
        if notify_func:
            notify_func(content)


def mainten_notify():
    """
    Send a maintenance notification to Pushdeer when the AUTHORIZATION expires.
    """
    try:
        notify_url = notify_config["pushdeer"]["BASE_URL"].format(
            token=config["PUSHDEER_MAINTAIN_TOKEN"], text="[抢场地]AUTHORIZATION过期了"
        )
        r = requests.get(notify_url, timeout=2)

        # Check if the request was successful
        if r.status_code == 200:
            logging.info("Maintenance notification sent successfully.")
        else:
            logging.warning(
                f"Failed to send maintenance notification. Status code: {r.status_code}"
            )
    except requests.RequestException as e:
        logging.error(f"Error sending maintenance notification: {e}")


if __name__ == "__main__":
    logging.info("Starting the data fetching process.")
    available_slots = fetch_data({"S": start_date, "E": end_date})
    logging.info(f"Available slots: {available_slots}")
    push_notify(available_slots)
