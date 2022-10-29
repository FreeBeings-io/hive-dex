

def get_orderbook_buys(depth:int):
    sql_buys = f"""
        SELECT
            (
                round((hive::numeric(12,3))/1000, 3)
            )::varchar hive,
            (
                round(hbd::numeric/hive::numeric(20,6), 6)
            )::varchar price
        FROM dev.orders
        WHERE pair_id = 'HIVE_HBD'
            AND side = 'b'
            AND settled < hbd
            AND expires > NOW() AT TIME ZONE 'utc'
        ORDER BY price DESC
        LIMIT {depth};
    """
    return sql_buys

def get_orderbook_sells(depth:int):
    sql_sells = f"""
        SELECT
            (
                round((hbd::numeric/hive)::numeric(20,6), 6)
            )::varchar price,
            (
                round((hive::numeric(12,3))/1000, 3)
            )::varchar hive
        FROM dev.orders
        WHERE pair_id = 'HIVE_HBD'
            AND side = 's'
            AND settled < hive
            AND expires > NOW() AT TIME ZONE 'utc'
        ORDER BY price ASC
        LIMIT {depth};
    """
    return sql_sells