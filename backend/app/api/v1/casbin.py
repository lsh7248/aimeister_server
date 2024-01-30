#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from backend.app.common.jwt import DependsJwtAuth
from backend.app.common.pagination import DependsPagination, paging_data
from backend.app.common.permission import RequestPermission
from backend.app.common.rbac import DependsRBAC
from backend.app.common.response.response_schema import ResponseModel, response_base
from backend.app.database.db_mysql import CurrentSession
from backend.app.schemas.casbin_rule import (
    CreatePolicyParam,
    CreateUserRoleParam,
    DeleteAllPoliciesParam,
    DeletePolicyParam,
    DeleteUserRoleParam,
    GetPolicyListDetails,
    UpdatePolicyParam,
)
from backend.app.services.casbin_service import casbin_service

router = APIRouter()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from backend.app.common.jwt import DependsJwtAuth
from backend.app.common.pagination import DependsPagination, paging_data
from backend.app.common.permission import RequestPermission
from backend.app.common.rbac import DependsRBAC
from backend.app.common.response.response_schema import ResponseModel, response_base
from backend.app.database.db_mysql import CurrentSession
from backend.app.schemas.casbin_rule import (
    CreatePolicyParam,
    CreateUserRoleParam,
    DeleteAllPoliciesParam,
    DeletePolicyParam,
    DeleteUserRoleParam,
    GetPolicyListDetails,
    UpdatePolicyParam,
)
from backend.app.services.casbin_service import casbin_service

router = APIRouter()


