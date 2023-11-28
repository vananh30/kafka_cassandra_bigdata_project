from sseclient import SSEClient as EventSource
import time
import json
from datetime import datetime, timedelta
# consume websocket
url = 'https://stream.wikimedia.org/v2/stream/recentchange'

print('Messages are being published to Kafka topic')
messages_count = 0

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

for event in EventSource(url):
    if event.event == 'message':
        try:
            event_data = json.loads(event.data)
        except ValueError:
            pass
        else:

            extracted_fields = extract_fields_from_json_string(event_data)
            print(extracted_fields)
            messages_count += 1
            time.sleep(5)


            
# {'id': 1698333354, 'type': 'categorize', 'title': 'Category:Noindexed pages', 'timestamp': '2023-11-27 00:06:24', 'user': 'AirportExpert', 'bot': False, 'length_old': None, 'length_new': None, 'revision_old': None, 'revision_new': None}