from typing import Any

import uvicorn
from litestar import Litestar
from litestar.openapi import OpenAPIConfig
from logging import getLogger

from app.config import Configuration
from app.controllers import example_route

LOGGER = getLogger(__name__)


async def __startup(app: Litestar):
    _ = app


async def _shutdown(app: Litestar):
    _ = app


def app():

    return Litestar(
        debug=True,
        route_handlers=[example_route],
        openapi_config=OpenAPIConfig(
            title="API",
            version=Configuration.VERSION,
            description="API",
            path="/docs",
            create_examples=True,  # If we remove create examples: all is OK!
        ),
        on_startup=[__startup],
        on_shutdown=[_shutdown],
    )


def main():
    """Run auth service"""
    uvicorn.run(
        "app.run:app",
        host="0.0.0.0",
        port=Configuration.PORT,
        reload=True,
    )


if __name__ == "__main__":
    main()
