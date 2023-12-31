# -*- coding: utf-8 -*-

import os
from urllib.parse import quote_plus
from typing import List, Dict, Any, Optional, Union

from pydantic import Field, constr, root_validator, validator, AnyUrl

from beans_logging import LoggerConfigPM

from src.core.constants import (
    EnvEnum,
    CORSMethodEnum,
    ENV_PREFIX,
    ENV_PREFIX_APP,
    ENV_PREFIX_DB,
)
from .base import FrozenBaseConfig, BaseConfig
from __version__ import __version__


class RoutesConfig(BaseConfig):
    pass


class ApiConfig(FrozenBaseConfig):
    version: constr(strip_whitespace=True) = Field(
        default="v1", min_length=1, max_length=16
    )
    prefix: constr(strip_whitespace=True) = Field(default="", max_length=128)
    routes: RoutesConfig = Field(default_factory=RoutesConfig)

    @validator("prefix", always=True)
    def _check_prefix(cls, val: str, values: Dict[str, Any]) -> str:
        if val and ("{api_version}" in val) and ("version" in values):
            val = val.format(api_version=values["version"])
        return val

    class Config:
        env_prefix = f"{ENV_PREFIX}API_"


class CorsConfig(FrozenBaseConfig):
    allow_origins: List[
        constr(strip_whitespace=True, min_length=1, max_length=256)
    ] = Field(default=["*"])
    allow_origin_regex: Optional[constr(strip_whitespace=True)] = Field(
        default=None, min_length=1, max_length=256
    )
    allow_headers: List[
        constr(strip_whitespace=True, min_length=1, max_length=128)
    ] = Field(default=["*"])
    allow_methods: List[CORSMethodEnum] = Field(default=[CORSMethodEnum.ALL])
    allow_credentials: bool = Field(default=False)
    expose_headers: List[
        constr(strip_whitespace=True, min_length=1, max_length=128)
    ] = Field(default=[])
    max_age: int = Field(default=600, ge=0, le=86_400)

    class Config:
        env_prefix = f"{ENV_PREFIX_APP}CORS_"


class DevConfig(BaseConfig):
    reload: bool = Field(default=False)
    reload_includes: Optional[
        List[constr(strip_whitespace=True, min_length=1, max_length=256)]
    ] = Field(default=None)
    reload_excludes: Optional[
        List[constr(strip_whitespace=True, min_length=1, max_length=256)]
    ] = Field(default=None)

    class Config:
        env_prefix = f"{ENV_PREFIX_APP}DEV_"


