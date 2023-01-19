from fastapi import APIRouter, HTTPException, Request
from datetime import datetime

from hive_dex.database.access import select, select_raw
from hive_dex.server.queries.historical import get_historical_trades_buys, get_historical_trades_sells
from hive_dex.server.buffer import Buffer
from hive_dex.tools import UTC_TIMESTAMP_FORMAT, add_server_metadata, populate_by_schema, check_timestamp_format

router_historical = APIRouter()

@router_historical.get("/historical_trades", tags=['historical_trades'])
async def get_historical_trades(request: Request, start_time:str=None, end_time:str=None, limit:int=25, side:str="all", ticker_id="HIVE_HBD"):
    """
        Returns the historical trades.
        `start_time` and `end_time` use require the format "yyyy-mm-ddT%hh:mm:ss",
        for example 2023-01-19T09:00:00
    """
    _limit = limit if limit < 25 else 25
    _buffer = Buffer.check_buffer(request['path'])
    if _buffer is not None:
        return _buffer
    result = {}
    if ticker_id == 'HIVE_HBD':
        if start_time:
            if not check_timestamp_format(start_time):
                raise HTTPException(status_code=400, detail=f"invalid start_time: '{start_time}'")
        if end_time:
            if not check_timestamp_format(end_time):
                raise HTTPException(status_code=400, detail=f"invalid end_time: '{start_time}'")
        if side == 'all':
            buys = get_historical_trades_buys(_limit, start_time, end_time)
            _buys = select_raw(buys) or []
            sells = get_historical_trades_sells(_limit, start_time, end_time)
            _sells = select_raw(sells) or []
            result['buy'] = populate_by_schema(_buys, ['trade_id', 'price', 'base_volume', 'target_volume', 'trade_timestamp', 'type'])
            result['sell'] = populate_by_schema(_sells, ['trade_id', 'price', 'base_volume', 'target_volume', 'trade_timestamp', 'type'])
        elif side == 'buy':
            buys = get_historical_trades_buys(_limit, start_time, end_time)
            _buys = select_raw(buys) or []
            result['buy'] = populate_by_schema(_buys, ['trade_id', 'price', 'base_volume', 'target_volume', 'trade_timestamp', 'type'])
        elif side == 'sell':
            sells = get_historical_trades_sells(_limit, start_time, end_time)
            _sells = select_raw(sells) or []
            result['sell'] = populate_by_schema(_sells, ['trade_id', 'price', 'base_volume', 'target_volume', 'trade_timestamp', 'type'])
    else:
        raise HTTPException(status_code=400, detail=f"ticker '{ticker_id}' not supported")
    Buffer.update_buffer(request['path'], result)
    return add_server_metadata(result)