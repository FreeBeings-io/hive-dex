import sys
import time

from hive_dex.config import Config
from hive_dex.database.core import DbSession
from hive_dex.server.serve import run_server
from hive_dex.database.haf import Haf

config = Config.config

def run():
    """Main entrypoint."""
    db = DbSession('setup')
    try:
        """Runs main application processes and server."""
        print("---   Hive DEX API started   ---")
        time.sleep(3)
        Haf.init(db)
        time.sleep(6)
        run_server()
    except KeyboardInterrupt:
        sys.exit()

if __name__ == "__main__":
    run()
