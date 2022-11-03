CREATE TABLE IF NOT EXISTS hive_dex.global_props(
    latest_block_num INTEGER,
    latest_block_num_trades INTEGER,
    check_in TIMESTAMP,
    sync_enabled BOOLEAN DEFAULT true,
    pre_sync_target INTEGER
);

CREATE TABLE IF NOT EXISTS hive_dex.pairs(
    pair_id VARCHAR(9) PRIMARY KEY,
    base VARCHAR(4),
    target VARCHAR(4)
);

CREATE TABLE IF NOT EXISTS hive_dex.orders(
    trx_id BYTEA,
    block_num INTEGER,
    acc VARCHAR(16),
    order_id BIGINT,
    pays BIGINT,
    pays_nai VARCHAR(11),
    receives BIGINT,
    receives_nai VARCHAR(11),
    settled BIGINT DEFAULT 0,
    fill_or_kill BOOLEAN,
    expires TIMESTAMP,
    PRIMARY KEY (acc, order_id)
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

CREATE INDEX IF NOT EXISTS idx_hive_dex_orders__expires
    ON hive_dex.orders (expires);