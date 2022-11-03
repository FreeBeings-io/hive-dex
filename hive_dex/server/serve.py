
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hive_dex.config import Config
from hive_dex.server.endpoints.pairs import router_pairs
from hive_dex.server.endpoints.orderbook import router_orderbook
from hive_dex.server.endpoints.tickers import router_tickers
from hive_dex.server.status import SystemStatus
from hive_dex.server.api_metadata import TITLE, DESCRIPTION, VERSION, CONTACT, LICENSE, TAGS_METADATA

from hive_dex.tools import normalize_types

config = Config.config

app = FastAPI(
    title=TITLE,
    description=DESCRIPTION,
    version=VERSION,
    contact=CONTACT,
    license_info=LICENSE,
    openapi_tags=TAGS_METADATA,
    openapi_url="/api/openapi.json",
    docs_url="/"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_pairs)
app.include_router(router_orderbook)
app.include_router(router_tickers)

async def root():
    """Reports the status of Hive DEX API."""
    report = {
        'name': 'Hive DEX API',
        'status': normalize_types(SystemStatus.get_server_status())
    }
    return report

# SYSTEM

app.add_api_route("/api", root, tags=["system"], methods=["GET"], summary="System status")

def run_server():
    """Run server."""
    uvicorn.run(
        "hive_dex.server.serve:app",
        host=config['server_host'],
        port=config['server_port'],
        log_level="info",
        reload=False,
        workers=config['server_workers']
    )
