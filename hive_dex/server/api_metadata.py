"""Metadata for the FastAPI instance"""

# Main

TITLE = "Hive DEX API"

DESCRIPTION = """
    Market data for the Hive blockchain's internal decentralized exchange.
"""

VERSION = "1.0"

CONTACT = {
    "name": "FreeBeings.io",
    "url": "https://freebeings.io",
    "email": "info@freebeings.io",
}

LICENSE = {
    "name": "MIT License"
}


# Tags for Endpoints

TAGS_METADATA = [
    {
        "name": "pairs",
        "description": "Available pairs."
    },
    {
        "name": "orderbook",
        "description": "Current orderbook."
    },
    {
        "name": "tickers",
        "description": "Current tickers."
    }
]