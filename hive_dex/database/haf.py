import os
import re
from threading import Thread
from hive_dex.config import Config
from hive_dex.database.core import DbSession

START_DAYS_DISTANCE = 1
SOURCE_DIR = os.path.dirname(__file__) + "/sql"


config = Config.config


class Haf:

    module_list = []

    @classmethod
    def _get_haf_sync_head(cls, db):
        sql = "SELECT hive.app_get_irreversible_block();"
        res = db.do('select', sql)
        return res[0]

    @classmethod
    def _is_valid_module(cls, module):
        return bool(re.match(r'^[a-z]+[_]*$', module))
    
    @classmethod
    def _update_functions(cls, db, functions):
        db.do('execute', functions, None)
        db.do('commit')

    @classmethod
    def _init_hive_dex(cls, db):
        db.do('execute', f"CREATE SCHEMA IF NOT EXISTS {config['schema']};")
        db.do('commit')
        for _file in ['tables.sql', 'functions.sql', 'sync.sql', 'queries.sql']:
            _sql = (open(f'{SOURCE_DIR}/{_file}', 'r', encoding='UTF-8').read()
                .replace('hive_dex.', f"{config['schema']}.")
            )
            db.do('execute', _sql)
        db.do('commit')
        has_globs = db.do('select', f"SELECT * FROM {config['schema']}.global_props;")
        if not has_globs:
            db.do('execute', f"INSERT INTO {config['schema']}.global_props (check_in) VALUES (NULL);")
            db.do('commit')
    
    @classmethod
    def _prepare_data(cls, db):
        has_prepped = db.do('select', f"SELECT * FROM {config['schema']}.pairs;")
        if not has_prepped:
            db.do('execute',f"INSERT INTO {config['schema']}.pairs VALUES ('HIVE_HBD', 'HIVE', 'HBD')")
            db.do('commit')
    
    @classmethod
    def _init_main_sync(cls, db):
        print("Starting main sync process...")
        db.do('execute', f"CALL {config['schema']}.sync_main();")
    
    @classmethod
    def _cleanup(cls, db):
        """Stops any running sync procedures from previous instances."""
        try:
            running = db.do('select_one', f"SELECT {config['schema']}.is_sync_running('{config['schema']}-main');")
            if running is True:
                db.do('execute', f"SELECT {config['schema']}.terminate_main_sync('{config['schema']}-main');")
        except:
            pass
        if config['reset'] == 'true':
            try:
                db.do('execute', f"DROP SCHEMA {config['schema']} CASCADE;")
                db.do('commit')
            except Exception as err:
                print(f"Reset encountered error: {err}")

    @classmethod
    def init(cls, db):
        """Initializes the HAF sync process."""
        cls._cleanup(db)
        cls._init_hive_dex(db)
        cls._prepare_data(db)
        start = db.do('select', f"SELECT {config['schema']}.global_sync_enabled()")[0][0]
        if start is True:
            db_main = DbSession('main')
            Thread(target=cls._init_main_sync, args=(db_main,)).start()
        else:
            print("Global sync is disabled. Shutting down")
            os._exit(0)
