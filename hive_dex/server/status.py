import datetime

from hive_dex.tools import UTC_TIMESTAMP_FORMAT

class SystemStatus:

    @classmethod
    def get_server_status(cls):
        timezone = "UTC"
        now = datetime.strftime(datetime.utcnow(),UTC_TIMESTAMP_FORMAT)
        res = {
            "timezone": timezone,
            "timestamp": now
        }
        return res