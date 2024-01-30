#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pydantic import ConfigDict, Field

from backend.app.common.enums import MethodType
from backend.app.schemas.base import SchemaBase


class CreatePolicyParam(SchemaBase):
    sub: str = Field(..., description="사용자 UUID / 역할 ID")
    path: str = Field(..., description="API 경로")
    method: MethodType = Field(default=MethodType.GET, description="요청 메서드")


class UpdatePolicyParam(CreatePolicyParam):
    pass


class DeletePolicyParam(CreatePolicyParam):
    pass


class DeleteAllPoliciesParam(SchemaBase):
    uuid: str | None = None
    role: str


class CreateUserRoleParam(SchemaBase):
    uuid: str = Field(..., description="사용자 UUID")
    role: str = Field(..., description="역할")


class DeleteUserRoleParam(CreateUserRoleParam):
    pass


class GetPolicyListDetails(SchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ptype: str = Field(..., description="규칙 유형, p / g")
    v0: str = Field(..., description="사용자 UUID / 역할")
    v1: str = Field(..., description="API 경로 / 역할")
    v2: str | None = None
    v3: str | None = None
    v4: str | None = None
    v5: str | None = None
