from datetime import datetime

from hive_dex.database.access import select
from hive_dex.tools import UTC_TIMESTAMP_FORMAT, schemafy

class SystemStatus:

    @classmethod
    def _get_haf_sync_head(cls):
        sql = f"SELECT hive.app_get_irreversible_block();"
        res = select(sql, ['head_block_num'])
        return res[0]
    
    @classmethod
    def _get_global_props(cls):
        sql = schemafy(f"SELECT latest_block_num, check_in FROM hive_dex.global_props;")
        res = select(sql, ['latest_block_num', 'check_in'])
        return res[0]

    @classmethod
    def get_server_status(cls):
        timezone = "UTC"
        now = datetime.strftime(datetime.utcnow(),UTC_TIMESTAMP_FORMAT)
        haf_head = cls._get_haf_sync_head()['head_block_num']
        global_props = cls._get_global_props()
        if global_props['latest_block_num'] is None:
            global_props['latest_block_num'] = 0
        _diff = haf_head - global_props['latest_block_num']
        if _diff > 10:
            health = f"BAD - {_diff} blocks behind"
        else:
            health = "GOOD"
        res = {
            "timezone": timezone,
            "timestamp": now,
            "haf": {
                "hive_head": haf_head,
                "db_head": global_props['latest_block_num'],
                "health": health
            }
        }
        return res
