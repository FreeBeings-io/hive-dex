CREATE OR REPLACE FUNCTION hive_dex.limit_order_create_operation( _block_num INTEGER, _block_time TIMESTAMP, _trx_id BYTEA, _data JSON)
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
            temprow RECORD;
            _acc VARCHAR(16);
            _order_id BIGINT;
            _pair_id VARCHAR(9);
            _hbd BIGINT;
            _hive BIGINT;
            _side VARCHAR(1);
            _fill_or_kill BOOLEAN;
            _expires TIMESTAMP;
            
            _price REAL;
            _base_amount BIGINT;
            _base_nai VARCHAR(11);
            _quote_amount BIGINT;
            _quote_nai VARCHAR(11);
        BEGIN

            _pair_id := 'HIVE_HBD';
            _acc := _data->'value'->>'owner';
            _order_id := _data->'value'->>'orderid';
            _base_amount := _data->'value'->'amount_to_sell'->>'amount';
            _base_nai := _data->'value'->'amount_to_sell'->>'nai';
            _quote_amount := _data->'value'->'min_to_receive'->>'amount';
            _quote_nai := _data->'value'->'min_to_receive'->>'nai';
            _fill_or_kill := _data->'value'->'fill_or_kill';
            _expires := _data->'value'->>'expiration';

            IF _base_nai = '@@000000013' THEN
                _side := 'b';
                _hbd := _base_amount;
                _hive := _quote_amount;
            ELSIF _base_nai = '@@000000021' THEN
                _side := 's';
                _hive := _base_amount;
                _hbd := _quote_amount;
            END IF;

            INSERT INTO hive_dex.orders (acc, order_id, pays, pays_nai, receives, receives_nai, fill_or_kill, expires, trx_id, block_num)
            VALUES (_acc, _order_id, _base_amount, _base_nai, _quote_amount, _quote_nai, _fill_or_kill, _expires, _trx_id, _block_num)
            ON CONFLICT (acc, order_id) DO UPDATE
                SET pays = _base_amount,
                    pays_nai = _base_nai,
                    receives = _quote_amount,
                    receives_nai = _quote_nai,
                    fill_or_kill = _fill_or_kill,
                    expires= _expires,
                    trx_id = _trx_id,
                    block_num = _block_num;

        END;
    $function$;

CREATE OR REPLACE FUNCTION hive_dex.limit_order_create2_operation( _block_num INTEGER, _block_time TIMESTAMP, _trx_id BYTEA, _data JSON)
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
            temprow RECORD;
            _acc VARCHAR(16);
            _order_id BIGINT;
            _pair_id VARCHAR(9);
            _hbd BIGINT;
            _hive BIGINT;
            _side VARCHAR(1);
            _fill_or_kill BOOLEAN;
            _expires TIMESTAMP;
            
            _price REAL;
            _base_amount BIGINT;
            _base_nai VARCHAR(11);
            _quote_amount BIGINT;
            _quote_nai VARCHAR(11);
        BEGIN

            _pair_id := 'HIVE_HBD';
            _acc := _data->'value'->>'owner';
            _order_id := _data->'value'->>'orderid';
            _base_amount := _data->'value'->'amount_to_sell'->>'amount';
            _base_nai := _data->'value'->'amount_to_sell'->>'nai';
            _quote_amount := _data->'value'->'exchange_rate'->'quote'->>'amount';
            _quote_nai := _data->'value'->'exchange_rate'->'quote'->>'nai';
            _fill_or_kill := _data->'value'->'fill_or_kill';
            _expires := _data->'value'->>'expiration';


            IF _base_nai = '@@000000013' THEN
                _side := 'b';
                _hbd := _base_amount;
                _hive := _quote_amount;
            ELSIF _base_nai = '@@000000021' THEN
                _side := 's';
                _hive := _base_amount;
                _hbd := _quote_amount;
            END IF;

            INSERT INTO hive_dex.orders (acc, order_id, pays, pays_nai, receives, receives_nai, fill_or_kill, expires, trx_id, block_num)
            VALUES (_acc, _order_id, _base_amount, _base_nai, _quote_amount, _quote_nai, _fill_or_kill, _expires, _trx_id, _block_num)
            ON CONFLICT (acc, order_id) DO UPDATE
                SET pays = _base_amount,
                    pays_nai = _base_nai,
                    receives = _quote_amount,
                    receives_nai = _quote_nai,
                    fill_or_kill = _fill_or_kill,
                    expires= _expires,
                    trx_id = _trx_id,
                    block_num = _block_num;

        END;
    $function$;

