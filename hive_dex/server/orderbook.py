from fastapi import APIRouter, HTTPException
from datetime import datetime

from hive_dex.database.access import select, select_raw
from hive_dex.server.queries.orderbook import get_orderbook_buys, get_orderbook_sells
from hive_dex.tools import UTC_TIMESTAMP_FORMAT

router_orderbook = APIRouter()

@router_orderbook.get("/orderbook", tags=['orderbook'])
async def get_orderbook(ticker_id, depth:int=10):
    "Returns the orderbook."
    result = {}
    result['timezone'] = "UTC"
    result['server_time'] = datetime.strftime(datetime.utcnow(), UTC_TIMESTAMP_FORMAT)
    if ticker_id == 'HIVE_HBD':
        buys = get_orderbook_buys(depth)
        _buys = select_raw(buys) or []
        sells = get_orderbook_sells(depth)
        _sells = select_raw(sells) or []
        result['bids'] = _buys
        result['asks'] = _sells
    else:
        raise HTTPException(status_code=400, detail=f"ticker '{ticker_id}' not supported")
    return result
