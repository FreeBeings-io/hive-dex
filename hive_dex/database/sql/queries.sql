CREATE OR REPLACE FUNCTION hive_dex.query_get_last_trade()
    RETURNS JSONB
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
            temprow RECORD;
            _nai VARCHAR(11);
            _side VARCHAR(4);
            _last_price NUMERIC(12,6);
            _best_bid NUMERIC(12,6);
            _best_ask NUMERIC(12,6);
            _high_price NUMERIC(12,6);
            _low_price NUMERIC(12,6);
            _base_volume BIGINT;
            _target_volume BIGINT;
            _block_num_yest BIGINT;
        BEGIN
            SELECT * INTO temprow FROM hive_dex.trades ORDER BY id DESC LIMIT 1;
            IF temprow.current_nai = '@@000000013' THEN
                _last_price := round((temprow.current_amount::numeric / temprow.open_amount::numeric)::numeric(12,6), 6);
            ELSIF temprow.current_nai = '@@000000021' THEN
                _last_price := round((temprow.open_amount::numeric / temprow.current_amount::numeric)::numeric(12,6), 6);
            END IF;
            _block_num_yest := (hive.app_get_irreversible_block()) - (1 * 24 * 60 * 20);
            -- hbd vol
            SELECT ROUND(SUM(current_amount)/1000::numeric,3) hbd
            INTO _base_volume
            FROM hive_dex.trades
            WHERE current_nai = '@@000000013'
                AND block_num >= _block_num_yest;
            -- hive vol
            SELECT ROUND(SUM(current_amount)/1000::numeric,3) hive
            INTO _target_volume
            FROM hive_dex.trades
            WHERE current_nai = '@@000000021'
                AND block_num >= _block_num_yest;
            -- bid
            SELECT
                (
                    round((pays::numeric/receives::numeric)::numeric(12,6), 6)
                )::varchar price
            INTO _best_bid
            FROM dev.orders
            WHERE pays_nai = '@@000000013'
                AND settled < pays
                AND expires > NOW() AT TIME ZONE 'utc'
            ORDER BY price DESC
            LIMIT 1;
            -- ask
            SELECT
                (
                    round((receives::numeric/pays::numeric)::numeric(12,6), 6)
                )::varchar price
            INTO _best_ask
            FROM dev.orders
            WHERE pays_nai = '@@000000021'
                AND settled < pays
                AND expires > NOW() AT TIME ZONE 'utc'
            ORDER BY price ASC
            LIMIT 1;
            -- high/low
            SELECT ROUND(MAX(price),6) high, ROUND(MIN(price),6) low
            INTO _high_price, _low_price
            FROM hive_dex.trades
            WHERE block_num >= _block_num_yest;
            RETURN jsonb_build_object(
                'last_price',_last_price,
                'base_volume',_base_volume,
                'target_volume',_target_volume,
                'bid', _best_bid,
                'ask', _best_ask,
                'high', _high_price,
                'low', _low_price
            );
        END;
    $function$;