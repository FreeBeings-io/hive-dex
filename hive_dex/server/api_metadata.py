"""Metadata for the FastAPI instance"""

# Main

TITLE = "Hive DEX API"

DESCRIPTION = """
    Market data for the Hive blockchain's internal decentralized exchange
"""

VERSION = "1.0"

CONTACT = {
    "name": "FreeBeings.io",
    "url": "https://github.com/FreeBeings-io/hive-dex",
    "email": "developers@freebeings.io",
}

LICENSE = {
    "name": "MIT License"
}


# Tags for Endpoints

TAGS_METADATA = [
    {
        "name": "pairs",
        "description": "Available pairs."
    }
]