class FrozenDevConfig(DevConfig):
    @root_validator(skip_on_failure=True)
    def _check_all(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not values["reload"]:
            values["reload_includes"] = None
            values["reload_excludes"] = None
        return values

    class Config:
        frozen = True


class DocsConfig(BaseConfig):
    enabled: bool = Field(default=True)
    openapi_url: Optional[constr(strip_whitespace=True)] = Field(
        default="/openapi.json", min_length=8, max_length=128
    )
    docs_url: Optional[constr(strip_whitespace=True)] = Field(
        default="/docs", min_length=5, max_length=128
    )
    redoc_url: Optional[constr(strip_whitespace=True)] = Field(
        default="/redoc", min_length=6, max_length=128
    )
    swagger_ui_oauth2_redirect_url: Optional[constr(strip_whitespace=True)] = Field(
        default="/docs/oauth2-redirect", min_length=12, max_length=128
    )
    summary: Optional[constr(strip_whitespace=True)] = Field(
        default=None, min_length=2, max_length=128
    )
    description: str = Field(default="", max_length=8192)
    terms_of_service: Optional[constr(strip_whitespace=True)] = Field(
        default=None, min_length=1, max_length=256
    )
    contact: Optional[Dict[str, Any]] = Field(default=None)
    license_info: Optional[Dict[str, Any]] = Field(default=None)
    openapi_tags: Optional[List[Dict[str, Any]]] = Field(default=None)
    swagger_ui_parameters: Optional[Dict[str, Any]] = Field(default=None)

    class Config:
        env_prefix = f"{ENV_PREFIX_APP}DOCS_"


class FrozenDocsConfig(DocsConfig):
    @validator("description", always=True)
    def _check_description(cls, val: str) -> str:
        _desc_file_path = "./assets/description.md"
        if (not val) and os.path.isfile(_desc_file_path):
            with open(_desc_file_path, "r") as _file:
                val = _file.read()
        return val

    @root_validator(skip_on_failure=True)
    def _check_all(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not values["enabled"]:
            values["openapi_url"] = None
            values["docs_url"] = None
            values["redoc_url"] = None
            values["swagger_ui_oauth2_redirect_url"] = None
        return values

    class Config:
        frozen = True


class AppConfig(BaseConfig):
    name: constr(strip_whitespace=True) = Field(
        default="FastAPI ORM Template",
        min_length=2,
        max_length=128,
    )
    slug: constr(strip_whitespace=True) = Field(
        default="fastapi-orm-template", min_length=2, max_length=128
    )
    bind_host: constr(strip_whitespace=True) = Field(
        default="0.0.0.0", min_length=2, max_length=128
    )
    port: int = Field(default=8000, ge=80, lt=65536)
    gzip_min_size: int = Field(default=512, ge=0, le=10_485_760)  # 512 bytes
    behind_proxy: bool = Field(default=True)
    behind_cf_proxy: bool = Field(default=False)
    allowed_hosts: List[
        constr(strip_whitespace=True, min_length=1, max_length=256)
    ] = Field(default=["*"])
    forwarded_allow_ips: List[
        constr(strip_whitespace=True, min_length=1, max_length=256)
    ] = Field(default=["*"])
    cors: CorsConfig = Field(default_factory=CorsConfig)
    dev: DevConfig = Field(default_factory=DevConfig)
    docs: DocsConfig = Field(default_factory=DocsConfig)

    @validator("slug", always=True)
    def _check_slug(cls, val: str, values: Dict[str, Any]) -> str:
        if "name" in values:
            val = (
                values["name"]
                .lower()
                .strip()
                .replace(" ", "-")
                .replace("_", "-")
                .replace(".", "-")
            )
        return val

    class Config:
        env_prefix = f"{ENV_PREFIX_APP}"


class FrozenAppConfig(AppConfig):
    class Config:
        frozen = True


class PathsConfig(BaseConfig):
    data_dir: constr(strip_whitespace=True) = Field(
        default="/var/lib/{app_slug}",
        min_length=2,
        max_length=1024,
        env=f"{ENV_PREFIX_APP}DATA_DIR",
    )
    uploads_dir: constr(strip_whitespace=True) = Field(
        default="{data_dir}/uploads", min_length=2, max_length=1024
    )
    # models_dir: constr(strip_whitespace=True) = Field(
    #     default="{data_dir}/models",
    #     min_length=2,
    #     max_length=1024,
    #     env=f"{ENV_PREFIX_APP}MODELS_DIR",
    # )

    class Config:
        env_prefix = f"{ENV_PREFIX_APP}PATHS_"


class FrozenPathsConfig(PathsConfig):
    @root_validator(skip_on_failure=True)
    def _check_all(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        for _key, _val in values.items():
            if isinstance(_val, str) and ("{data_dir}" in _val):
                values[_key] = _val.format(data_dir=values["data_dir"])

        return values

    class Config:
        frozen = True


class DbConfig(BaseConfig):
    dialect: constr(strip_whitespace=True) = Field(
        default="postgresql", min_length=2, max_length=32
    )
    driver: constr(strip_whitespace=True) = Field(
        default="psycopg", min_length=2, max_length=32
    )

    host: constr(strip_whitespace=True) = Field(
        default="localhost", min_length=2, max_length=128
    )
    port: int = Field(default=5432, ge=100, le=65535)
    username: constr(strip_whitespace=True) = Field(
        default="fot_user", min_length=2, max_length=32
    )
    password: constr(strip_whitespace=True) = Field(
        default="fot_password1", min_length=2, max_length=64
    )
    database: constr(strip_whitespace=True) = Field(
        default="fot_db", min_length=2, max_length=128
    )
    dsn_url: Optional[AnyUrl] = Field(default=None)

    read_host: Optional[
        constr(strip_whitespace=True, min_length=2, max_length=128)
    ] = Field(default=None)
    read_port: Optional[int] = Field(default=None, ge=100, le=65535)
    read_username: Optional[
        constr(strip_whitespace=True, min_length=2, max_length=32)
    ] = Field(default=None)
    read_password: Optional[
        constr(strip_whitespace=True, min_length=2, max_length=64)
    ] = Field(default=None)
    read_database: Optional[
        constr(strip_whitespace=True, min_length=2, max_length=128)
    ] = Field(default=None)
    read_dsn_url: Optional[AnyUrl] = Field(default=None)

    table_prefix: constr(strip_whitespace=True) = Field(default="fot_", max_length=16)
    max_try_connect: int = Field(default=3, ge=1, le=100)
    wait_seconds_try_connect: int = Field(default=5, ge=1, le=600)
    echo_sql: Union[bool, constr(strip_whitespace=True, regex="^(debug)$")] = Field(
        default=False
    )
    echo_pool: Union[bool, constr(strip_whitespace=True, regex="^(debug)$")] = Field(
        default=False
    )
    pool_size: int = Field(default=10, ge=0, le=1000)  # 0 means no limit
    max_overflow: int = Field(
        default=10, ge=0, le=1000
    )  # pool_size + max_overflow = max number of pools allowed
    pool_recycle: int = Field(
        default=10_800, ge=-1, le=86_400
    )  # 3 hours, -1 means no timeout
    pool_timeout: int = Field(default=30, ge=0, le=3600)  # 30 seconds
    select_limit: int = Field(default=100, ge=1, le=100_000)
    max_select_limit: int = Field(default=100_000, ge=1, le=10_000_000)

    class Config:
        env_prefix = f"{ENV_PREFIX_DB}"


class FrozenDbConfig(DbConfig):
    @root_validator(skip_on_failure=True)
    def _check_all(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        _dsn_url_template = (
            "{dialect}+{driver}://{username}:{password}@{host}:{port}/{database}"
        )

        if not values["dsn_url"]:
            _encoded_password = quote_plus(values["password"])
            values["dsn_url"] = _dsn_url_template.format(
                dialect=values["dialect"],
                driver=values["driver"],
                username=values["username"],
                password=_encoded_password,
                host=values["host"],
                port=values["port"],
                database=values["database"],
            )

        if not values["read_dsn_url"]:
            _encoded_password = quote_plus(
                values["read_password"] or values["password"]
            )
            values["read_dsn_url"] = _dsn_url_template.format(
                dialect=values["dialect"],
                driver=values["driver"],
                username=values["read_username"] or values["username"],
                password=_encoded_password,
                host=values["read_host"] or values["host"],
                port=values["read_port"] or values["port"],
                database=values["read_database"] or values["database"],
            )

        return values

    class Config:
        frozen = True


# Main config schema:
class ConfigSchema(FrozenBaseConfig):
    env: EnvEnum = Field(default=EnvEnum.LOCAL, env="ENV")
    debug: bool = Field(default=False, env="DEBUG")
    version: constr(strip_whitespace=True) = Field(
        default=__version__, min_length=3, max_length=32
    )
    api: ApiConfig = Field(default_factory=ApiConfig)
    app: AppConfig = Field(default_factory=AppConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    db: DbConfig = Field(default_factory=DbConfig)
    logger: LoggerConfigPM = Field(default_factory=LoggerConfigPM)

    @validator("version", always=True)
    def _check_version(cls, val: str) -> str:
        val = __version__
        return val

    @validator("app", always=True)
    def _check_app(cls, val: AppConfig, values: Dict[str, Any]) -> FrozenAppConfig:
        _dev: DevConfig = val.dev
        if ("env" in values) and (values["env"] == EnvEnum.DEVELOPMENT):
            _dev.reload = True
        _dev = FrozenDevConfig(**_dev.dict())

        _docs: DocsConfig = val.docs
        _api = None
        if "api" in values:
            _api: ApiConfig = values["api"]

        if _api and _docs.enabled:
            if _docs.openapi_url and ("{api_prefix}" in _docs.openapi_url):
                _docs.openapi_url = _docs.openapi_url.format(api_prefix=_api.prefix)

            if _docs.docs_url and ("{api_prefix}" in _docs.docs_url):
                _docs.docs_url = _docs.docs_url.format(api_prefix=_api.prefix)

            if _docs.redoc_url and ("{api_prefix}" in _docs.redoc_url):
                _docs.redoc_url = _docs.redoc_url.format(api_prefix=_api.prefix)

            if _docs.swagger_ui_oauth2_redirect_url and (
                "{api_prefix}" in _docs.swagger_ui_oauth2_redirect_url
            ):
                _docs.swagger_ui_oauth2_redirect_url = (
                    _docs.swagger_ui_oauth2_redirect_url.format(api_prefix=_api.prefix)
                )
        _docs = FrozenDocsConfig(**_docs.dict())

        val = FrozenAppConfig(dev=_dev, docs=_docs, **val.dict(exclude={"dev", "docs"}))
        return val

    @validator("paths", always=True)
    def _check_paths(
        cls, val: PathsConfig, values: Dict[str, Any]
    ) -> FrozenPathsConfig:
        if ("app" in values) and ("{app_slug}" in val.data_dir):
            val.data_dir = val.data_dir.format(app_slug=values["app"].slug)

        val = FrozenPathsConfig(**val.dict())
        return val

    @validator("db", always=True)
    def _check_db(cls, val: DbConfig, values: Dict[str, Any]) -> FrozenDbConfig:
        if ("debug" in values) and (not values["debug"]):
            os.environ.pop(f"{ENV_PREFIX_DB}ECHO_SQL", None)
            val.echo_sql = False

            os.environ.pop(f"{ENV_PREFIX_DB}ECHO_POOL", None)
            val.echo_pool = False

        val = FrozenDbConfig(**val.dict())
        return val

    @validator("logger", always=True)
    def _check_logger(
        cls, val: LoggerConfigPM, values: Dict[str, Any]
    ) -> LoggerConfigPM:
        if "app" in values:
            if not val.app_name:
                val.app_name = values["app"].slug
            elif "{app_slug}" in val.app_name:
                val.app_name = val.app_name.format(app_slug=values["app"].slug)

        if f"{ENV_PREFIX_APP}LOGS_DIR" in os.environ:
            val.file.logs_dir = os.getenv(f"{ENV_PREFIX_APP}LOGS_DIR")
        return val

    class Config:
        env_prefix = f"{ENV_PREFIX}"
        env_nested_delimiter = "__"


__all__ = [
    "ConfigSchema",
    "ApiConfig",
    "AppConfig",
    "CorsConfig",
    "DevConfig",
    "DocsConfig",
    "PathsConfig",
    "DbConfig",
    "LoggerConfigPM",
]
