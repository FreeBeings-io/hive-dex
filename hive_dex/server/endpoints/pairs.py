from fastapi import APIRouter, HTTPException
from datetime import datetime

from hive_dex.tools import UTC_TIMESTAMP_FORMAT

PAIRS = [
    {
        "ticker": "HIVE_HBD",
        "base": "HBD",
        "target": "HIVE"
    }
]

router_pairs = APIRouter()

def _get_pairs():
    return PAIRS


@router_pairs.get("/pairs", tags=['pairs'])
async def get_pairs():
    "Returns the available pairs."
    result = {}
    result['timezone'] = "UTC"
    result['server_time'] = datetime.strftime(datetime.utcnow(), UTC_TIMESTAMP_FORMAT)
    result["symbols"] = _get_pairs()
    return result
