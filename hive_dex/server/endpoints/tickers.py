from fastapi import APIRouter, HTTPException
from datetime import datetime

from hive_dex.database.access import select
from hive_dex.tools import UTC_TIMESTAMP_FORMAT, schemafy

router_tickers = APIRouter()

@router_tickers.get("/tickers", tags=['tickers'])
async def get_ticker(ticker_id="HIVE_HBD"):
    "Returns the ticker for the given ticker_id."
    result = {}
    result['timezone'] = "UTC"
    result['server_time'] = datetime.strftime(datetime.utcnow(), UTC_TIMESTAMP_FORMAT)
    if ticker_id == 'HIVE_HBD':
        result['ticker_id'] = ticker_id
        result['base_currency'] = 'HBD'
        result['target_currency'] = 'HIVE'
        result['data'] = select(schemafy("SELECT hive_dex.query_get_last_trade();"),['data'])[0]['data']
    else:
        raise HTTPException(status_code=400, detail=f"ticker '{ticker_id}' not supported")
    return result
