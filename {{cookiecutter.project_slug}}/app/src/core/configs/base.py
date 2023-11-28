# -*- coding: utf-8 -*-

from pydantic import BaseSettings
from pydantic.env_settings import SettingsSourceCallable


class BaseConfig(BaseSettings):
    class Config:
        extra = "allow"
        arbitrary_types_allowed = True

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> tuple[SettingsSourceCallable, ...]:
            return env_settings, init_settings, file_secret_settings


class FrozenBaseConfig(BaseConfig):
    class Config:
        frozen = True


__all__ = ["BaseConfig", "FrozenBaseConfig"]
