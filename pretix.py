from dataclasses import dataclass
import os
from urllib.parse import urljoin
from dotenv import load_dotenv
import requests
import json
from pathlib import Path

load_dotenv()


@dataclass
class Config:
    PRETIX_API_URL: str
    PRETIX_EVENT_ID: str
    PRETIX_ORGANIZER_ID: str
    PRETIX_API_TOKEN: str

    @classmethod
    def from_env(cls):
        return cls(
            PRETIX_API_URL=os.getenv("PRETIX_API_URL", ""),
            PRETIX_EVENT_ID=os.getenv("PRETIX_EVENT_ID", ""),
            PRETIX_ORGANIZER_ID=os.getenv("PRETIX_ORGANIZER_ID", ""),
            PRETIX_API_TOKEN=os.getenv("PRETIX_API_TOKEN", ""),
        )


config = Config.from_env()


def get_api_url(endpoint: str) -> str:
    return urljoin(
        config.PRETIX_API_URL,
        f"organizers/{config.PRETIX_ORGANIZER_ID}/events/{config.PRETIX_EVENT_ID}/{endpoint}",
    )


def request(url: str):
    headers = {
        "Authorization": f"Token {config.PRETIX_API_TOKEN}",
        "Content-Type": "application/pdf",
        "Cache-Control": "no-cache",
    }

    response = requests.get(url, headers=headers)

    response.raise_for_status()

    return response


def get_orders():
    # GET /api/v1/organizers/bigevents/events/sampleconf/orders/
    url = get_api_url("orders/")
    orders = []
    try:
        response = request(url)
        data = response.json()
        orders.extend(data["results"])

        next = data.get("next")
        index = 2
        while next:
            response = request(next)
            data = response.json()
            orders.extend(data["results"])
            next = data.get("next")
            index += 1

        Path(f"{config.PRETIX_EVENT_ID}.json").write_text(json.dumps(orders))

    except requests.HTTPError as e:
        print("Can't get ticket info...", e.response, e.response.reason)
        data = e.response.json()
        print(data)


def get_items():
    # GET /api/v1/organizers/(organizer)/events/(event)/items/

    url = get_api_url("items/")
    try:
        response = request(url)
        data = response.json()
        Path(f"{config.PRETIX_EVENT_ID}_items.json").write_text(json.dumps(data))

    except requests.HTTPError as e:
        print("Can't get ticket info...", e.response, e.response.reason)
        data = e.response.json()
        print(data)


# get_orders()
get_items()
