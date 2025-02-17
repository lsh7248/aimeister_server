#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import ConfigDict, Field

from backend.app.common.enums import StatusType
from backend.app.schemas.base import CustomEmailStr, CustomPhoneNumber, SchemaBase


class DeptSchemaBase(SchemaBase):
    name: str
    parent_id: int | None = Field(default=None, description="부서 상위 ID")
    sort: int = Field(default=0, ge=0, description="정렬")
    leader: str | None = None
    phone: CustomPhoneNumber | None = None
    email: CustomEmailStr | None = None
    status: StatusType = Field(default=StatusType.enable)


class CreateDeptParam(DeptSchemaBase):
    pass


class UpdateDeptParam(DeptSchemaBase):
    pass


class GetDeptListDetails(DeptSchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    del_flag: bool
    created_time: datetime
    updated_time: datetime | None = None
