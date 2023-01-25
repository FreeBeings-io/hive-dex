CREATE OR REPLACE FUNCTION hive_dex.query_get_last_trade()
    RETURNS JSONB
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
            temprow RECORD;
            _nai VARCHAR(11);
            _side VARCHAR(4);
            _last_price NUMERIC;
            _best_bid NUMERIC;
            _best_ask NUMERIC;
            _high_price NUMERIC;
            _low_price NUMERIC;
            _base_volume BIGINT;
            _quote_volume BIGINT;
            _block_num_yest BIGINT;
        BEGIN
            SELECT * INTO temprow FROM hive_dex.trades ORDER BY id DESC LIMIT 1;
            IF temprow.current_nai = '@@000000013' THEN
                _last_price := trunc((temprow.current_amount::numeric / temprow.open_amount::numeric)::numeric, 6);
            ELSIF temprow.current_nai = '@@000000021' THEN
                _last_price := trunc((temprow.open_amount::numeric / temprow.current_amount::numeric)::numeric, 6);
            END IF;
            _block_num_yest := (hive.app_get_irreversible_block()) - (1 * 24 * 60 * 20);
            -- hbd vol
            SELECT TRUNC(SUM(current_amount)/1000::numeric,3) hbd
            INTO _quote_volume
            FROM hive_dex.trades
            WHERE current_nai = '@@000000013'
                AND block_num >= _block_num_yest;
            -- hive vol
            SELECT TRUNC(SUM(current_amount)/1000::numeric,3) hive
            INTO _base_volume
            FROM hive_dex.trades
            WHERE current_nai = '@@000000021'
                AND block_num >= _block_num_yest;
            -- bid
            SELECT
                (
                    trunc((pays::numeric/receives::numeric)::numeric, 6)
                )::varchar price
            INTO _best_bid
            FROM hive_dex.orders
            WHERE pays_nai = '@@000000013'
                AND pays > 0
                AND expires > NOW() AT TIME ZONE 'utc'
                AND fill_or_kill = false
            ORDER BY price DESC
            LIMIT 1;
            -- ask
            SELECT
                (
                    trunc((receives::numeric/pays::numeric)::numeric, 6)
                )::varchar price
            INTO _best_ask
            FROM hive_dex.orders
            WHERE pays_nai = '@@000000021'
                AND pays > 0
                AND expires > NOW() AT TIME ZONE 'utc'
                AND fill_or_kill = false
            ORDER BY price ASC
            LIMIT 1;
            -- high/low
            SELECT TRUNC(MAX(price),6) high, TRUNC(MIN(price),6) low
            INTO _high_price, _low_price
            FROM hive_dex.trades
            WHERE block_num >= _block_num_yest
            AND open_amount > 1
            AND current_amount > 1;
            RETURN jsonb_build_object(
                'last_price',_last_price,
                'base_volume',_base_volume,
                'quote_volume',_quote_volume,
                'bid', _best_bid,
                'ask', _best_ask,
                'high', _high_price,
                'low', _low_price
            );
        END;
    $function$;