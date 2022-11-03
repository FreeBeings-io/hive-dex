"""Queries to get orderbook state."""

from hive_dex.tools import schemafy


def get_orderbook_buys(depth:int):
    sql_buys = f"""
        SELECT
            (
                round((pays::numeric/receives::numeric)::numeric, 6)
            )::varchar price,
            (
                SUM(round((receives::numeric)/1000, 3)
            ))::varchar hive
        FROM hive_dex.orders
        WHERE pays_nai = '@@000000013'
            AND settled < pays
            AND expires > NOW() AT TIME ZONE 'utc'
        GROUP BY price
        ORDER BY price DESC
        LIMIT {depth};
    """
    return schemafy(sql_buys)

def get_orderbook_sells(depth:int):
    sql_sells = f"""
        SELECT
            (
                round((receives::numeric/pays::numeric)::numeric, 6)
            )::varchar price,
            (
                SUM(round((pays::numeric)/1000, 3)
            ))::varchar hive
        FROM hive_dex.orders
        WHERE pays_nai = '@@000000021'
            AND settled < pays
            AND expires > NOW() AT TIME ZONE 'utc'
        GROUP BY price
        ORDER BY price ASC
        LIMIT {depth};
    """
    return schemafy(sql_sells)