#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from asgiref.sync import sync_to_async
from fastapi import Depends, Request
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.common.exception.errors import AuthorizationError, TokenError
from backend.app.common.redis import redis_client
from backend.app.core.conf import settings
from backend.app.crud.crud_user import user_dao
from backend.app.models import User
from backend.app.utils.timezone import timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Deprecated, may be enabled when oauth2 is actually integrated
oauth2_schema = OAuth2PasswordBearer(tokenUrl=settings.TOKEN_URL_SWAGGER)

# JWT authorizes dependency injection
DependsJwtAuth = Depends(HTTPBearer())


@sync_to_async
def get_hash_password(password: str) -> str:
    """
    Encrypt passwords using the hash algorithm

    :param password:
    :return:
    """
    return pwd_context.hash(password)


@sync_to_async
def password_verify(plain_password: str, hashed_password: str) -> bool:
    """
    Password verification

    :param plain_password: The password to verify
    :param hashed_password: The hash ciphers to compare
    :return:
    """
    return pwd_context.verify(plain_password, hashed_password)


async def create_access_token(
    sub: str, expires_delta: timedelta | None = None, **kwargs
) -> tuple[str, datetime]:
    """
    Generate encryption token

    :param sub: The subject/userid of the JWT
    :param expires_delta: Increased expiry time
    :return:
    """
    if expires_delta:
        expire = timezone.now() + expires_delta
        expire_seconds = int(expires_delta.total_seconds())
    else:
        expire = timezone.now() + timedelta(seconds=settings.TOKEN_EXPIRE_SECONDS)
        expire_seconds = settings.TOKEN_EXPIRE_SECONDS
    multi_login = kwargs.pop("multi_login", None)
    to_encode = {"exp": expire, "sub": sub, **kwargs}
    token = jwt.encode(to_encode, settings.TOKEN_SECRET_KEY, settings.TOKEN_ALGORITHM)
    if multi_login is False:
        prefix = f"{settings.TOKEN_REDIS_PREFIX}:{sub}:"
        await redis_client.delete_prefix(prefix)
    key = f"{settings.TOKEN_REDIS_PREFIX}:{sub}:{token}"
    await redis_client.setex(key, expire_seconds, token)
    return token, expire


async def create_refresh_token(
    sub: str, expire_time: datetime | None = None, **kwargs
) -> tuple[str, datetime]:
    """
    Generate encryption refresh token, only used to create a new token

    :param sub: The subject/userid of the JWT
    :param expire_time: expiry time
    :return:
    """
    if expire_time:
        expire = expire_time + timedelta(seconds=settings.TOKEN_REFRESH_EXPIRE_SECONDS)
        expire_datetime = timezone.f_datetime(expire_time)
        current_datetime = timezone.now()
        if expire_datetime < current_datetime:
            raise TokenError(msg="Refresh Token 유효기간이 잘못되었습니다.")
        expire_seconds = int((expire_datetime - current_datetime).total_seconds())
    else:
        expire = timezone.now() + timedelta(seconds=settings.TOKEN_EXPIRE_SECONDS)
        expire_seconds = settings.TOKEN_REFRESH_EXPIRE_SECONDS
    multi_login = kwargs.pop("multi_login", None)
    to_encode = {"exp": expire, "sub": sub, **kwargs}
    refresh_token = jwt.encode(
        to_encode, settings.TOKEN_SECRET_KEY, settings.TOKEN_ALGORITHM
    )
    if multi_login is False:
        prefix = f"{settings.TOKEN_REFRESH_REDIS_PREFIX}:{sub}:"
        await redis_client.delete_prefix(prefix)
    key = f"{settings.TOKEN_REFRESH_REDIS_PREFIX}:{sub}:{refresh_token}"
    await redis_client.setex(key, expire_seconds, refresh_token)
    return refresh_token, expire


