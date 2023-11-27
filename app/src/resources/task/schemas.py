# -*- coding: utf-8 -*-

from typing import Union, List, Any, Dict

from pydantic import Field, root_validator, validator

from src.config import config
from src.core.utils.validator import ValidRegEnum
from src.core.schemas import IdPM, TimestampPM, ExtraBasePM, BaseResPM, LinksResPM


_tasks_base_url = f'{config.api.prefix}{config.api.routes.tasks["_prefix"]}'


## Tasks
class TaskBasePM(ExtraBasePM):
    name: str = Field(
        ...,
        min_length=2,
        max_length=64,
        regex=ValidRegEnum.ALPHANUM_EXTEND.value,
        title="Task name",
        description="Name of the task.",
        examples=["Task 1"],
    )
    point: int = Field(
        default=70,
        ge=0,
        le=100,
        title="Task point",
        description="Point of the task.",
        examples=[70],
    )

    @validator("point", always=True)
    def _check_point(cls, value: int) -> int:
        if (value % 10) != 0:
            raise ValueError("Point must be a multiple of 10!")
        return value


class TaskPM(TimestampPM, TaskBasePM, IdPM):
    class Config:
        orm_mode = True


class TasksPM(TaskPM):
    links: LinksResPM = Field(
        default_factory=LinksResPM,
        title="Links",
        description="Links related to the current task.",
        examples=[
            {
                "self": "/api/v1/tasks/TAS1699928748406212_46D46E7E55FA4A6E8478BD6B04195793"
            }
        ],
    )

    @root_validator(skip_on_failure=True)
    def _check_all(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values[
            "links"
        ].self_link = f'{_tasks_base_url}{config.api.routes.tasks["task"].format(task_id=values["id"])}'
        return values


class ResTaskPM(BaseResPM):
    data: Union[TaskPM, None] = Field(
        default=None,
        title="Task data",
        description="Task as a main data.",
        examples=[
            {
                "id": "TAS1699928748406212_46D46E7E55FA4A6E8478BD6B04195793",
                "name": "Task 1",
                "point": 70,
                "updated_at": "2021-01-01T00:00:00+00:00",
                "created_at": "2021-01-01T00:00:00+00:00",
            }
        ],
    )


class ResTasksPM(BaseResPM):
    data: List[TasksPM] = Field(
        default=[],
        title="List of tasks",
        description="List of tasks as main data.",
        examples=[
            [
                {
                    "id": "TAS1699928748406212_46D46E7E55FA4A6E8478BD6B04195793",
                    "name": "Task 1",
                    "point": 70,
                    "updated_at": "2021-01-01T00:00:00+00:00",
                    "created_at": "2021-01-01T00:00:00+00:00",
                    "links": {
                        "self": "/api/v1/tasks/TAS1699928748406212_46D46E7E55FA4A6E8478BD6B04195793"
                    },
                },
                {
                    "id": "TAS1699854600504660_337FC34BE4304E14A193F6A2793AD9D1",
                    "name": "Task 2",
                    "point": 30,
                    "updated_at": "2021-01-01T00:00:00+00:00",
                    "created_at": "2021-01-01T00:00:00+00:00",
                    "links": {
                        "self": "/api/v1/tasks/TAS1699854600504660_337FC34BE4304E14A193F6A2793AD9D1"
                    },
                },
            ]
        ],
    )


## Tasks


__all__ = ["TaskBasePM", "TaskInPM", "TaskPM", "ResTaskPM", "ResTasksPM"]
