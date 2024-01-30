#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

from redis.asyncio.client import Redis
from redis.exceptions import AuthenticationError, TimeoutError

from backend.app.common.log import log
from backend.app.core.conf import settings


class RedisCli(Redis):
    def __init__(self):
        super(RedisCli, self).__init__(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DATABASE,
            socket_timeout=settings.REDIS_TIMEOUT,
            decode_responses=True,  # 인코딩 utf-8
        )

    async def open(self):
        """
        초기화 연결을 트리거합니다.

        :return:
        """
        try:
            await self.ping()
        except TimeoutError:
            log.error("❌ 데이터베이스 redis 연결 시간 초과")
            sys.exit()
        except AuthenticationError:
            log.error("❌ 데이터베이스 redis 인증 실패")
            sys.exit()
        except Exception as e:
            log.error("❌ 데이터베이스 redis 연결 오류 {}", e)
            sys.exit()

    async def delete_prefix(self, prefix: str, exclude: str | list = None):
        """
        지정된 접두사의 모든 키를 삭제합니다.

        :param prefix:
        :param exclude:
        :return:
        """
        keys = []
        async for key in self.scan_iter(match=f"{prefix}*"):
            if isinstance(exclude, str):
                if key != exclude:
                    keys.append(key)
            elif isinstance(exclude, list):
                if key not in exclude:
                    keys.append(key)
            else:
                keys.append(key)
        for key in keys:
            await self.delete(key)


# redis 연결 객체 생성
redis_client = RedisCli()
