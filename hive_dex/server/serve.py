
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from hive_dex.config import Config
from hive_dex.server.buffer import Buffer
from hive_dex.server.endpoints.pairs import router_pairs
from hive_dex.server.endpoints.orderbook import router_orderbook
from hive_dex.server.endpoints.tickers import router_tickers
from hive_dex.server.endpoints.historical import router_historical
from hive_dex.server.status import SystemStatus
from hive_dex.server.api_metadata import TITLE, DESCRIPTION, VERSION, CONTACT, LICENSE, TAGS_METADATA

from hive_dex.tools import add_server_metadata, normalize_types

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


async def root(request: Request):
    """Reports the status of Hive DEX API."""
    _buffer = Buffer.check_buffer(request['path'])
    if _buffer is not None:
        return _buffer
    report = {
        'name': 'Hive DEX API',
        'status': normalize_types(SystemStatus.get_server_status())
    }
    Buffer.update_buffer(request['path'], report)
    return add_server_metadata(report)

app.add_api_route("/api", root, tags=["system"], methods=["GET"], summary="System status")
app.include_router(router_pairs)
app.include_router(router_orderbook)
app.include_router(router_tickers)
app.include_router(router_historical)

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
