from fastapi import APIRouter, HTTPException, Request
from datetime import datetime

from hive_dex.database.access import select, select_raw
from hive_dex.server.queries.orderbook import get_orderbook_buys, get_orderbook_sells
from hive_dex.server.buffer import Buffer
from hive_dex.tools import UTC_TIMESTAMP_FORMAT, add_server_metadata

router_orderbook = APIRouter()

@router_orderbook.get("/orderbook", tags=['orderbook'])
async def get_orderbook(request: Request, ticker_id="HIVE_HBD", depth:int=10):
    "Returns the orderbook."
    _buffer = Buffer.check_buffer(request['path'])
    if _buffer is not None:
        return _buffer
    result = {}
    if ticker_id == 'HIVE_HBD':
        buys = get_orderbook_buys(depth)
        _buys = select_raw(buys) or []
        sells = get_orderbook_sells(depth)
        _sells = select_raw(sells) or []
        result['bids'] = _buys
        result['asks'] = _sells
    else:
        raise HTTPException(status_code=400, detail=f"ticker '{ticker_id}' not supported")
    Buffer.update_buffer(request['path'], result)
    return add_server_metadata(result)
