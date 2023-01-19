import decimal
from datetime import datetime

from hive_dex.config import Config

UTC_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"

config = Config.config

def _populate_by_schema(data, fields):
    """ Populate a new dictionary of items.
    From an array of data items, a new dictionary is mapped to provided fields.
    """
    result = {}
    for i in range(len(fields)):
        result[fields[i]] = data[i]
    return result

def populate_by_schema(data, fields):
    result = []
    for x in data:
        result.append(_populate_by_schema(x, fields))
    return result

def _normalize(data):
    if isinstance(data, dict):
        for k in data:
            if isinstance(data[k], decimal.Decimal):
                data[k] = float(data[k])
            elif isinstance(data[k], datetime):
                data[k] = datetime.strftime(data[k], UTC_TIMESTAMP_FORMAT)
        return data

def normalize_types(data):
    if isinstance(data, list) or isinstance(data, tuple):
        res = []
        for l in data:
            res.append(_normalize(l))
        return res
    elif isinstance(data, dict):
        return _normalize(data)
    return data

def schemafy(data:str):
    _data = data.replace('hive_dex.', f"{config['schema']}.")
    return _data

def add_server_metadata(data:dict):
    data['timezone'] = 'UTC'
    data['server_time'] = datetime.strftime(datetime.utcnow(), UTC_TIMESTAMP_FORMAT)
    return data

def check_timestamp_format(data:str):
    try:
        result = datetime.strptime(data, UTC_TIMESTAMP_FORMAT)
        return True
    except:
        return False