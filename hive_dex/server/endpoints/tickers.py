from fastapi import APIRouter, HTTPException, Request
from datetime import datetime

from hive_dex.database.access import select
from hive_dex.server.buffer import Buffer
from hive_dex.tools import UTC_TIMESTAMP_FORMAT, add_server_metadata, schemafy

router_tickers = APIRouter()

@router_tickers.get("/tickers", tags=['tickers'])
async def get_ticker(request: Request, ticker_id="HIVE_HBD"):
    "Returns the ticker for the given ticker_id."
    _buffer = Buffer.check_buffer(request['path'])
    if _buffer is not None:
        return _buffer
    result = {}
    result['timezone'] = "UTC"
    result['server_time'] = datetime.strftime(datetime.utcnow(), UTC_TIMESTAMP_FORMAT)
    if ticker_id == 'HIVE_HBD':
        result['ticker_id'] = ticker_id
        result['base_currency'] = 'HIVE'
        result['quote_currency'] = 'HBD'
        result['data'] = select(schemafy("SELECT hive_dex.query_get_last_trade();"),['data'])[0]['data']
    else:
        raise HTTPException(status_code=400, detail=f"ticker '{ticker_id}' not supported")
    Buffer.update_buffer(request['path'], result)
    return add_server_metadata(result)
