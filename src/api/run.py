# -*- coding: utf-8 -*-

import uvicorn
from pydantic import validate_arguments

from src.config import config


@validate_arguments
def run_uvicorn(app: str = "main:app"):
    """Run uvicorn server.

    Args:
        app (str, optional): Import path to ASGI application. Defaults to "main:app".
    """

    uvicorn.run(
        app=app,
        host=config.app.bind_host,
        port=config.app.port,
        access_log=False,
        server_header=False,
        proxy_headers=config.app.behind_proxy,
        forwarded_allow_ips=config.app.forwarded_allow_ips,
        **config.app.dev.dict(),
    )


__all__ = ["run_uvicorn"]
