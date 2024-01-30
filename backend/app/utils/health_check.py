#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from math import ceil

from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute

from backend.app.common.exception import errors


def ensure_unique_route_names(app: FastAPI) -> None:
    """
    라우트 이름이 고유한지 확인합니다.

    :param app:
    :return:
    """
    temp_routes = set()
    for route in app.routes:
        if isinstance(route, APIRoute):
            if route.name in temp_routes:
                raise ValueError(f"라우트 이름이 고유하지 않습니다: {route.name}")
            temp_routes.add(route.name)


async def http_limit_callback(request: Request, response: Response, expire: int):
    """
    요청 제한 시의 기본 콜백 함수

    :param request:
    :param response:
    :param expire: 남은 밀리초
    :return:
    """
    expires = ceil(expire / 1000)
    raise errors.HTTPError(
        code=429,
        msg="요청이 너무 빈번합니다. 잠시 후에 다시 시도하세요.",
        headers={"Retry-After": str(expires)},
    )
