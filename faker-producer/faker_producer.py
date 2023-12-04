"""Produce openweathermap content to 'faker' kafka topic."""
import os
import time
from kafka import KafkaProducer
from faker import Faker
import json

fake = Faker()

def get_registered_user():
    return {
        "name": fake.name(),
        "gender":  fake.random_element(["Male", "Female", "Other"]),
        "address": fake.address(),
        "year": fake.year(),
        "email": fake.email(),
        "phone_number": fake.phone_number(),
        "job": fake.job(),
        "company": fake.company(),
        "country": fake.country(),
        "city": fake.city(),
        "date_time": fake.date_time().strftime('%Y-%m-%d %H:%M:%S'),
        "credit_card_number": fake.credit_card_number(),
    }

KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 5))

def run():
    iterator = 0
    print("Setting up faker producer at {}".format(KAFKA_BROKER_URL))
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER_URL],
        # Encode all values as JSON
        value_serializer=lambda x: json.dumps(x).encode("utf-8"),
    )

    while True:
        # adding prints for debugging in logs
        print("Sending new faker data iteration - {}".format(iterator))
        registered_user = get_registered_user()
        print(registered_user)
        producer.send(TOPIC_NAME, value=registered_user)
        print("New faker data sent")
        time.sleep(SLEEP_TIME)
        print("Waking up!")
        iterator += 1

if __name__ == "__main__":
    run()
