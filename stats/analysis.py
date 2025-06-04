"""Data analysis utilities for PyCon Italia statistics."""

import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

# Import colors and country data
from countries import COUNTRIES

from stats import colors


def load_pretix_data(event_id: str) -> dict[str, Any]:
    """Load orders and items data from Pretix JSON files."""
    orders_path = Path(f"{event_id}.json")

    if not orders_path.exists():
        error_message = "Pretix data files not found. Please run pretix.py to download the data first."
        raise FileNotFoundError(error_message)

    return json.loads(orders_path.read_text())


def extract_attendee_data(orders: list[dict[str, Any]]) -> pd.DataFrame:
    """Extract attendee data from Pretix orders."""
    # Create a list to hold all attendee data
    attendees_data = []

    for order in orders:
        # Only paid orders
        if order["status"] != "p":
            continue

        country = order["invoice_address"]["country"]

        for position in order["positions"]:
            # Get gender information
            gender = next(
                (a["answer"] for a in position["answers"] if a["question"] == 76), "--",
            )

            attendee = {
                "order_code": order["code"],
                "status": order["status"],
                "country": country,
                "item": position["item"],
                "gender": gender,
                "continent": COUNTRIES.get(country, {}).get("continent_name", "Unknown"),
            }

            attendees_data.append(attendee)

    return pd.DataFrame(attendees_data)


def plot_attendees_by_country(df: pd.DataFrame, top_n: int = 10) -> None:
    """Plot the top N countries by number of attendees."""
    country_counts = df["country"].value_counts().head(top_n)
    countries = country_counts.index
    counts = country_counts.values
    country_names = [
        COUNTRIES.get(country, {}).get("name", country) for country in countries
    ]

    plt.figure(figsize=(12, 8))
    colors_list = [
        colors.DARK_BLUE,
        colors.GREEN,
        colors.PURPLE,
        colors.CORAL,
        colors.YELLOW,
        colors.GREEN_4,
        colors.BLUE,
        colors.PINK,
        colors.RED,
        colors.NEUTRAL_BLUE,
    ]

    bars = plt.bar(country_names, counts, color=colors_list[: len(country_names)])
    plt.title("Top Countries by Attendees")
    plt.xlabel("Country")
    plt.ylabel("Number of Attendees")
    plt.xticks(ha="center")

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.annotate(
            f"{height}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
        )

    plt.tight_layout()
    output_path = Path("plots/pycon_2024_top_10_countries.png")
    plt.savefig(output_path, bbox_inches="tight")
    plt.show()

    print(f"Plot saved to {output_path}")


def plot_italian_vs_non_italian(df: pd.DataFrame) -> None:
    """Plot Italian vs Non-Italian attendee distribution."""
    italian_non_italian = (
        df["country"].apply(lambda x: "IT" if x == "IT" else "Non-IT").value_counts()
    )

    plt.figure(figsize=(8, 6))
    plt.pie(
        italian_non_italian.values,
        labels=italian_non_italian.index,
        autopct="%1.1f%%",
        colors=[GREEN, CORAL],
    )
    plt.title("Italian vs Non-Italian Attendees")

    output_path = Path("plots/pycon_2024_italian_vs_non_italian.png")
    plt.savefig(output_path, bbox_inches="tight")
    plt.show()

    print(f"Plot saved to {output_path}")


def plot_europe_vs_non_europe(df: pd.DataFrame) -> None:
    """Plot European vs non-European attendee distribution."""
    europe_counts = (
        df["continent"]
        .apply(lambda x: "Europe" if x == "Europe" else "Non-Europe")
        .value_counts()
    )

    plt.figure(figsize=(8, 6))
    plt.pie(
        europe_counts.values,
        labels=europe_counts.index,
        autopct="%1.1f%%",
        colors=[DARK_BLUE, CORAL],
    )
    plt.title("Europe vs Non-Europe Attendees")

    output_path = Path("plots/pycon_2024_europe_vs_non_europe.png")
    plt.savefig(output_path, bbox_inches="tight")
    plt.show()

    print(f"Plot saved to {output_path}")


def plot_gender_diversity(df: pd.DataFrame) -> None:
    """Plot gender diversity of attendees."""

    # Categorize genders
    def categorize_gender(g):
        if g in ["he/him", "she/her", "--"]:
            return g
        return "Other"

    gender_stats = df["gender"].apply(categorize_gender).value_counts()

    # Bar chart
    plt.figure(figsize=(10, 6))
    bars = plt.bar(
        gender_stats.index, gender_stats.values, color=[BLUE, PINK, GRAY_250, GREEN_4],
    )
    plt.title("Gender Diversity")
    plt.xlabel("Gender")
    plt.ylabel("Number of Attendees")
    plt.xticks(ha="center")

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.annotate(
            f"{height}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
        )

    plt.tight_layout()
    output_path = Path("plots/pycon_2024_gender_diversity_bar.png")
    plt.savefig(output_path, bbox_inches="tight")
    plt.show()

    print(f"Bar chart saved to {output_path}")

    # Pie chart
    plt.figure(figsize=(8, 6))
    plt.pie(
        gender_stats.values,
        labels=gender_stats.index,
        autopct="%1.1f%%",
        colors=[colors.BLUE, colors.PINK, colors.GRAY_250, colors.GREEN_4],
    )
    plt.title("Gender Diversity")

    output_path = Path("plots/pycon_2024_gender_diversity_pie.png")
    plt.savefig(output_path, bbox_inches="tight")
    plt.show()

    print(f"Pie chart saved to {output_path}")
