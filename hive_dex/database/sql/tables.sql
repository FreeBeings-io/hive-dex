CREATE TABLE IF NOT EXISTS hive_dex.global_props(
    latest_block_num INTEGER,
    latest_block_time TIMESTAMP,
    check_in TIMESTAMP,
    sync_enabled BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS hive_dex.orders(
    order_id BIGINT,
    acc VARCHAR(16),
    sell_amount INTEGER,
    sell_nai VARCHAR(11),

    fill_or_kill BOOLEAN,
    expires TIMESTAMP,
    cancelled BOOLEAN,
);

CREATE TABLE IF NOT EXISTS hive_dex.orders_cancelled(
    order_id BIGINT NOT NULL REFERENCES hive_dex.orders(order_id),
    
);

hive_dex.trades

