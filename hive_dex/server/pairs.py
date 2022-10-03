"""Plug endpoints for podping."""
from time import time
from fastapi import APIRouter, HTTPException
from datetime import datetime

from hive_dex.database.access import select

TICKERS = [
    {
        "ticker": "HBD_HIVE",
        "base": "HBD",
        "target": "HIVE"
    }
]

router_pairs = APIRouter()

def get_pairs():
    return TICKERS



@router_pairs.get("/pairs", tags=['pairs'])
async def get_podping_url_latest():
    "Returns the available pairs."
    result = {}
    feed_updates = select(sql_feed_update, ['trx_id', 'block_num', 'created', 'reason', 'medium'])
    result["feed_updates"] = feed_updates
    result["iri"] = iri
    _time_since = datetime.utcnow() - datetime.strptime(feed_updates[0]['created'], UTC_TIMESTAMP_FORMAT)
    result["time_since_last_update"] = _time_since.seconds
    return result
