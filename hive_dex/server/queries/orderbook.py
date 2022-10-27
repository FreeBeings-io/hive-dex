

def get_orderbook_buys(depth:int):
    sql_buys = f"""
        SELECT
            (
                to_char((hive::decimal(12,3))/1000,'FM999999999.000')
            ) hive,
            (
                to_char(hbd::real/hive::numeric(20,6),'FM999999999.000000')
            ) price
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
                to_char((hbd::real/hive)::numeric(20,6), 'FM9999999990.000000')
            ) price,
            (
                to_char((hive::numeric(12,3))/1000, 'FM9999999990.000')
            ) hive
        FROM dev.orders
        WHERE pair_id = 'HIVE_HBD'
            AND side = 's'
            AND settled < hive
            AND expires > NOW() AT TIME ZONE 'utc'
        ORDER BY price ASC
        LIMIT {depth};
    """
    return sql_sells