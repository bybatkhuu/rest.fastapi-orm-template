# -*- coding: utf-8 -*-

from datetime import datetime

from pydantic import BaseModel, Field, constr

from src.core.utils import dt


class BasePM(BaseModel):
    class Config:
        json_encoders = {datetime: dt.datetime_to_iso}


class ExtraBasePM(BasePM):
    class Config:
        extra = "allow"


class IdPM(ExtraBasePM):
    id: constr(strip_whitespace=True) = Field(
        ...,
        min_length=32,
        max_length=64,
        title="ID",
        description="Identifier value of the resource.",
        examples=["RES1699854224922928_DC2CC6C9033C4837B6C34C8BB19BB289"],
    )


class AtPM(ExtraBasePM):
    created_at: datetime = Field(
        ...,
        title="Created datetime",
        description="Created datetime of the resource.",
        examples=["2021-01-01T00:00:00+00:00"],
    )
    updated_at: datetime = Field(
        ...,
        title="Updated datetime",
        description="Last updated datetime of the resource.",
        examples=["2021-01-02T00:00:00+00:00"],
    )


__all__ = ["BasePM", "ExtraBasePM", "IdPM", "AtPM"]
