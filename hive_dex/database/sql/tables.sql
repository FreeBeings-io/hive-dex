CREATE TABLE IF NOT EXISTS hive_dex.global_props(
    latest_block_num INTEGER,
    check_in TIMESTAMP,
    sync_enabled BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS hive_dex.pairs(
    pair_id VARCHAR(9) PRIMARY KEY,
    base VARCHAR(4),
    target VARCHAR(4)
);

CREATE TABLE IF NOT EXISTS hive_dex.orders(
    id BIGSERIAL PRIMARY KEY,
    trx_id BYTEA,
    pair_id VARCHAR(9) REFERENCES hive_dex.pairs(pair_id),
    acc VARCHAR(16),
    order_id BIGINT,
    side VARCHAR(1),
    hbd BIGINT,
    hive BIGINT,
    settled BIGINT DEFAULT 0,
    fill_or_kill BOOLEAN,
    expires TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hive_dex.trades(
    id BIGSERIAL PRIMARY KEY,
    block_num INTEGER,
    block_time TIMESTAMP,
    trx_id BYTEA,
    current_owner VARCHAR(16),
    current_amount BIGINT,
    current_nai VARCHAR(11),
    open_owner VARCHAR(16),
    open_amount FLOAT,
    open_nai VARCHAR(11)
);

CREATE INDEX IF NOT EXISTS idx_hdx_orders_expires
    ON hive_dex.orders (expires);


