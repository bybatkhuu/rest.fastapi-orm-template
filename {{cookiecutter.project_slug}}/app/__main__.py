# -*- coding: utf-8 -*-

from src.run import run_uvicorn
from src.logger import logger


if __name__ == "__main__":
    logger.info(f"Starting server from '__main__.py'...")
    run_uvicorn()
