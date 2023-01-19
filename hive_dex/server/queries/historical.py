"""Queries to get orderbook state."""

from hive_dex.tools import schemafy


def get_historical_trades_buys(limit:int, start_time:str=None, end_time:str=None):
    sql_buys = f"""
        SELECT encode(trx_id, 'hex'),
            price,
            round((current_amount::numeric)/1000, 3),
            round((open_amount::numeric)/1000, 3),
            block_time,
            'buy'
        FROM hive_dex.trades
        WHERE current_nai = '@@000000013'
        """
    if start_time:
        sql_buys += f"AND block_time >= '{start_time}' "
    if end_time:
        sql_buys += f"AND block_time <= '{end_time}' "
    sql_buys += f"ORDER BY block_num DESC LIMIT {limit};"
    return schemafy(sql_buys)

def get_historical_trades_sells(limit:int, start_time:str, end_time:str):
    sql_sells = f"""
        SELECT encode(trx_id, 'hex'),
            price,
            round((current_amount::numeric)/1000, 3),
            round((open_amount::numeric)/1000, 3),
            block_time,
            'sell'
        FROM hive_dex.trades
        WHERE open_nai = '@@000000021'
    """
    if start_time:
        sql_sells += f"AND block_time >= '{start_time}' "
    if end_time:
        sql_sells += f"AND block_time <= '{end_time}' "
    sql_sells += f"ORDER BY block_num DESC LIMIT {limit};"
    return schemafy(sql_sells)
