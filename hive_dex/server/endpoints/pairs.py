from fastapi import APIRouter, HTTPException, Request
from datetime import datetime
from hive_dex.server.buffer import Buffer

from hive_dex.tools import UTC_TIMESTAMP_FORMAT, add_server_metadata

PAIRS = [
    {
        "ticker": "HIVE_HBD",
        "base": "HIVE",
        "quote": "HBD"
    }
]

router_pairs = APIRouter()

def _get_pairs():
    return PAIRS


@router_pairs.get("/pairs", tags=['pairs'])
async def get_pairs(request: Request):
    "Returns the available pairs."
    _buffer = Buffer.check_buffer(request['path'])
    if _buffer is not None:
        return _buffer
    result = {}
    result['timezone'] = "UTC"
    result['server_time'] = datetime.strftime(datetime.utcnow(), UTC_TIMESTAMP_FORMAT)
    result["symbols"] = _get_pairs()
    Buffer.update_buffer(request['path'], result)
    return add_server_metadata(result)