@router.get(
    "",
    summary="（흐린 조건）페이징으로 모든 권한 규칙 가져오기",
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_casbin(
    db: CurrentSession,
    ptype: Annotated[str | None, Query(description="규칙 유형, p / g")] = None,
    sub: Annotated[str | None, Query(description="사용자 uuid / 역할")] = None,
) -> ResponseModel:
    casbin_select = await casbin_service.get_casbin_list(ptype=ptype, sub=sub)
    page_data = await paging_data(db, casbin_select, GetPolicyListDetails)
    return await response_base.success(data=page_data)


@router.get(
    "/policies", summary="모든 P 권한 규칙 가져오기", dependencies=[DependsJwtAuth]
)
async def get_all_policies(
    role: Annotated[int | None, Query(description="역할 ID")] = None
) -> ResponseModel:
    policies = await casbin_service.get_policy_list(role=role)
    return await response_base.success(data=policies)


@router.post(
    "/policy",
    summary="P 권한 규칙 추가",
    dependencies=[
        Depends(RequestPermission("casbin:p:add")),
        DependsRBAC,
    ],
)
async def create_policy(p: CreatePolicyParam) -> ResponseModel:
    """
    p 규칙:

    - 역할 기반의 액세스 권한을 권장하며, 액세스 권한을 실제로 가지려면 g 규칙을 추가해야합니다. 전역 인터페이스 액세스 정책 구성에 적합합니다.
    **형식**: 역할 role + 액세스 경로 path + 액세스 방법 method

    - 사용자 기반의 액세스 권한을 추가하는 경우 g 규칙을 추가할 필요가 없으며, 특정 사용자 인터페이스 액세스 정책 구성에 적합합니다.
    **형식**: 사용자 uuid + 액세스 경로 path + 액세스 방법 method
    """
    data = await casbin_service.create_policy(p=p)
    return await response_base.success(data=data)


@router.post(
    "/policies",
    summary="다중 그룹 P 권한 규칙 추가",
    dependencies=[
        Depends(RequestPermission("casbin:p:group:add")),
        DependsRBAC,
    ],
)
async def create_policies(ps: list[CreatePolicyParam]) -> ResponseModel:
    data = await casbin_service.create_policies(ps=ps)
    return await response_base.success(data=data)


@router.put(
    "/policy",
    summary="P 권한 규칙 업데이트",
    dependencies=[
        Depends(RequestPermission("casbin:p:edit")),
        DependsRBAC,
    ],
)
async def update_policy(
    old: UpdatePolicyParam, new: UpdatePolicyParam
) -> ResponseModel:
    data = await casbin_service.update_policy(old=old, new=new)
    return await response_base.success(data=data)


@router.put(
    "/policies",
    summary="다중 그룹 P 권한 규칙 업데이트",
    dependencies=[
        Depends(RequestPermission("casbin:p:group:edit")),
        DependsRBAC,
    ],
)
async def update_policies(
    old: list[UpdatePolicyParam], new: list[UpdatePolicyParam]
) -> ResponseModel:
    data = await casbin_service.update_policies(old=old, new=new)
    return await response_base.success(data=data)


@router.delete(
    "/policy",
    summary="P 권한 규칙 삭제",
    dependencies=[
        Depends(RequestPermission("casbin:p:del")),
        DependsRBAC,
    ],
)
async def delete_policy(p: DeletePolicyParam) -> ResponseModel:
    data = await casbin_service.delete_policy(p=p)
    return await response_base.success(data=data)


@router.delete(
    "/policies",
    summary="다중 그룹 P 권한 규칙 삭제",
    dependencies=[
        Depends(RequestPermission("casbin:p:group:del")),
        DependsRBAC,
    ],
)
async def delete_policies(ps: list[DeletePolicyParam]) -> ResponseModel:
    data = await casbin_service.delete_policies(ps=ps)
    return await response_base.success(data=data)


@router.delete(
    "/policies/all",
    summary="모든 P 권한 규칙 삭제",
    dependencies=[
        Depends(RequestPermission("casbin:p:empty")),
        DependsRBAC,
    ],
)
async def delete_all_policies(sub: DeleteAllPoliciesParam) -> ResponseModel:
    count = await casbin_service.delete_all_policies(sub=sub)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()


@router.get(
    "/groups", summary="모든 G 권한 규칙 가져오기", dependencies=[DependsJwtAuth]
)
async def get_all_groups() -> ResponseModel:
    data = await casbin_service.get_group_list()
    return await response_base.success(data=data)


@router.post(
    "/group",
    summary="G 권한 규칙 추가",
    dependencies=[
        Depends(RequestPermission("casbin:g:add")),
        DependsRBAC,
    ],
)
async def create_group(g: CreateUserRoleParam) -> ResponseModel:
    """
    g 규칙 (**p 규칙에 따라**):

    - 역할 기반의 액세스 권한이 p 규칙에 추가된 경우, 사용자 그룹 기반의 액세스 권한을 g 규칙에 추가해야 실제로 액세스 권한을 가질 수 있습니다.
    **형식**: 사용자 uuid + 역할 role

    - 사용자 기반의 액세스 권한이 p 규칙에 추가된 경우, 해당 g 규칙을 추가하지 않으면 직접 액세스 권한을 가집니다.
    그러나 가지고있는 것은 사용자 역할의 모든 권한이 아니라 단일로 추가 된 p 규칙에 해당하는 액세스 권한입니다.
    """
    data = await casbin_service.create_group(g=g)
    return await response_base.success(data=data)


@router.post(
    "/groups",
    summary="다중 그룹 G 권한 규칙 추가",
    dependencies=[
        Depends(RequestPermission("casbin:g:group:add")),
        DependsRBAC,
    ],
)
async def create_groups(gs: list[CreateUserRoleParam]) -> ResponseModel:
    data = await casbin_service.create_groups(gs=gs)
    return await response_base.success(data=data)


@router.delete(
    "/group",
    summary="G 권한 규칙 삭제",
    dependencies=[
        Depends(RequestPermission("casbin:g:del")),
        DependsRBAC,
    ],
)
async def delete_group(g: DeleteUserRoleParam) -> ResponseModel:
    data = await casbin_service.delete_group(g=g)
    return await response_base.success(data=data)


@router.delete(
    "/groups",
    summary="다중 그룹 G 권한 규칙 삭제",
    dependencies=[
        Depends(RequestPermission("casbin:g:group:del")),
        DependsRBAC,
    ],
)
async def delete_groups(gs: list[DeleteUserRoleParam]) -> ResponseModel:
    data = await casbin_service.delete_groups(gs=gs)
    return await response_base.success(data=data)


@router.delete(
    "/groups/all",
    summary="모든 G 권한 규칙 삭제",
    dependencies=[
        Depends(RequestPermission("casbin:g:empty")),
        DependsRBAC,
    ],
)
async def delete_all_groups(uuid: Annotated[UUID, Query(...)]) -> ResponseModel:
    count = await casbin_service.delete_all_groups(uuid=uuid)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()


async def delete_all_groups(uuid: Annotated[UUID, Query(...)]) -> ResponseModel:
    count = await casbin_service.delete_all_groups(uuid=uuid)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()
