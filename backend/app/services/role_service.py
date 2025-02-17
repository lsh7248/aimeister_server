#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Sequence

from fastapi import Request
from sqlalchemy import Select

from backend.app.common.exception import errors
from backend.app.common.redis import redis_client
from backend.app.core.conf import settings
from backend.app.crud.crud_menu import menu_dao
from backend.app.crud.crud_role import role_dao
from backend.app.database.db_mysql import async_db_session
from backend.app.models import Role
from backend.app.schemas.role import (
    CreateRoleParam,
    UpdateRoleMenuParam,
    UpdateRoleParam,
)


class RoleService:
    @staticmethod
    async def get(*, pk: int) -> Role:
        async with async_db_session() as db:
            role = await role_dao.get_with_relation(db, pk)
            if not role:
                raise errors.NotFoundError(msg="역할이 존재하지 않습니다")
            return role

    @staticmethod
    async def get_all() -> Sequence[Role]:
        async with async_db_session() as db:
            roles = await role_dao.get_all(db)
            return roles

    @staticmethod
    async def get_user_roles(*, pk: int) -> Sequence[Role]:
        async with async_db_session() as db:
            roles = await role_dao.get_user_all(db, user_id=pk)
            return roles

    @staticmethod
    async def get_select(
        *, name: str = None, data_scope: int = None, status: int = None
    ) -> Select:
        return await role_dao.get_list(name=name, data_scope=data_scope, status=status)

    @staticmethod
    async def create(*, obj: CreateRoleParam) -> None:
        async with async_db_session.begin() as db:
            role = await role_dao.get_by_name(db, obj.name)
            if role:
                raise errors.ForbiddenError(msg="역할이 이미 존재합니다.")
            await role_dao.create(db, obj)

    @staticmethod
    async def update(*, pk: int, obj: UpdateRoleParam) -> int:
        async with async_db_session.begin() as db:
            role = await role_dao.get(db, pk)
            if not role:
                raise errors.NotFoundError(msg="역할이 존재하지 않습니다")
            if role.name != obj.name:
                role = await role_dao.get_by_name(db, obj.name)
                if role:
                    raise errors.ForbiddenError(msg="역할이 이미 존재합니다.")
            count = await role_dao.update(db, pk, obj)
            return count

    @staticmethod
    async def update_role_menu(
        *, request: Request, pk: int, menu_ids: UpdateRoleMenuParam
    ) -> int:
        async with async_db_session.begin() as db:
            role = await role_dao.get(db, pk)
            if not role:
                raise errors.NotFoundError(msg="역할이 존재하지 않습니다")
            for menu_id in menu_ids.menus:
                menu = await menu_dao.get(db, menu_id)
                if not menu:
                    raise errors.NotFoundError(msg="메뉴가 존재하지 않습니다")
            count = await role_dao.update_menus(db, pk, menu_ids)
            await redis_client.delete_prefix(
                f"{settings.PERMISSION_REDIS_PREFIX}:{request.user.uuid}"
            )
            return count

    @staticmethod
    async def delete(*, pk: list[int]) -> int:
        async with async_db_session.begin() as db:
            count = await role_dao.delete(db, pk)
            return count


role_service: RoleService = RoleService()
