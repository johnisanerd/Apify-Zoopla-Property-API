"""Zoopla UK Property API: a Python quick start for sold house prices and live UK listings.

Actor page:   https://apify.com/johnvc/zoopla-property-api?fpr=9n7kx3
Input schema: https://apify.com/johnvc/zoopla-property-api/input-schema?fpr=9n7kx3
Free Apify API key: https://apify.com?fpr=9n7kx3

The Actor searches UK property by town, city, borough, or postcode area, so you never
need to hold a listing URL. Every listing row carries the asking price, beds, baths,
tenure, agent, features, the UPRN, and a dated `listingHistory` that includes what the
property last sold for and when.

Recipes:
  uv run python zoopla-property-api-example.py                        # default search
  uv run python zoopla-property-api-example.py --example sold-prices  # sale history focus
  uv run python zoopla-property-api-example.py --example by-url \\
      --url https://www.zoopla.co.uk/for-sale/details/70012345/
"""

from __future__ import annotations

import argparse
import os
from typing import Any

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

ACTOR_ID = "johnvc/zoopla-property-api"

# Every run is billed per listing returned, so `maxResultsPerSearch` is the cost knob.
# All recipes below keep it at 3 with a single location, which makes a first run cost
# roughly a penny. Raise it once you have your own API key and know your budget.
CHEAP_RESULT_CAP = 3


def _fetch(client: ApifyClient, run_input: dict[str, Any]) -> list[dict[str, Any]]:
    """Run the Actor and return every row from its default dataset.

    Args:
        client: An authenticated Apify client.
        run_input: The Actor input, matching the published input schema.

    Returns:
        The dataset rows produced by the run.
    """
    run = client.actor(ACTOR_ID).call(run_input=run_input)
    if run is None:
        raise SystemExit("The Actor run did not return a result.")

    # apify-client 3.x returns a typed Run object, so read the attribute, not a dict key.
    print(f"Run {run.id} finished with status {run.status}.")
    return list(client.dataset(run.default_dataset_id).iterate_items())


def _price_events(row: dict[str, Any]) -> list[dict[str, Any]]:
    """Return only the real dated price events from a row's `listingHistory`.

    The raw history array also carries a few layout fragments from the source page,
    with no `date` and a price of zero. Keeping the entries that have a `date` leaves
    you with the Listed, Price reduced, and Sold events, which is what sold price
    research runs on.
    """
    return [
        event
        for event in (row.get("listingHistory") or [])
        if event.get("date") and event.get("priceValue")
    ]


def _print_listings(items: list[dict[str, Any]]) -> None:
    """Print the headline fields of each listing row, plus any error rows."""
    listings = [row for row in items if row.get("result_type") == "listing"]
    errors = [row for row in items if row.get("result_type") == "error"]
    print(f"Returned {len(listings)} listing(s) and {len(errors)} error row(s).\n")

    for row in listings:
        print(row.get("address", "unknown address"))
        print(f"  Type:      {row.get('propertyType')}")
        print(f"  Price:     {row.get('price')}  (numeric: {row.get('priceValue')} "
              f"{row.get('currency')})")
        print(
            f"  Rooms:     {row.get('bedrooms')} bed, "
            f"{row.get('bathrooms')} bath, {row.get('receptions')} reception"
        )
        # Tenure, floor area, and the agent phone are published on some listings only.
        for label, key in (("Tenure", "tenure"), ("Size", "propertySize"),
                           ("Deposit", "deposit")):
            if row.get(key):
                print(f"  {label}:{' ' * (10 - len(label))}{row.get(key)}")
        print(f"  UPRN:      {row.get('uprn')}")
        agent = " ".join(str(v) for v in (row.get("agentName"), row.get("agentPhone")) if v)
        print(f"  Agent:     {agent}")
        if row.get("lastSoldPrice"):
            print(f"  Last sold: {row.get('lastSoldPrice')} on {row.get('lastSoldDate')}")
        else:
            print("  Last sold: no recorded sale on this property")
        features = row.get("features") or []
        if features:
            print(f"  Features:  {', '.join(str(f) for f in features[:4])}")
        print(f"  Listing:   {row.get('listingUrl')}")
        print()

    for row in errors:
        print(f"Error row: {row.get('error_type')}: {row.get('error_message')}")


