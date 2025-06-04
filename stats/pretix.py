import json
import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin

import requests
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Configuration for Pretix API access."""

    api_url: str
    event_id: str
    organizer_id: str
    api_token: str

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls(
            api_url=os.getenv("PRETIX_API_URL", ""),
            event_id=os.getenv("PRETIX_EVENT_ID", ""),
            organizer_id=os.getenv("PRETIX_ORGANIZER_ID", ""),
            api_token=os.getenv("PRETIX_API_TOKEN", ""),
        )


config = Config.from_env()


def get_api_url(endpoint: str) -> str:
    """Generate a Pretix API URL for the given endpoint."""
    return urljoin(
        config.api_url,
        f"organizers/{config.organizer_id}/events/{config.event_id}/{endpoint}",
    )


def request(url: str) -> requests.Response:
    """Make a request to the Pretix API."""
    headers = {
        "Authorization": f"Token {config.api_token}",
        "Content-Type": "application/pdf",
        "Cache-Control": "no-cache",
    }

    response = requests.get(url, headers=headers, timeout=10)

    response.raise_for_status()

    return response


def get_orders(config: Config) -> None:
    """Fetch and save all orders from the Pretix API."""
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
        
        Path(f"{config.event_id}.json").write_text(json.dumps(orders))

    except requests.HTTPError as e:
        print("Can't get ticket info...", e.response, e.response.reason)
        data = e.response.json()
        print(data)


def get_items(config: Config):
    """Fetch and save all items from the Pretix API."""
    # GET /api/v1/organizers/(organizer)/events/(event)/items/

    url = get_api_url("items/")
    try:
        response = request(url)
        data = response.json()
        Path(f"{config.event_id}_items.json").write_text(json.dumps(data))

    except requests.HTTPError as e:
        print("Can't get ticket info...", e.response, e.response.reason)
        data = e.response.json()
        print(data)


def main() -> None:
    """Main function to execute the Pretix data fetching."""
    config = Config.from_env()

    # Uncomment to fetch orders
    get_orders(config)

    # Fetch items
    # get_items(config)


if __name__ == "__main__":
    main()
