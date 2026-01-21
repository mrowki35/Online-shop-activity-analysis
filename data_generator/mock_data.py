import asyncio
import json
import os
import random
import uuid
from datetime import datetime, timezone

from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient
from dotenv import load_dotenv

load_dotenv()
CONNECTION_STR = os.getenv("EVENT_HUB_CONNECTION_STR")
EVENTHUB_NAME = os.getenv("EVENT_HUB_NAME")

EVENT_TYPES = [
    "PAGE_VIEW",
    "SEARCH",
    "PRODUCT_VIEW",
    "ADD_TO_CART",
    "REMOVE_FROM_CART",
    "VIEW_CART",
    "CHECKOUT_START",
    "ADD_SHIPPING_INFO",
    "ADD_PAYMENT_INFO",
    "PURCHASE",
]

PRODUCTS = [
    {
        "id": "PROD_001",
        "name": "Laptop Gamingowy",
        "price": 4500.00,
        "category": "Electronics",
    },
    {
        "id": "PROD_002",
        "name": "Mysz Bezprzewodowa",
        "price": 120.50,
        "category": "Accessories",
    },
    {
        "id": "PROD_003",
        "name": "Monitor 4K",
        "price": 1200.00,
        "category": "Electronics",
    },
    {
        "id": "PROD_004",
        "name": "Klawiatura Mechaniczna",
        "price": 350.00,
        "category": "Accessories",
    },
    {
        "id": "PROD_005",
        "name": "Słuchawki Noise Cancelling",
        "price": 800.00,
        "category": "Audio",
    },
]


class ClickstreamGenerator:
    def __init__(self):
        self.active_users = []

    def _get_or_create_user(self):
        if not self.active_users or random.random() < 0.3:
            new_user = {
                "userId": f"user_{random.randint(1000, 9999)}",
                "sessionId": str(uuid.uuid4()),
                "deviceType": random.choice(["Mobile", "Desktop", "Tablet"]),
                "os": random.choice(["Windows", "iOS", "Android", "MacOS"]),
            }
            if len(self.active_users) > 20:
                self.active_users.pop(0)
            self.active_users.append(new_user)
            return new_user
        else:
            return random.choice(self.active_users)

    def generate_event(self):
        user_context = self._get_or_create_user()

        rand_val = random.random()
        if rand_val < 0.4:
            event_type = "PAGE_VIEW"
        elif rand_val < 0.6:
            event_type = "PRODUCT_VIEW"
        elif rand_val < 0.7:
            event_type = "SEARCH"
        elif rand_val < 0.8:
            event_type = "ADD_TO_CART"
        elif rand_val < 0.95:
            event_type = random.choice(
                ["VIEW_CART", "CHECKOUT_START", "ADD_SHIPPING_INFO", "ADD_PAYMENT_INFO"]
            )
        else:
            event_type = "PURCHASE"

        product = (
            random.choice(PRODUCTS)
            if event_type not in ["PAGE_VIEW", "SEARCH"]
            else None
        )

        event_body = {
            "eventId": str(uuid.uuid4()),
            "eventType": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "userId": user_context["userId"],
            "sessionId": user_context["sessionId"],
            "device": {
                "type": user_context["deviceType"],
                "os": user_context["os"],
                "ip": f"192.168.{random.randint(0,255)}.{random.randint(0,255)}",
            },
            "pageUrl": f"https://shop.example.com/{event_type.lower().replace('_','-')}",
            "data": {},
        }
        if product:
            event_body["data"]["productId"] = product["id"]
            event_body["data"]["productName"] = product["name"]
            event_body["data"]["price"] = product["price"]
            event_body["data"]["currency"] = "PLN"

        if event_type == "SEARCH":
            event_body["data"]["searchQuery"] = random.choice(
                ["laptop", "mouse", "desktop", "cable"]
            )

        if event_type == "PURCHASE":
            event_body["data"]["orderId"] = f"ORD-{random.randint(10000, 99999)}"
            event_body["data"]["totalAmount"] = product["price"]

        return event_body


async def run():
    print(f"Start wysyłania zdarzeń do: {EVENTHUB_NAME}")
    producer = EventHubProducerClient.from_connection_string(
        conn_str=CONNECTION_STR, eventhub_name=EVENTHUB_NAME
    )

    generator = ClickstreamGenerator()

    async with producer:
        while True:
            event_data_batch = await producer.create_batch()

            for _ in range(random.randint(1, 5)):
                event_payload = generator.generate_event()

                event_json = json.dumps(event_payload)
                event_data_batch.add(EventData(event_json))

                print(
                    f"[{event_payload['timestamp']}] {event_payload['eventType']} - User: {event_payload['userId']}"
                )

            await producer.send_batch(event_data_batch)

            await asyncio.sleep(random.uniform(0.5, 2.0))


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("Zatrzymano.")
