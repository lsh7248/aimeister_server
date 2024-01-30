#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from asgiref.sync import sync_to_async
from fastapi import Response
from starlette.background import BackgroundTask
from starlette.datastructures import UploadFile
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from backend.app.common.enums import OperaLogCipherType
from backend.app.common.log import log
from backend.app.core.conf import settings
from backend.app.schemas.opera_log import CreateOperaLogParam
from backend.app.services.opera_log_service import OperaLogService
from backend.app.utils.encrypt import AESCipher, ItsDCipher, Md5Cipher
from backend.app.utils.request_parse import parse_ip_info, parse_user_agent_info
from backend.app.utils.timezone import timezone


class OperaLogMiddleware(BaseHTTPMiddleware):
    """작업 로그 미들웨어"""

    async def dispatch(self, request: Request, call_next) -> Response:
        # 기록할 수 없는 흰색 목록 제외
        path = request.url.path
        if path in settings.OPERA_LOG_EXCLUDE or not path.startswith(
            f"{settings.API_V1_STR}"
        ):
            return await call_next(request)

        # 요청 분석
        user_agent, device, os, browser = await parse_user_agent_info(request)
        ip, country, region, city = await parse_ip_info(request)
        try:
            # 이 정보는 jwt 미들웨어에 종속됨
            username = request.user.username
        except AttributeError:
            username = None
        method = request.method
        router = request.scope.get("route")
        summary = getattr(router, "summary", None) or ""
        args = await self.get_request_args(request)
        args = await self.desensitization(args)

        # 부가 요청 정보 설정
        request.state.ip = ip
        request.state.country = country
        request.state.region = region
        request.state.city = city
        request.state.user_agent = user_agent
        request.state.os = os
        request.state.browser = browser
        request.state.device = device

        # 요청 실행
        start_time = timezone.now()
        code, msg, status, err, response = await self.execute_request(
            request, call_next
        )
        end_time = timezone.now()
        cost_time = (end_time - start_time).total_seconds() * 1000.0

        # 로그 작성
        opera_log_in = CreateOperaLogParam(
            username=username,
            method=method,
            title=summary,
            path=path,
            ip=ip,
            country=country,
            region=region,
            city=city,
            user_agent=user_agent,
            os=os,
            browser=browser,
            device=device,
            args=args,
            status=status,
            code=code,
            msg=msg,
            cost_time=cost_time,
            opera_time=start_time,
        )
        back = BackgroundTask(OperaLogService.create, obj_in=opera_log_in)
        await back()

        # 오류 던지기
        if err:
            raise err from None

        return response

    async def execute_request(self, request: Request, call_next) -> tuple:
        """요청 실행"""
        err = None
        response = None
        try:
            response = await call_next(request)
            code, msg, status = await self.request_exception_handler(request)
        except Exception as e:
            log.exception(e)
            # 코드 처리에는 SQLAlchemy 및 Pydantic 포함
            code = getattr(e, "code", None) or 500
            msg = getattr(e, "msg", None) or "Internal Server Error"
            status = 0
            err = e

        return str(code), msg, status, err, response


@staticmethod
@sync_to_async
def request_exception_handler(request: Request) -> tuple:
    """요청 예외 처리기"""
    code = 200
    msg = "성공"
    status = 1
    try:
        http_exception = request.state.__request_http_exception__
    except AttributeError:
        pass
    else:
        code = http_exception.get("code", 500)
        msg = http_exception.get("msg", "내부 서버 오류")
        status = 0
    try:
        validation_exception = request.state.__request_validation_exception__
    except AttributeError:
        pass
    else:
        code = validation_exception.get("code", 400)
        msg = validation_exception.get("msg", "잘못된 요청")
        status = 0
    return code, msg, status


@staticmethod
async def get_request_args(request: Request) -> dict:
    """요청 인수 가져오기"""
    args = dict(request.query_params)
    args.update(request.path_params)
    # Tip: .body()는 .form() 이전에 가져와야 합니다.
    # https://github.com/encode/starlette/discussions/1933
    body_data = await request.body()
    form_data = await request.form()
    if len(form_data) > 0:
        args.update(
            {
                k: v.filename if isinstance(v, UploadFile) else v
                for k, v in form_data.items()
            }
        )
    else:
        if body_data:
            json_data = await request.json()
            if not isinstance(json_data, dict):
                json_data = {
                    f"{type(json_data)}_to_dict_data": (
                        json_data.decode("utf-8")
                        if isinstance(json_data, bytes)
                        else json_data
                    )
                }
            args.update(json_data)
    return args


@staticmethod
@sync_to_async
def desensitization(args: dict) -> dict | None:
    """
    데이터 익명화 처리

    :param args:
    :return:
    """
    if not args:
        args = None
    else:
        match settings.OPERA_LOG_ENCRYPT:
            case OperaLogCipherType.aes:
                for key in args.keys():
                    if key in settings.OPERA_LOG_ENCRYPT_INCLUDE:
                        args[key] = (
                            AESCipher(settings.OPERA_LOG_ENCRYPT_SECRET_KEY).encrypt(
                                args[key]
                            )
                        ).hex()
            case OperaLogCipherType.md5:
                for key in args.keys():
                    if key in settings.OPERA_LOG_ENCRYPT_INCLUDE:
                        args[key] = Md5Cipher.encrypt(args[key])
            case OperaLogCipherType.itsdangerous:
                for key in args.keys():
                    if key in settings.OPERA_LOG_ENCRYPT_INCLUDE:
                        args[key] = ItsDCipher(
                            settings.OPERA_LOG_ENCRYPT_SECRET_KEY
                        ).encrypt(args[key])
            case OperaLogCipherType.plan:
                pass
            case _:
                for key in args.keys():
                    if key in settings.OPERA_LOG_ENCRYPT_INCLUDE:
                        args[key] = "******"
    return args