def _print_sold_history(items: list[dict[str, Any]]) -> None:
    """Print the dated sale history of each listing, the sold house prices view."""
    listings = [row for row in items if row.get("result_type") == "listing"]
    print(f"Sale history for {len(listings)} propert(ies).\n")

    for row in listings:
        print(f"{row.get('address')}  (UPRN {row.get('uprn')})")
        if row.get("lastSoldPrice"):
            print(
                f"  Last sold: {row.get('lastSoldPrice')} on {row.get('lastSoldDate')} "
                f"(numeric: {row.get('lastSoldValue')})"
            )
        else:
            print("  Last sold: no recorded sale on this property")
        for event in _price_events(row):
            print(
                f"    {event.get('date')}: {event.get('event')} "
                f"{event.get('price')} (numeric: {event.get('priceValue')})"
            )
        print(f"  Listing: {row.get('listingUrl')}")
        print()


def run_default(client: ApifyClient, args: argparse.Namespace) -> None:
    """Cheap general quick start: three for-sale listings in one town."""
    run_input: dict[str, Any] = {
        "mode": "search",
        "locations": ["Rochdale"],
        "propertyType": "For sale",
        "maxResultsPerSearch": CHEAP_RESULT_CAP,
    }
    _print_listings(_fetch(client, run_input))


def run_sold_prices(client: ApifyClient, args: argparse.Namespace) -> None:
    """Sold house prices recipe: search a postcode area and read each sale history.

    Uses the same search input as the default run, then prints `listingHistory`
    instead of the asking-price summary. Every `Sold` event carries the date and the
    price as published, plus a parsed numeric value you can sort on. The `uprn` field
    is the join key for Land Registry and council datasets.
    """
    run_input: dict[str, Any] = {
        "mode": "search",
        "locations": ["OL11"],
        "propertyType": "For sale",
        "maxResultsPerSearch": CHEAP_RESULT_CAP,
    }
    _print_sold_history(_fetch(client, run_input))


def run_by_url(client: ApifyClient, args: argparse.Namespace) -> None:
    """URL recipe: collect one listing page you already hold.

    Pass your own live listing with --url. UK listings are taken down quickly once a
    property is sold or let, so a saved link often points at a page that no longer
    exists. When that happens you get an `error` row rather than silence, and the
    removed listing is not charged. Search mode is the reliable path.
    """
    if not args.url:
        raise SystemExit(
            "The by-url recipe needs a live listing, for example:\n"
            "  uv run python zoopla-property-api-example.py --example by-url \\\n"
            "      --url https://www.zoopla.co.uk/for-sale/details/70012345/"
        )
    run_input: dict[str, Any] = {
        "mode": "url",
        "listingUrls": [args.url],
    }
    _print_listings(_fetch(client, run_input))


def main() -> None:
    """Dispatch one of the Zoopla UK Property API recipes."""
    parser = argparse.ArgumentParser(description="Zoopla UK Property API examples")
    parser.add_argument(
        "--example",
        default="default",
        choices=["default", "sold-prices", "by-url"],
        help="Which recipe to run. See the README for what each one returns.",
    )
    parser.add_argument(
        "--url",
        default=None,
        help="A live listing URL, used only by the by-url recipe.",
    )
    args = parser.parse_args()

    token = os.getenv("APIFY_API_TOKEN")
    if not token:
        raise SystemExit(
            "Set APIFY_API_TOKEN in .env or the environment. "
            "Get a free key at https://apify.com?fpr=9n7kx3"
        )

    client = ApifyClient(token)
    dispatch = {
        "default": run_default,
        "sold-prices": run_sold_prices,
        "by-url": run_by_url,
    }
    dispatch[args.example](client, args)


if __name__ == "__main__":
    main()
