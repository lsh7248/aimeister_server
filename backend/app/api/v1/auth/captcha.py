#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fast_captcha import img_captcha
from fastapi import APIRouter, Depends, Request
from fastapi_limiter.depends import RateLimiter
from starlette.concurrency import run_in_threadpool

from backend.app.common.redis import redis_client
from backend.app.common.response.response_schema import ResponseModel, response_base
from backend.app.core.conf import settings

router = APIRouter()


@router.get(
    "/captcha",
    summary="로그인 인증 코드 가져오기",
    dependencies=[Depends(RateLimiter(times=5, seconds=10))],
)
async def get_captcha(request: Request) -> ResponseModel:
    """
    이 인터페이스는 성능 손실이 있을 수 있으며, 비동기 인터페이스이지만, 인증 코드 생성은 IO 집약적인 작업이므로 성능 손실을 최소화하기 위해 스레드 풀을 사용합니다.
    """
    img_type: str = "base64"
    img, code = await run_in_threadpool(img_captcha, img_byte=img_type)
    ip = request.state.ip
    await redis_client.set(
        f"{settings.CAPTCHA_LOGIN_REDIS_PREFIX}:{ip}",
        code,
        ex=settings.CAPTCHA_LOGIN_EXPIRE_SECONDS,
    )
    return await response_base.success(data={"image_type": img_type, "image": img})
