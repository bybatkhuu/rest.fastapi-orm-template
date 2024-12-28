# -*- coding: utf-8 -*-

import os
from typing import Dict, Any

from onion_config import ConfigLoader
from beans_logging import logger

from src.core.constants import EnvEnum, ENV_PREFIX_DB
from src.core.configs import ConfigSchema


def _pre_load_hook(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """Pre-load hook to modify config data before loading and validation.

    Args:
        config_data (Dict[str, Any]): Pre-loaded config data.

    Returns:
        Dict[str, Any]: Modified config data.
    """

    try:
        if "ENV" in os.environ:
            config_data["env"] = os.getenv("ENV")

        if ("env" in config_data) and (
            (config_data["env"] == EnvEnum.STAGING)
            or (config_data["env"] == EnvEnum.PRODUCTION)
        ):
            if f"{ENV_PREFIX_DB}DSN_URL" not in os.environ and (
                f"{ENV_PREFIX_DB}HOST" not in os.environ
                or f"{ENV_PREFIX_DB}PORT" not in os.environ
                or f"{ENV_PREFIX_DB}USERNAME" not in os.environ
                or f"{ENV_PREFIX_DB}PASSWORD" not in os.environ
                or f"{ENV_PREFIX_DB}DATABASE" not in os.environ
            ):
                raise KeyError(
                    f"Missing required '{ENV_PREFIX_DB}*' environment variables for staging/production environment!"
                )
    except Exception:
        logger.error(f"Error occured while pre-loading config!")
        raise

    return config_data


config: ConfigSchema
try:
    _config_loader = ConfigLoader(
        config_schema=ConfigSchema,
        pre_load_hook=_pre_load_hook,
    )
    # Main config object:
    config: ConfigSchema = _config_loader.load()
except Exception:
    logger.exception("Failed to load config:")
    exit(2)


__all__ = ["config"]
