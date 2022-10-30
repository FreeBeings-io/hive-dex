CREATE OR REPLACE FUNCTION hive_dex.global_sync_enabled()
    RETURNS BOOLEAN
    LANGUAGE plpgsql
    VOLATILE AS $function$
        BEGIN
            RETURN (SELECT sync_enabled FROM hive_dex.global_props LIMIT 1);
        END;
    $function$;

CREATE OR REPLACE FUNCTION hive_dex.is_sync_running(app_desc VARCHAR)
    RETURNS BOOLEAN
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
        BEGIN
            RETURN (
                SELECT EXISTS (
                    SELECT * FROM pg_stat_activity
                    WHERE application_name = app_desc
                )
            );
        END;
    $function$;

CREATE OR REPLACE FUNCTION hive_dex.terminate_main_sync(app_desc VARCHAR)
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
            _pid INTEGER;
        BEGIN
            SELECT pid INTO _pid FROM pg_stat_activity
                WHERE application_name = app_desc;
            IF _pid IS NOT NULL THEN
                PERFORM pg_cancel_backend(_pid);
            END IF;
        END;
    $function$;


CREATE OR REPLACE PROCEDURE hive_dex.sync_main()
    LANGUAGE plpgsql
    AS $$
        DECLARE
            temprow RECORD;
            _global_start_block INTEGER;
            _head_haf_block_num INTEGER;
            _latest_block_num INTEGER;
            _first_block INTEGER;
            _last_block INTEGER;
            _step INTEGER;
            _op_ids SMALLINT[];

            _begin INTEGER;
            _target INTEGER;
        BEGIN
            _op_ids := ARRAY [5,21];
            _step := 100000;
            _global_start_block := 0; -- (hive.app_get_irreversible_block()) - (30 * 24 * 60 * 20);
            UPDATE hive_dex.global_props SET pre_sync_target = hive.app_get_irreversible_block();
            SELECT latest_block_num INTO _latest_block_num FROM hive_dex.global_props;

            --decide which block to start at initially
            IF _latest_block_num IS NULL THEN
                _begin := _global_start_block;
            ELSE
                _begin := _latest_block_num;
            END IF;

            -- begin main sync loop
            WHILE hive_dex.global_sync_enabled() LOOP
                _target := hive.app_get_irreversible_block();
                IF _target - _begin >= 0 THEN
                    RAISE NOTICE 'New block range: <%,%>', _begin, _target;
                    FOR _first_block IN _begin .. _target BY _step LOOP
                        _last_block := _first_block + _step - 1;

                        IF _last_block > _target THEN --- in case the _step is larger than range length
                            _last_block := _target;
                        END IF;

                        RAISE NOTICE 'Attempting to process a block range: <%, %>', _first_block, _last_block;
                        FOR temprow IN
                            SELECT
                                ov.id,
                                ov.op_type_id,
                                ov.block_num,
                                ov.timestamp,
                                ov.trx_in_block,
                                tv.trx_hash,
                                ov.body::json
                            FROM hive.operations_view ov
                            JOIN hive.transactions_view tv
                                ON tv.block_num = ov.block_num
                                AND tv.trx_in_block = ov.trx_in_block
                            WHERE ov.block_num >= _first_block
                                AND ov.block_num <= _last_block
                                AND ov.op_type_id = ANY(_op_ids)
                                AND (ov.body::json->'value'->>'expiration')::timestamp > NOW() AT TIME ZONE 'utc'
                            ORDER BY ov.block_num, ov.id
                        LOOP
                            IF temprow.op_type_id = 5 THEN
                                -- limit_order_create_operation
                                PERFORM hive_dex.limit_order_create_operation(temprow.block_num, temprow.timestamp, temprow.trx_hash, temprow.body);
                            ELSIF temprow.op_type_id = 21 THEN
                                -- limit_order_create2_operation
                                PERFORM hive_dex.limit_order_create2_operation(temprow.block_num, temprow.timestamp, temprow.trx_hash, temprow.body);
                            END IF;
                        END LOOP;
                        -- prune
                        PERFORM hive_dex.prune();
                        -- update global props and save
                        UPDATE hive_dex.global_props SET check_in = NOW() AT TIME ZONE 'utc', latest_block_num = _last_block;
                        COMMIT;
                    END LOOP;
                    -- sync trades
                    CALL hive_dex.sync_trades();
                    COMMIT;
                    _begin := _target +1;
                ELSE
                    RAISE NOTICE 'begin: %   target: %', _begin, _target;
                    PERFORM pg_sleep(1);
                END IF;
            END LOOP;
        END;
    $$;