CREATE OR REPLACE FUNCTION hive_dex.limit_order_cancel_operation( _block_num INTEGER, _block_time TIMESTAMP, _trx_id BYTEA, _data JSON)
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
            _acc VARCHAR(16);
            _order_id BIGINT;
        BEGIN

            _acc := _data->'value'->>'owner';
            _order_id := _data->'value'->'orderid';

            DELETE FROM hive_dex.orders WHERE acc = _acc AND order_id = _order_id;

        END;
    $function$;

CREATE OR REPLACE FUNCTION hive_dex.limit_order_cancelled_operation( _block_num INTEGER, _block_time TIMESTAMP, _trx_id BYTEA, _data JSON)
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
            _acc VARCHAR(16);
        BEGIN

            _acc := _data->'value'->>'seller';


        END;
    $function$;

CREATE OR REPLACE FUNCTION hive_dex.fill_order_operation( _block_num INTEGER, _block_time TIMESTAMP, _trx_id BYTEA, _data JSON)
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
            _current_owner VARCHAR(16);
            _open_owner VARCHAR(16);
            _side VARCHAR(1);
            _hbd BIGINT := 0;
            _hive BIGINT := 0;
            _price NUMERIC;

            _current_id BIGINT;
            _current_amount BIGINT;
            _current_nai VARCHAR(11);
            _open_id BIGINT;
            _open_amount BIGINT;
            _open_nai VARCHAR(11);

            temprow RECORD;
        BEGIN

            _current_id := _data->'value'->>'current_orderid';
            _current_owner := _data->'value'->>'current_owner';
            _current_amount := _data->'value'->'current_pays'->>'amount';
            _current_nai := _data->'value'->'current_pays'->>'nai';
            
            _open_id := _data->'value'->>'open_orderid';
            _open_owner := _data->'value'->>'open_owner';
            _open_amount := _data->'value'->'open_pays'->>'amount';
            _open_nai := _data->'value'->'open_pays'->>'nai';

            IF _current_nai = '@@000000013' THEN
                _price := round((_current_amount::numeric/_open_amount::numeric)::numeric, 6);
            ELSIF _current_nai = '@@000000021' THEN
                _price := round((_open_amount::numeric/_current_amount::numeric)::numeric, 6);
            END IF;

            -- current

            UPDATE hive_dex.orders
                SET pays = pays - _current_amount
            WHERE acc = _current_owner
                AND order_id = _current_id;

            -- open
            UPDATE hive_dex.orders
                SET pays = pays - _open_amount
            WHERE acc = _open_owner
                AND order_id = _open_id;

            INSERT INTO hive_dex.trades(
                block_num, block_time, trx_id, current_owner, current_amount,
                current_nai, open_owner, open_amount, open_nai, price
            )
            VALUES (
                _block_num, _block_time, _trx_id, _current_owner, _current_amount,
                _current_nai, _open_owner, _open_amount, _open_nai, _price
            );

        END;
    $function$;

CREATE OR REPLACE FUNCTION hive_dex.prune()
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$
        BEGIN
            DELETE FROM hive_dex.orders
            WHERE pays = 0;

            DELETE FROM hive_dex.orders
            WHERE fill_or_kill = true
                AND block_num < (hive.app_get_irreversible_block() - 1200);
        END;
    $function$;