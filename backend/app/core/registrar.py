#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi_pagination import add_pagination
from starlette.middleware.authentication import AuthenticationMiddleware

from backend.app.api.routers import v1
from backend.app.common.exception.exception_handler import register_exception
from backend.app.common.redis import redis_client
from backend.app.core.conf import settings
from backend.app.database.db_mysql import create_table
from backend.app.middleware.jwt_auth_middleware import JwtAuthMiddleware
from backend.app.middleware.opera_log_middleware import OperaLogMiddleware
from backend.app.utils.demo_site import demo_site
from backend.app.utils.health_check import (
    ensure_unique_route_names,
    http_limit_callback,
)
from backend.app.utils.openapi import simplify_operation_ids
from backend.app.utils.serializers import MsgSpecJSONResponse


@asynccontextmanager
async def register_init(app: FastAPI):
    """
    초기화 시작

    :return:
    """
    # 데이터베이스 테이블 생성
    await create_table()
    # Redis에 연결
    await redis_client.open()
    # 리미터 초기화
    await FastAPILimiter.init(
        redis_client,
        prefix=settings.LIMITER_REDIS_PREFIX,
        http_callback=http_limit_callback,
    )

    yield

    # Redis 연결 종료
    await redis_client.close()
    # 리미터 종료
    await FastAPILimiter.close()


def register_app():
    # FastAPI
    app = FastAPI(
        title=settings.TITLE,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOCS_URL,
        openapi_url=settings.OPENAPI_URL,
        default_response_class=MsgSpecJSONResponse,
        lifespan=register_init,
    )

    # 정적 파일
    register_static_file(app)

    # 미들웨어
    register_middleware(app)

    # 라우터
    register_router(app)

    # 페이지네이션
    register_page(app)

    # 전역 예외 처리
    register_exception(app)

    return app


def register_static_file(app: FastAPI):
    """
    정적 파일 개발 모드, 프로덕션에서는 Nginx 정적 리소스 서비스 사용

    :param app:
    :return:
    """
    if settings.STATIC_FILES:
        import os

        from fastapi.staticfiles import StaticFiles

        if not os.path.exists("./static"):
            os.mkdir("./static")
        app.mount("/static", StaticFiles(directory="static"), name="static")


def register_middleware(app: FastAPI):
    """
    미들웨어, 아래에서 위로 실행

    :param app:
    :return:
    """
    # Gzip: 항상 가장 위에
    if settings.MIDDLEWARE_GZIP:
        from fastapi.middleware.gzip import GZipMiddleware

        app.add_middleware(GZipMiddleware)
    # Opera 로그
    app.add_middleware(OperaLogMiddleware)
    # JWT 인증, 필수
    app.add_middleware(
        AuthenticationMiddleware,
        backend=JwtAuthMiddleware(),
        on_error=JwtAuthMiddleware.auth_exception_handler,
    )
    # 접근 로그
    if settings.MIDDLEWARE_ACCESS:
        from backend.app.middleware.access_middleware import AccessMiddleware

        app.add_middleware(AccessMiddleware)
    # CORS: 항상 가장 아래에
    if settings.MIDDLEWARE_CORS:
        from fastapi.middleware.cors import CORSMiddleware

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


def register_router(app: FastAPI):
    """
    라우터

    :param app: FastAPI
    :return:
    """
    dependencies = [Depends(demo_site)] if settings.DEMO_MODE else None

    # API
    app.include_router(v1, dependencies=dependencies)

    # 추가
    ensure_unique_route_names(app)
    simplify_operation_ids(app)


def register_page(app: FastAPI):
    """
    페이지네이션 쿼리

    :param app:
    :return:
    """
    add_pagination(app)
