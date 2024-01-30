#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.routing import APIRoute


def simplify_operation_ids(app: FastAPI) -> None:
    """
    작업 ID를 간소화하여 생성된 클라이언트에 더 간단한 API 함수 이름이 포함되도록 합니다.

    :param app:
    :return:
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name
