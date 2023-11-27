# -*- coding: utf-8 -*-

from beans_logging import Logger, LoggerLoader
from beans_logging_fastapi import (
    add_http_file_handler,
    add_http_file_json_handler,
    http_file_format,
)

from src.config import config


logger_loader = LoggerLoader(config=config.logger, auto_config_file=False)
logger: Logger = logger_loader.load()


def _http_file_format(record: dict) -> str:
    _format = http_file_format(
        record=record, msg_format=config.logger.extra.http_file_format
    )
    return _format


if config.logger.extra.http_file_enabled:
    add_http_file_handler(
        logger_loader=logger_loader,
        log_path=config.logger.extra.http_log_path,
        err_path=config.logger.extra.http_err_path,
        formatter=_http_file_format,
    )

if config.logger.extra.http_json_enabled:
    add_http_file_json_handler(
        logger_loader=logger_loader,
        log_path=config.logger.extra.http_json_path,
        err_path=config.logger.extra.http_json_err_path,
    )


__all__ = ["logger_loader", "logger"]
