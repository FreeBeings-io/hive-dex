from hive_dex.database.core import DbSession
from hive_dex.tools import populate_by_schema, normalize_types

_read_db = DbSession("read")

def select_raw(sql:str):
    _res = _read_db.do('select',sql)
    return _res

def select(sql:str, schema:list, one:bool = False):
    _res = _read_db.do('select',sql)
    res = []
    if _res:
        assert len(schema) == len(_res[0]), 'invalid schema'
        res = populate_by_schema(_res, schema)
        if one:
            return normalize_types(res)[0]
        else:
            return normalize_types(res)
