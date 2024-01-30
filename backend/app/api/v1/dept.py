#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.common.jwt import DependsJwtAuth
from backend.app.common.permission import RequestPermission
from backend.app.common.rbac import DependsRBAC
from backend.app.common.response.response_schema import ResponseModel, response_base
from backend.app.schemas.dept import (
    CreateDeptParam,
    GetDeptListDetails,
    UpdateDeptParam,
)
from backend.app.services.dept_service import dept_service
from backend.app.utils.serializers import select_as_dict

router = APIRouter()


@router.get("/{pk}", summary="부서 상세 정보 가져오기", dependencies=[DependsJwtAuth])
async def get_dept(pk: Annotated[int, Path(...)]) -> ResponseModel:
    dept = await dept_service.get(pk=pk)
    data = GetDeptListDetails(**await select_as_dict(dept))
    return await response_base.success(data=data)


@router.get("", summary="모든 부서 트리 가져오기", dependencies=[DependsJwtAuth])
async def get_all_depts_tree(
    name: Annotated[str | None, Query()] = None,
    leader: Annotated[str | None, Query()] = None,
    phone: Annotated[str | None, Query()] = None,
    status: Annotated[int | None, Query()] = None,
) -> ResponseModel:
    dept = await dept_service.get_dept_tree(
        name=name, leader=leader, phone=phone, status=status
    )
    return await response_base.success(data=dept)


@router.post(
    "",
    summary="부서 생성",
    dependencies=[
        Depends(RequestPermission("sys:dept:add")),
        DependsRBAC,
    ],
)
async def create_dept(obj: CreateDeptParam) -> ResponseModel:
    await dept_service.create(obj=obj)
    return await response_base.success()


@router.put(
    "/{pk}",
    summary="부서 수정",
    dependencies=[
        Depends(RequestPermission("sys:dept:edit")),
        DependsRBAC,
    ],
)
async def update_dept(
    pk: Annotated[int, Path(...)], obj: UpdateDeptParam
) -> ResponseModel:
    count = await dept_service.update(pk=pk, obj=obj)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()


@router.delete(
    "/{pk}",
    summary="부서 삭제",
    dependencies=[
        Depends(RequestPermission("sys:dept:del")),
        DependsRBAC,
    ],
)
async def delete_dept(pk: Annotated[int, Path(...)]) -> ResponseModel:
    count = await dept_service.delete(pk=pk)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()
