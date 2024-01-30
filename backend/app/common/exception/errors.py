#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
전역 비즈니스 예외 클래스

비즈니스 코드 실행 도중에 내부 오류를 발생시키기 위해 raise xxxError를 사용할 수 있으며, 이는 가능한 한 백그라운드 작업을 수반하는 예외를 구현하지만, **사용자 정의 응답 상태 코드**에는 적용되지 않습니다.
**사용자 정의 응답 상태 코드**를 사용해야 하는 경우 return await response_base.fail(res=CustomResponseCode.xxx)를 통해 직접 반환할 수 있습니다.
"""  # noqa: E501
from typing import Any

from fastapi import HTTPException
from starlette.background import BackgroundTask

from backend.app.common.response.response_code import (
    CustomErrorCode,
    StandardResponseCode,
)


class BaseExceptionMixin(Exception):
    code: int

    def __init__(
        self,
        *,
        msg: str = None,
        data: Any = None,
        background: BackgroundTask | None = None
    ):
        self.msg = msg
        self.data = data
        # The original background task: https://www.starlette.io/background/
        self.background = background


class HTTPError(HTTPException):
    def __init__(
        self, *, code: int, msg: Any = None, headers: dict[str, Any] | None = None
    ):
        super().__init__(status_code=code, detail=msg, headers=headers)


class CustomError(BaseExceptionMixin):
    def __init__(
        self,
        *,
        error: CustomErrorCode,
        data: Any = None,
        background: BackgroundTask | None = None
    ):
        self.code = error.code
        super().__init__(msg=error.msg, data=data, background=background)


class RequestError(BaseExceptionMixin):
    code = StandardResponseCode.HTTP_400

    def __init__(
        self,
        *,
        msg: str = "Bad Request",
        data: Any = None,
        background: BackgroundTask | None = None
    ):
        super().__init__(msg=msg, data=data, background=background)


class ForbiddenError(BaseExceptionMixin):
    code = StandardResponseCode.HTTP_403

    def __init__(
        self,
        *,
        msg: str = "Forbidden",
        data: Any = None,
        background: BackgroundTask | None = None
    ):
        super().__init__(msg=msg, data=data, background=background)


class NotFoundError(BaseExceptionMixin):
    code = StandardResponseCode.HTTP_404

    def __init__(
        self,
        *,
        msg: str = "Not Found",
        data: Any = None,
        background: BackgroundTask | None = None
    ):
        super().__init__(msg=msg, data=data, background=background)


class ServerError(BaseExceptionMixin):
    code = StandardResponseCode.HTTP_500

    def __init__(
        self,
        *,
        msg: str = "Internal Server Error",
        data: Any = None,
        background: BackgroundTask | None = None
    ):
        super().__init__(msg=msg, data=data, background=background)


class GatewayError(BaseExceptionMixin):
    code = StandardResponseCode.HTTP_502

    def __init__(
        self,
        *,
        msg: str = "Bad Gateway",
        data: Any = None,
        background: BackgroundTask | None = None
    ):
        super().__init__(msg=msg, data=data, background=background)


class AuthorizationError(BaseExceptionMixin):
    code = StandardResponseCode.HTTP_401

    def __init__(
        self,
        *,
        msg: str = "Permission Denied",
        data: Any = None,
        background: BackgroundTask | None = None
    ):
        super().__init__(msg=msg, data=data, background=background)


class TokenError(HTTPError):
    code = StandardResponseCode.HTTP_401

    def __init__(
        self, *, msg: str = "Not Authenticated", headers: dict[str, Any] | None = None
    ):
        super().__init__(
            code=self.code, msg=msg, headers=headers or {"WWW-Authenticate": "Bearer"}
        )