CREATE OR REPLACE PROCEDURE hive_dex.sync_trades()
    LANGUAGE plpgsql
    AS $$
        DECLARE
            temprow RECORD;
            _global_start_block INTEGER;
            _head_haf_block_num INTEGER;
            _latest_block_num INTEGER;
            _first_block INTEGER;
            _last_block INTEGER;
            _step INTEGER;
            _op_ids SMALLINT[];

            _begin INTEGER;
            _target INTEGER;
        BEGIN
            _op_ids := ARRAY [6,57,85];
            _step := 10000;
            _global_start_block := 0; -- (hive.app_get_irreversible_block()) - (30 * 24 * 60 * 20);
            SELECT latest_block_num_trades INTO _latest_block_num FROM hive_dex.global_props;

            --decide which block to start at initially
            IF _latest_block_num IS NULL THEN
                _begin := _global_start_block;
            ELSE
                _begin := _latest_block_num;
            END IF;

            -- process pending
            _target := hive.app_get_irreversible_block();
            IF _target - _begin >= 0 THEN
                RAISE NOTICE 'New block range: <%,%>', _begin, _target;
                FOR _first_block IN _begin .. _target BY _step LOOP
                    _last_block := _first_block + _step - 1;

                    IF _last_block > _target THEN --- in case the _step is larger than range length
                        _last_block := _target;
                    END IF;

                    RAISE NOTICE 'Attempting to process a block range: <%, %>', _first_block, _last_block;
                    FOR temprow IN
                        SELECT
                            ov.id,
                            ov.op_type_id,
                            ov.block_num,
                            ov.timestamp,
                            ov.trx_in_block,
                            tv.trx_hash,
                            ov.body::json
                        FROM hive.operations_view ov
                        JOIN hive.transactions_view tv
                            ON tv.block_num = ov.block_num
                            AND tv.trx_in_block = ov.trx_in_block
                        WHERE ov.block_num >= _first_block
                            AND ov.block_num <= _last_block
                            AND ov.op_type_id = ANY(_op_ids)
                        ORDER BY ov.block_num, ov.id
                    LOOP
                        IF temprow.op_type_id = 57 THEN
                            PERFORM hive_dex.fill_order_operation(temprow.block_num, temprow.timestamp, temprow.trx_hash, temprow.body);
                        ELSIF temprow.op_type_id = 6 THEN
                            -- limit_order_cancel_operation
                            PERFORM hive_dex.limit_order_cancel_operation(temprow.block_num, temprow.timestamp, temprow.trx_hash, temprow.body);
                        ELSIF temprow.op_type_id = 85 THEN
                            -- limit_order_cancelled_operation
                            PERFORM hive_dex.limit_order_cancelled_operation(temprow.block_num, temprow.timestamp, temprow.trx_hash, temprow.body);
                        END IF;
                    END LOOP;
                    -- update global props and save
                    UPDATE hive_dex.global_props SET check_in = NOW() AT TIME ZONE 'utc', latest_block_num_trades = _last_block;
                END LOOP;
                _begin := _target +1;
            ELSE
                RAISE NOTICE 'begin: %   target: %', _begin, _target;
                PERFORM pg_sleep(1);
            END IF;
        END;
    $$;
