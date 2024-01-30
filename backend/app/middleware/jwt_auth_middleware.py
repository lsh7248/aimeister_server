#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any

from fastapi import Request, Response
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
)
from starlette.requests import HTTPConnection

from backend.app.common import jwt
from backend.app.common.exception.errors import TokenError
from backend.app.common.log import log
from backend.app.core.conf import settings
from backend.app.database.db_mysql import async_db_session
from backend.app.utils.serializers import MsgSpecJSONResponse


class _AuthenticationError(AuthenticationError):
    """내부 인증 오류를 재정의하는 클래스"""

    def __init__(
        self,
        *,
        code: int = None,
        msg: str = None,
        headers: dict[str, Any] | None = None
    ):
        self.code = code
        self.msg = msg
        self.headers = headers


class JwtAuthMiddleware(AuthenticationBackend):
    """JWT 인증 미들웨어"""

    @staticmethod
    def auth_exception_handler(
        conn: HTTPConnection, exc: _AuthenticationError
    ) -> Response:
        """내부 인증 오류 처리를 덮어쓰는 함수"""
        return MsgSpecJSONResponse(
            content={"code": exc.code, "msg": exc.msg, "data": None},
            status_code=exc.code,
        )

    async def authenticate(self, request: Request):
        auth = request.headers.get("Authorization")
        if not auth:
            return

        if request.url.path in settings.TOKEN_EXCLUDE:
            return

        scheme, token = auth.split()
        if scheme.lower() != "bearer":
            return

        try:
            sub = await jwt.jwt_authentication(token)
            async with async_db_session() as db:
                user = await jwt.get_current_user(db, data=sub)
        except TokenError as exc:
            raise _AuthenticationError(
                code=exc.code, msg=exc.detail, headers=exc.headers
            )
        except Exception as e:
            log.exception(e)
            raise _AuthenticationError(
                code=getattr(e, "code", 500),
                msg=getattr(e, "msg", "Internal Server Error"),
            )

        # 이 반환은 표준 모드를 사용하지 않기 때문에 인증이 통과되면 일부 표준 기능이 손실됩니다.
        # 표준 반환 모드는 여기를 참조하세요: https://www.starlette.io/authentication/
        return AuthCredentials(["authenticated"]), user
