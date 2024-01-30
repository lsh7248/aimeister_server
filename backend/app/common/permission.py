#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import Request

from backend.app.common.exception.errors import ServerError
from backend.app.core.conf import settings


class RequestPermission:
    """
    요청 권한, 역할 메뉴 RBAC에만 사용됩니다.

    팁:
        이 요청 권한을 사용할 때는 `Depends(RequestPermission('xxx'))`을 `DependsRBAC` 이전에 설정해야합니다.
        fastapi의 현재 버전에서는 인터페이스 종속성 주입이 순차적으로 실행되므로 RBAC 식별자가 검증 전에 설정됩니다.
    """

    def __init__(self, value: str):
        self.value = value

    async def __call__(self, request: Request):
        if settings.PERMISSION_MODE == "role-menu":
            if not isinstance(self.value, str):
                raise ServerError
            # 권한 식별자 추가
            request.state.permission = self.value
