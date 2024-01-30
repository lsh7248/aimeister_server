#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import ConfigDict, Field

from backend.app.common.enums import RoleDataScopeType, StatusType
from backend.app.schemas.base import SchemaBase
from backend.app.schemas.menu import GetMenuListDetails


class RoleSchemaBase(SchemaBase):
    name: str
    data_scope: RoleDataScopeType = Field(
        default=RoleDataScopeType.custom,
        description="권한 범위 (1 : 전체 데이터 권한, 2 : 사용자 정의 데이터 권한)",
    )
    status: StatusType = Field(default=StatusType.enable)
    remark: str | None = None


class CreateRoleParam(RoleSchemaBase):
    pass


class UpdateRoleParam(RoleSchemaBase):
    pass


class UpdateRoleMenuParam(SchemaBase):
    menus: list[int]


class GetRoleListDetails(RoleSchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
    menus: list[GetMenuListDetails]
