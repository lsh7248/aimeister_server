#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import ConfigDict, Field

from backend.app.common.enums import MethodType
from backend.app.schemas.base import SchemaBase


class ApiSchemaBase(SchemaBase):
    name: str
    method: MethodType = Field(default=MethodType.GET, description="요청 방법")
    path: str = Field(..., description="api路径")
    remark: str | None = None


class CreateApiParam(ApiSchemaBase):
    pass


class UpdateApiParam(ApiSchemaBase):
    pass


class GetApiListDetails(ApiSchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
