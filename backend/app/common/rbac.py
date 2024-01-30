#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import casbin
import casbin_async_sqlalchemy_adapter

from fastapi import Depends, Request

from backend.app.common.enums import MethodType, StatusType
from backend.app.common.exception.errors import AuthorizationError, TokenError
from backend.app.common.jwt import DependsJwtAuth
from backend.app.common.redis import redis_client
from backend.app.core.conf import settings
from backend.app.database.db_mysql import async_engine
from backend.app.models import CasbinRule


class RBAC:
    @staticmethod
    async def enforcer() -> casbin.AsyncEnforcer:
        """
        casbin 실행기 가져오기

        :return:
        """
        # 규칙 데이터는 메서드 내에서 직접 정의됨
        _CASBIN_RBAC_MODEL_CONF_TEXT = """
        [request_definition]
        r = sub, obj, act

        [policy_definition]
        p = sub, obj, act

        [role_definition]
        g = _, _

        [policy_effect]
        e = some(where (p.eft == allow))

        [matchers]
        m = g(r.sub, p.sub) && (keyMatch(r.obj, p.obj) || keyMatch3(r.obj, p.obj)) && (r.act == p.act || p.act == "*")
        """
        adapter = casbin_async_sqlalchemy_adapter.Adapter(
            async_engine, db_class=CasbinRule
        )
        model = casbin.AsyncEnforcer.new_model(text=_CASBIN_RBAC_MODEL_CONF_TEXT)
        enforcer = casbin.AsyncEnforcer(model, adapter)
        await enforcer.load_policy()
        return enforcer

    async def rbac_verify(self, request: Request, _token: str = DependsJwtAuth) -> None:
        """
        RBAC 권한 검증

        :param request:
        :param _token:
        :return:
        """
        path = request.url.path
        # 인증 예외 목록
        if path in settings.TOKEN_EXCLUDE:
            return
        # JWT 인증 상태 강제 검증
        if not request.auth.scopes:
            raise TokenError
        # 슈퍼 관리자는 검증하지 않음
        if request.user.is_superuser:
            return
        # 역할 데이터 권한 범위 확인
        user_roles = request.user.roles
        if not user_roles:
            raise AuthorizationError(
                msg="사용자에게 역할이 할당되지 않았습니다. 권한 부여 실패"
            )
        if not any(len(role.menus) > 0 for role in user_roles):
            raise AuthorizationError(
                msg="사용자의 역할에 메뉴가 할당되지 않았습니다. 권한 부여 실패"
            )
        method = request.method
        if method != MethodType.GET or method != MethodType.OPTIONS:
            if not request.user.is_staff:
                raise AuthorizationError(
                    msg="이 사용자는 백엔드 관리 작업이 금지되었습니다."
                )
        # 데이터 권한 범위
        data_scope = any(role.data_scope == 1 for role in user_roles)
        if data_scope:
            return
        user_uuid = request.user.uuid
        path_auth_perm = request.state.permission
        if settings.PERMISSION_MODE == "role-menu":
            # 역할 메뉴 권한 검증
            if path_auth_perm in set(settings.ROLE_MENU_EXCLUDE):
                return
            user_menu_perms = await redis_client.get(
                f"{settings.PERMISSION_REDIS_PREFIX}:{user_uuid}:enable"
            )
            user_forbid_menu_perms = await redis_client.get(
                f"{settings.PERMISSION_REDIS_PREFIX}:{user_uuid}:disable"
            )
            if not user_menu_perms or not user_forbid_menu_perms:
                user_menu_perms = []
                user_forbid_menu_perms = []
                for role in user_roles:
                    user_menus = role.menus
                    if user_menus:
                        for menu in user_menus:
                            perms = menu.perms
                            if perms:
                                if menu.status == StatusType.enable:
                                    user_menu_perms.extend(perms.split(","))
                                else:
                                    user_forbid_menu_perms.extend(perms.split(","))
                await redis_client.set(
                    f"{settings.PERMISSION_REDIS_PREFIX}:{user_uuid}:enable",
                    ",".join(user_menu_perms),
                )
                await redis_client.set(
                    f"{settings.PERMISSION_REDIS_PREFIX}:{user_uuid}:disable",
                    ",".join(user_forbid_menu_perms),
                )
            if path_auth_perm in user_forbid_menu_perms:
                raise AuthorizationError(
                    msg="메뉴가 비활성화되었습니다. 권한 부여 실패"
                )
            if path_auth_perm not in user_menu_perms:
                raise AuthorizationError
        else:
            # casbin 권한 검증
            user_forbid_menu_perms = await redis_client.get(
                f"{settings.PERMISSION_REDIS_PREFIX}:{request.user.uuid}:disable"
            )
            if not user_forbid_menu_perms:
                user_forbid_menu_perms = []
                for role in user_roles:
                    user_menus = role.menus
                    if user_menus:
                        for menu in user_menus:
                            perms = menu.perms
                            if perms:
                                if menu.status == StatusType.disable:
                                    user_forbid_menu_perms.extend(perms.split(","))
                await redis_client.set(
                    f"{settings.PERMISSION_REDIS_PREFIX}:{user_uuid}:disable",
                    ",".join(user_forbid_menu_perms),
                )
            if path_auth_perm in user_forbid_menu_perms:
                raise AuthorizationError(
                    msg="메뉴가 비활성화되었습니다. 권한 부여 실패"
                )
            if (method, path) in settings.CASBIN_EXCLUDE:
                return
            enforcer = await self.enforcer()
            if not enforcer.enforce(user_uuid, path, method):
                raise AuthorizationError


rbac = RBAC()
# RBAC 권한 주입
DependsRBAC = Depends(rbac.rbac_verify)