async def create_new_token(
    sub: str, token: str, refresh_token: str, **kwargs
) -> tuple[str, str, datetime, datetime]:
    """
    새 토큰 생성

    :param sub:
    :param token
    :param refresh_token:
    :return:
    """
    redis_refresh_token = await redis_client.get(
        f"{settings.TOKEN_REFRESH_REDIS_PREFIX}:{sub}:{refresh_token}"
    )
    if not redis_refresh_token or redis_refresh_token != refresh_token:
        raise TokenError(msg="리프레시 토큰이 만료되었습니다.")
    new_access_token, new_access_token_expire_time = await create_access_token(
        sub, **kwargs
    )
    new_refresh_token, new_refresh_token_expire_time = await create_refresh_token(
        sub, **kwargs
    )
    token_key = f"{settings.TOKEN_REDIS_PREFIX}:{sub}:{token}"
    refresh_token_key = f"{settings.TOKEN_REDIS_PREFIX}:{sub}:{refresh_token}"
    await redis_client.delete(token_key)
    await redis_client.delete(refresh_token_key)
    return (
        new_access_token,
        new_refresh_token,
        new_access_token_expire_time,
        new_refresh_token_expire_time,
    )


@sync_to_async
def get_token(request: Request) -> str:
    """
    요청 헤더에 있는 토큰 가져오기

    :return:
    """
    authorization = request.headers.get("Authorization")
    scheme, token = get_authorization_scheme_param(authorization)
    if not authorization or scheme.lower() != "bearer":
        raise TokenError(msg="유효하지 않은 토큰입니다.")
    return token


@sync_to_async
def jwt_decode(token: str) -> int:
    """
    토큰 디코딩

    :param token:
    :return:
    """
    try:
        payload = jwt.decode(
            token, settings.TOKEN_SECRET_KEY, algorithms=[settings.TOKEN_ALGORITHM]
        )
        user_id = int(payload.get("sub"))
        if not user_id:
            raise TokenError(msg="유효하지 않은 토큰입니다.")
    except jwt.ExpiredSignatureError:
        raise TokenError(msg="토큰이 만료되었습니다.")
    except (jwt.JWTError, Exception):
        raise TokenError(msg="유효하지 않은 토큰입니다.")
    return user_id


async def jwt_authentication(token: str) -> dict[str, int]:
    """
    JWT 인증

    :param token:
    :return:
    """
    user_id = await jwt_decode(token)
    key = f"{settings.TOKEN_REDIS_PREFIX}:{user_id}:{token}"
    token_verify = await redis_client.get(key)
    if not token_verify:
        raise TokenError(msg="토큰이 만료되었습니다.")
    return {"sub": user_id}


async def get_current_user(db: AsyncSession, data: dict) -> User:
    """
    토큰을 통해 현재 사용자 가져오기

    :param db:
    :param data:
    :return:
    """
    user_id = data.get("sub")
    user = await user_dao.get_with_relation(db, user_id=user_id)
    if not user:
        raise TokenError(msg="유효하지 않은 토큰입니다.")
    if not user.status:
        raise AuthorizationError(msg="사용자가 잠겨있습니다.")
    if user.dept_id:
        if not user.dept.status:
            raise AuthorizationError(msg="사용자의 부서가 잠겨있습니다.")
        if user.dept.del_flag:
            raise AuthorizationError(msg="사용자의 부서가 삭제되었습니다.")
    if user.roles:
        role_status = [role.status for role in user.roles]
        if all(status == 0 for status in role_status):
            raise AuthorizationError(msg="사용자의 역할이 잠겨있습니다.")
    return user


@sync_to_async
def superuser_verify(request: Request) -> bool:
    """
    토큰을 통해 현재 사용자 권한 검증

    :param request:
    :return:
    """
    is_superuser = request.user.is_superuser
    if not is_superuser:
        raise AuthorizationError(msg="관리자만 접근할 수 있습니다.")
    if not request.user.is_staff:
        raise AuthorizationError(msg="관리자의 백엔드 관리 작업이 금지되었습니다.")
    return is_superuser
