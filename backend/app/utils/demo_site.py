#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import Request

from backend.app.common.exception import errors
from backend.app.core.conf import settings


async def demo_site(request: Request):
    """데모 사이트"""

    method = request.method
    path = request.url.path
    if (
        settings.DEMO_MODE
        and method != "GET"
        and method != "OPTIONS"
        and (method, path) not in settings.DEMO_MODE_EXCLUDE
    ):
        raise errors.ForbiddenError(msg="이 작업은 데모 환경에서 금지되어 있습니다.")
