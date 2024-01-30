#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import String
from sqlalchemy.dialects.mysql import JSON, LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import DataClassBase, id_key
from backend.app.utils.timezone import timezone


class OperaLog(DataClassBase):
    """작업 로그 테이블"""

    __tablename__ = "sys_opera_log"

    id: Mapped[id_key] = mapped_column(init=False)
    username: Mapped[str | None] = mapped_column(String(20), comment="사용자 이름")
    method: Mapped[str] = mapped_column(String(20), comment="요청 유형")
    title: Mapped[str] = mapped_column(String(255), comment="작업 모듈")
    path: Mapped[str] = mapped_column(String(500), comment="요청 경로")
    ip: Mapped[str] = mapped_column(String(50), comment="IP 주소")
    country: Mapped[str | None] = mapped_column(String(50), comment="국가")
    region: Mapped[str | None] = mapped_column(String(50), comment="지역")
    city: Mapped[str | None] = mapped_column(String(50), comment="도시")
    user_agent: Mapped[str] = mapped_column(String(255), comment="요청 헤더")
    os: Mapped[str | None] = mapped_column(String(50), comment="운영 체제")
    browser: Mapped[str | None] = mapped_column(String(50), comment="브라우저")
    device: Mapped[str | None] = mapped_column(String(50), comment="장치")
    args: Mapped[str | None] = mapped_column(JSON(), comment="요청 매개변수")
    status: Mapped[int] = mapped_column(comment="작업 상태 (0이상 1정상)")
    code: Mapped[str] = mapped_column(
        String(20), insert_default="200", comment="작업 상태 코드"
    )
    msg: Mapped[str | None] = mapped_column(LONGTEXT, comment="알림 메시지")
    cost_time: Mapped[float] = mapped_column(
        insert_default=0.0, comment="요청 시간(ms)"
    )
    opera_time: Mapped[datetime] = mapped_column(comment="작업 시간")
    created_time: Mapped[datetime] = mapped_column(
        init=False, default_factory=timezone.now, comment="생성 시간"
    )
