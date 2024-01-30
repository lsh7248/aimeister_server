#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile

from backend.app.common.response.response_schema import ResponseModel, response_base
from backend.app.tasks import task_demo_async

router = APIRouter(prefix="/tests")


@router.post("/send", summary="다음에서 시연하는 비동기 작업")
async def send_task() -> ResponseModel:
    result = task_demo_async.delay()
    return await response_base.success(data=result.id)


@router.post("/files", summary="파일 데모 업로드")
async def create_file(
    file: Annotated[bytes, File()],
    fileb: Annotated[UploadFile, File()],
    token: Annotated[str, Form()],
) -> ResponseModel:
    return ResponseModel(
        data={
            "file_size": len(file),
            "token": token,
            "fileb_content_type": fileb.content_type,
        }
    )
