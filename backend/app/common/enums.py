#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum
from enum import IntEnum as SourceIntEnum
from typing import Type


class _EnumBase:
    @classmethod
    def get_member_keys(cls: Type[Enum]) -> list[str]:
        return [name for name in cls.__members__.keys()]

    @classmethod
    def get_member_values(cls: Type[Enum]) -> list:
        return [item.value for item in cls.__members__.values()]


class IntEnum(_EnumBase, SourceIntEnum):
    """정수형 열거형"""

    pass


class StrEnum(_EnumBase, str, Enum):
    """문자열 열거형"""

    pass


class MenuType(IntEnum):
    """메뉴 유형"""

    directory = 0
    menu = 1
    button = 2


class RoleDataScopeType(IntEnum):
    """데이터 범위"""

    all = 1
    custom = 2


class MethodType(StrEnum):
    """요청 방법"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"


class LoginLogStatusType(IntEnum):
    """로그인 로그 상태"""

    fail = 0
    success = 1


class BuildTreeType(StrEnum):
    """트리 구조 생성 유형"""

    traversal = "traversal"
    recursive = "recursive"


class OperaLogCipherType(IntEnum):
    """동작 로그 암호화 유형"""

    aes = 0
    md5 = 1
    itsdangerous = 2
    plan = 3


class StatusType(IntEnum):
    """상태 유형"""

    disable = 0
    enable = 1
