from sseclient import SSEClient as EventSource
import time
import json
from datetime import datetime, timedelta
import os
from kafka import KafkaProducer

KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 5))


def extract_fields_from_json_string(event_json):
    """
    Extracts specific fields from a Wikimedia Recent Change event JSON string.

    Args:
    - event_string (str): A string representing the JSON structure of the event.

    Returns:
    - dict: A dictionary containing the extracted fields.
    """
    try:
        # Extract specific fields
        extracted_fields = {
            "id": event_json.get("id"),
            "type": event_json.get("type"),
            "title": event_json.get("title"),
            "timestamp":  (datetime.utcfromtimestamp(event_json.get("timestamp")) + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S'),
            "user": event_json.get("user"),
            "bot": event_json.get("bot"),
            "length_old": event_json.get("length", {}).get("old"),
            "length_new": event_json.get("length", {}).get("new"),
            "revision_old": event_json.get("revision", {}).get("old"),
            "revision_new": event_json.get("revision", {}).get("new"),
        }

        return extracted_fields
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return {}



def run():
    iterator = 0
    print("Setting up wikipedia producer at {}".format(KAFKA_BROKER_URL))
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER_URL],
        # Encode all values as JSON
        value_serializer=lambda x: json.dumps(x).encode("utf-8"),
    )

    url = 'https://stream.wikimedia.org/v2/stream/recentchange'
    for event in EventSource(url):
        if event.event == 'message':
            try:
                event_data = json.loads(event.data)
            except ValueError:
                pass
            else:
                print("Sending new wikepedia data iteration - {}".format(iterator))
                extracted_fields = extract_fields_from_json_string(event_data)
                print(extracted_fields)
                producer.send(TOPIC_NAME, value=extracted_fields)
                print("New faker data sent")
                time.sleep(SLEEP_TIME)
                print("Waking up!")
                iterator += 1


if __name__ == "__main__":
    run()

