# -*- coding: utf-8 -*-

from urllib.parse import quote_plus
from typing import Any, Dict, Optional, Union
from typing_extensions import Self

from pydantic import AnyUrl, Field, conint, constr, SecretStr, model_validator
from pydantic_settings import SettingsConfigDict

from api.core.constants import ENV_PREFIX_DB

from ._base import BaseConfig


class DbConfig(BaseConfig):
    dialect: constr(strip_whitespace=True) = Field(..., min_length=2, max_length=32)  # type: ignore
    driver: constr(strip_whitespace=True) = Field(..., min_length=2, max_length=32)  # type: ignore

    host: constr(strip_whitespace=True) = Field(..., min_length=2, max_length=128)  # type: ignore
    port: int = Field(..., ge=100, le=65535)
    username: constr(strip_whitespace=True) = Field(..., min_length=2, max_length=32)  # type: ignore
    password: SecretStr = Field(..., min_length=8, max_length=64)
    database: constr(strip_whitespace=True) = Field(..., min_length=2, max_length=128)  # type: ignore
    dsn_url: Optional[AnyUrl] = Field(default=None)

    read_host: Optional[
        constr(strip_whitespace=True, min_length=2, max_length=128)  # type: ignore
    ] = Field(default=None)
    read_port: Optional[conint(ge=100, le=65535)] = Field(default=None)  # type: ignore
    read_username: Optional[
        constr(strip_whitespace=True, min_length=2, max_length=32)  # type: ignore
    ] = Field(default=None)
    read_password: Optional[SecretStr] = Field(default=None, min_length=8, max_length=64)  # type: ignore
    read_database: Optional[
        constr(strip_whitespace=True, min_length=2, max_length=128)  # type: ignore
    ] = Field(default=None)
    read_dsn_url: Optional[AnyUrl] = Field(default=None)

    connect_args: Optional[Dict[str, Any]] = Field(default=None)
    prefix: constr(strip_whitespace=True) = Field(..., max_length=16)  # type: ignore
    max_try_connect: int = Field(..., ge=1, le=100)
    retry_after: int = Field(..., ge=1, le=600)
    echo_sql: Union[bool, constr(strip_whitespace=True, regex="^(debug)$")] = Field(...)  # type: ignore
    echo_pool: Union[bool, constr(strip_whitespace=True, regex="^(debug)$")] = Field(  # type: ignore
        ...
    )
    pool_size: int = Field(..., ge=0, le=1000)  # 0 means no limit
    max_overflow: int = Field(
        ..., ge=0, le=1000
    )  # pool_size + max_overflow = max number of pools allowed
    pool_recycle: int = Field(..., ge=-1, le=86_400)  # 3 hours, -1 means no timeout
    pool_timeout: int = Field(..., ge=0, le=3600)  # 30 seconds
    select_limit: int = Field(..., ge=1, le=100_000)
    select_max_limit: int = Field(..., ge=1, le=10_000_000)
    select_is_desc: bool = Field(...)

    model_config = SettingsConfigDict(env_prefix=ENV_PREFIX_DB)


class FrozenDbConfig(DbConfig):
    @model_validator(mode="after")
    def _check_all(self) -> Self:
        _dsn_url_template = (
            "{dialect}+{driver}://{username}:{password}@{host}:{port}/{database}"
        )

        if not self.dsn_url:
            _encoded_password = quote_plus(self.password.get_secret_value())
            self.dsn_url = _dsn_url_template.format(
                dialect=self.dialect,
                driver=self.driver,
                username=self.username,
                password=_encoded_password,
                host=self.host,
                port=self.port,
                database=self.database,
            )

        if not self.read_dsn_url:
            if self.read_password:
                _encoded_password = quote_plus(self.read_password.get_secret_value())
            else:
                _encoded_password = quote_plus(self.password.get_secret_value())

            self.read_dsn_url = _dsn_url_template.format(
                dialect=self.dialect,
                driver=self.driver,
                username=self.read_username or self.username,
                password=_encoded_password,
                host=self.read_host or self.host,
                port=self.read_port or self.port,
                database=self.read_database or self.database,
            )

        return self

    model_config = SettingsConfigDict(frozen=True)


__all__ = ["DbConfig", "FrozenDbConfig"]
