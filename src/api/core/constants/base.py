# -*- coding: utf-8 -*-

from enum import Enum


ENV_PREFIX = "FOT_"
ENV_PREFIX_APP = f"{ENV_PREFIX}APP_"
ENV_PREFIX_DB = f"{ENV_PREFIX}DB_"


class EnvEnum(str, Enum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEMO = "demo"
    DOCUMENTATION = "documentation"
    STAGING = "staging"
    PRODUCTION = "production"


class CORSMethodEnum(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    CONNECT = "CONNECT"
    TRACE = "TRACE"
    ALL = "*"


class MethodEnum(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    CONNECT = "CONNECT"
    TRACE = "TRACE"


class WarnEnum(str, Enum):
    ERROR = "ERROR"
    ALWAYS = "ALWAYS"
    DEBUG = "DEBUG"
    IGNORE = "IGNORE"


class OrderDirect(str, Enum):
    ASC = "ASC"
    DESC = "DESC"


__all__ = [
    "ENV_PREFIX",
    "ENV_PREFIX_APP",
    "ENV_PREFIX_DB",
    "EnvEnum",
    "CORSMethodEnum",
    "MethodEnum",
    "WarnEnum",
    "OrderDirect",
]
