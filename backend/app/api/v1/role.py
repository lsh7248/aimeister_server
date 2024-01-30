#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request

from backend.app.common.jwt import DependsJwtAuth
from backend.app.common.pagination import DependsPagination, paging_data
from backend.app.common.permission import RequestPermission
from backend.app.common.rbac import DependsRBAC
from backend.app.common.response.response_schema import ResponseModel, response_base
from backend.app.database.db_mysql import CurrentSession
from backend.app.schemas.role import (
    CreateRoleParam,
    GetRoleListDetails,
    UpdateRoleMenuParam,
    UpdateRoleParam,
)
from backend.app.services.menu_service import menu_service
from backend.app.services.role_service import role_service
from backend.app.utils.serializers import select_as_dict, select_list_serialize

router = APIRouter()


@router.get("/all", summary="모든 역할 가져오기", dependencies=[DependsJwtAuth])
async def get_all_roles() -> ResponseModel:
    roles = await role_service.get_all()
    data = await select_list_serialize(roles)
    return await response_base.success(data=data)


@router.get(
    "/{pk}/all", summary="사용자의 모든 역할 가져오기", dependencies=[DependsJwtAuth]
)
async def get_user_all_roles(pk: Annotated[int, Path(...)]) -> ResponseModel:
    roles = await role_service.get_user_roles(pk=pk)
    data = await select_list_serialize(roles)
    return await response_base.success(data=data)


@router.get(
    "/{pk}/menus", summary="역할의 모든 메뉴 가져오기", dependencies=[DependsJwtAuth]
)
async def get_role_all_menus(pk: Annotated[int, Path(...)]) -> ResponseModel:
    menu = await menu_service.get_role_menu_tree(pk=pk)
    return await response_base.success(data=menu)


@router.get("/{pk}", summary="역할 세부 정보 가져오기", dependencies=[DependsJwtAuth])
async def get_role(pk: Annotated[int, Path(...)]) -> ResponseModel:
    role = await role_service.get(pk=pk)
    data = GetRoleListDetails(**await select_as_dict(role))
    return await response_base.success(data=data)


@router.get(
    "",
    summary="(키워드 조건) 페이징하여 모든 역할 가져오기",
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_roles(
    db: CurrentSession,
    name: Annotated[str | None, Query()] = None,
    data_scope: Annotated[int | None, Query()] = None,
    status: Annotated[int | None, Query()] = None,
) -> ResponseModel:
    role_select = await role_service.get_select(
        name=name, data_scope=data_scope, status=status
    )
    page_data = await paging_data(db, role_select, GetRoleListDetails)
    return await response_base.success(data=page_data)


@router.post(
    "",
    summary="역할 생성하기",
    dependencies=[
        Depends(RequestPermission("sys:role:add")),
        DependsRBAC,
    ],
)
async def create_role(obj: CreateRoleParam) -> ResponseModel:
    await role_service.create(obj=obj)
    return await response_base.success()


@router.put(
    "/{pk}",
    summary="역할 업데이트하기",
    dependencies=[
        Depends(RequestPermission("sys:role:edit")),
        DependsRBAC,
    ],
)
async def update_role(
    pk: Annotated[int, Path(...)], obj: UpdateRoleParam
) -> ResponseModel:
    count = await role_service.update(pk=pk, obj=obj)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()


@router.put(
    "/{pk}/menu",
    summary="역할 메뉴 업데이트하기",
    dependencies=[
        Depends(RequestPermission("sys:role:menu:edit")),
        DependsRBAC,
    ],
)
async def update_role_menus(
    request: Request, pk: Annotated[int, Path(...)], menu_ids: UpdateRoleMenuParam
) -> ResponseModel:
    count = await role_service.update_role_menu(
        request=request, pk=pk, menu_ids=menu_ids
    )
    if count > 0:
        return await response_base.success()
    return await response_base.fail()


@router.delete(
    "",
    summary="(일괄) 역할 삭제하기",
    dependencies=[
        Depends(RequestPermission("sys:role:del")),
        DependsRBAC,
    ],
)
async def delete_role(pk: Annotated[list[int], Query(...)]) -> ResponseModel:
    count = await role_service.delete(pk=pk)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()
