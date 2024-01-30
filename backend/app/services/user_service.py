#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random

from fastapi import Request
from sqlalchemy import Select

from backend.app.common.exception import errors
from backend.app.common.jwt import get_token, password_verify, superuser_verify
from backend.app.common.redis import redis_client
from backend.app.core.conf import settings
from backend.app.crud.crud_dept import dept_dao
from backend.app.crud.crud_role import role_dao
from backend.app.crud.crud_user import user_dao
from backend.app.database.db_mysql import async_db_session
from backend.app.models import User
from backend.app.schemas.user import (
    AddUserParam,
    AvatarParam,
    RegisterUserParam,
    ResetPasswordParam,
    UpdateUserParam,
    UpdateUserRoleParam,
)


class UserService:
    @staticmethod
    async def register(*, obj: RegisterUserParam) -> None:
        async with async_db_session.begin() as db:
            username = await user_dao.get_by_username(db, obj.username)
            if username:
                raise errors.ForbiddenError(msg="해당 사용자 이름은 이미 등록되었습니다")
            obj.nickname = (
                obj.nickname
                if obj.nickname
                else f"사용자{random.randrange(10000, 99999)}"
            )
            nickname = await user_dao.get_by_nickname(db, obj.nickname)
            if nickname:
                raise errors.ForbiddenError(msg="닉네임은 이미 등록되었습니다")
            email = await user_dao.check_email(db, obj.email)
            if email:
                raise errors.ForbiddenError(msg="해당 이메일은 이미 등록되었습니다")
            await user_dao.create(db, obj)

    @staticmethod
    async def add(*, request: Request, obj: AddUserParam) -> None:
        async with async_db_session.begin() as db:
            await superuser_verify(request)
            username = await user_dao.get_by_username(db, obj.username)
            if username:
                raise errors.ForbiddenError(msg="해당 사용자 이름은 이미 등록되었습니다")
            obj.nickname = (
                obj.nickname
                if obj.nickname
                else f"사용자{random.randrange(10000, 99999)}"
            )
            nickname = await user_dao.get_by_nickname(db, obj.nickname)
            if nickname:
                raise errors.ForbiddenError(msg="닉네임은 이미 등록되었습니다")
            dept = await dept_dao.get(db, obj.dept_id)
            if not dept:
                raise errors.NotFoundError(msg="부서가 존재하지 않습니다")
            for role_id in obj.roles:
                role = await role_dao.get(db, role_id)
                if not role:
                    raise errors.NotFoundError(msg="역할이 존재하지 않습니다")
            email = await user_dao.check_email(db, obj.email)
            if email:
                raise errors.ForbiddenError(msg="해당 이메일은 이미 등록되었습니다")
            await user_dao.add(db, obj)

    @staticmethod
    async def pwd_reset(*, request: Request, obj: ResetPasswordParam) -> int:
        async with async_db_session.begin() as db:
            op = obj.old_password
            if not await password_verify(op + request.user.salt, request.user.password):
                raise errors.ForbiddenError(msg="기존 비밀번호가 잘못되었습니다")
            np1 = obj.new_password
            np2 = obj.confirm_password
            if np1 != np2:
                raise errors.ForbiddenError(msg="두 비밀번호가 일치하지 않습니다")
            count = await user_dao.reset_password(
                db, request.user.id, obj.new_password, request.user.salt
            )
            prefix = [
                f"{settings.TOKEN_REDIS_PREFIX}:{request.user.id}:",
                f"{settings.TOKEN_REFRESH_REDIS_PREFIX}:{request.user.id}:",
            ]
            for i in prefix:
                await redis_client.delete_prefix(i)
            return count

    @staticmethod
    async def get_userinfo(*, username: str) -> User:
        async with async_db_session() as db:
            user = await user_dao.get_with_relation(db, username=username)
            if not user:
                raise errors.NotFoundError(msg="사용자가 존재하지 않습니다")
            return user

    @staticmethod
    async def update(*, request: Request, username: str, obj: UpdateUserParam) -> int:
        async with async_db_session.begin() as db:
            if not request.user.is_superuser:
                if request.user.username != username:
                    raise errors.ForbiddenError(msg="자신의 정보만 수정할 수 있습니다")
            input_user = await user_dao.get_with_relation(db, username=username)
            if not input_user:
                raise errors.NotFoundError(msg="사용자가 존재하지 않습니다")
            if input_user.username != obj.username:
                _username = await user_dao.get_by_username(db, obj.username)
                if _username:
                    raise errors.ForbiddenError(msg="해당 사용자 이름은 이미 존재합니다")
            if input_user.nickname != obj.nickname:
                nickname = await user_dao.get_by_nickname(db, obj.nickname)
                if nickname:
                    raise errors.ForbiddenError(msg="해당 닉네임은 이미 존재합니다")
            if input_user.email != obj.email:
                email = await user_dao.check_email(db, obj.email)
                if email:
                    raise errors.ForbiddenError(msg="해당 이메일은 이미 등록되었습니다")
            count = await user_dao.update_userinfo(db, input_user, obj)
            return count

    @staticmethod
    async def update_roles(
        *, request: Request, username: str, obj: UpdateUserRoleParam
    ) -> None:
        async with async_db_session.begin() as db:
            if not request.user.is_superuser:
                if request.user.username != username:
                    raise errors.ForbiddenError(msg="자신의 역할만 수정할 수 있습니다")
            input_user = await user_dao.get_with_relation(db, username=username)
            if not input_user:
                raise errors.NotFoundError(msg="사용자가 존재하지 않습니다")
            for role_id in obj.roles:
                role = await role_dao.get(db, role_id)
                if not role:
                    raise errors.NotFoundError(msg="역할이 존재하지 않습니다")
            await user_dao.update_role(db, input_user, obj)
            await redis_client.delete_prefix(
                f"{settings.PERMISSION_REDIS_PREFIX}:{request.user.uuid}"
            )

    @staticmethod
    async def update_avatar(
        *, request: Request, username: str, avatar: AvatarParam
    ) -> int:
        async with async_db_session.begin() as db:
            if not request.user.is_superuser:
                if request.user.username != username:
                    raise errors.ForbiddenError(msg="자신의 아바타만 수정할 수 있습니다")
            input_user = await user_dao.get_by_username(db, username)
            if not input_user:
                raise errors.NotFoundError(msg="사용자가 존재하지 않습니다")
            count = await user_dao.update_avatar(db, input_user, avatar)
            return count

    @staticmethod
    async def get_select(
        *, dept: int, username: str = None, phone: str = None, status: int = None
    ) -> Select:
        return await user_dao.get_all(
            dept=dept, username=username, phone=phone, status=status
        )

    @staticmethod
    async def update_permission(*, request: Request, pk: int) -> int:
        async with async_db_session.begin() as db:
            await superuser_verify(request)
            if not await user_dao.get(db, pk):
                raise errors.NotFoundError(msg="사용자가 존재하지 않습니다")
            else:
                if pk == request.user.id:
                    raise errors.ForbiddenError(msg="자체 관리자 권한을 수정할 수 없습니다")
                count = await user_dao.set_super(db, pk)
                return count

    @staticmethod
    async def update_staff(*, request: Request, pk: int) -> int:
        async with async_db_session.begin() as db:
            await superuser_verify(request)
            if not await user_dao.get(db, pk):
                raise errors.NotFoundError(msg="사용자가 존재하지 않습니다")
            else:
                if pk == request.user.id:
                    raise errors.ForbiddenError(msg="자체 백엔드 관리 로그인 권한을 수정할 수 없습니다")
                count = await user_dao.set_staff(db, pk)
                return count

    @staticmethod
    async def update_status(*, request: Request, pk: int) -> int:
        """
        pk: user_id
        """
        async with async_db_session.begin() as db:
            await superuser_verify(request)
            if not await user_dao.get(db, pk):
                raise errors.NotFoundError(msg="사용자가 존재하지 않습니다")
            else:
                if pk == request.user.id:
                    raise errors.ForbiddenError(msg="자체 상태를 수정할 수 없습니다")
                count = await user_dao.set_status(db, pk)
                return count

    @staticmethod
    async def update_multi_login(*, request: Request, pk: int) -> int:
        async with async_db_session.begin() as db:
            await superuser_verify(request)
            if not await user_dao.get(db, pk):
                raise errors.NotFoundError(msg="사용자가 존재하지 않습니다")
            else:
                count = await user_dao.set_multi_login(db, pk)
                token = await get_token(request)
                user_id = request.user.id
                latest_multi_login = await user_dao.get_multi_login(db, pk)
                # TODO: 사용자 refresh token 삭제, 이 작업은 매개변수가 필요하며 일단 구현하지 않음
                # 현재 사용자가 자신을 수정할 때 (일반 / 슈퍼), 현재 토큰 이외의 다른 토큰은 모두 무효화됩니다.
                if pk == user_id:
                    if not latest_multi_login:
                        prefix = f"{settings.TOKEN_REDIS_PREFIX}:{pk}:"
                        await redis_client.delete_prefix(prefix, exclude=prefix + token)
                # 슈퍼 사용자가 다른 사람을 수정할 때, 다른 사람의 토큰은 모두 무효화됩니다.
                else:
                    if not latest_multi_login:
                        prefix = f"{settings.TOKEN_REDIS_PREFIX}:{pk}:"
                        await redis_client.delete_prefix(prefix)
                return count

    @staticmethod
    async def delete(*, username: str) -> int:
        async with async_db_session.begin() as db:
            input_user = await user_dao.get_by_username(db, username)
            if not input_user:
                raise errors.NotFoundError(msg="사용자가 존재하지 않습니다.")
            count = await user_dao.delete(db, input_user.id)
            prefix = [
                f"{settings.TOKEN_REDIS_PREFIX}:{input_user.id}:",
                f"{settings.TOKEN_REFRESH_REDIS_PREFIX}:{input_user.id}:",
            ]
            for i in prefix:
                await redis_client.delete_prefix(i)
            return count


user_service: UserService = UserService()

