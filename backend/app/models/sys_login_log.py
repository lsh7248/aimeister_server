#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import String
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import DataClassBase, id_key
from backend.app.utils.timezone import timezone


class LoginLog(DataClassBase):
    """로그인 로그 테이블"""

    __tablename__ = "sys_login_log"

    id: Mapped[id_key] = mapped_column(init=False)
    user_uuid: Mapped[str] = mapped_column(String(50), comment="사용자 UUID")
    username: Mapped[str] = mapped_column(String(20), comment="사용자명")
    status: Mapped[int] = mapped_column(
        insert_default=0, comment="로그인 상태 (0 실패, 1 성공)"
    )
    ip: Mapped[str] = mapped_column(String(50), comment="로그인 IP 주소")
    country: Mapped[str | None] = mapped_column(String(50), comment="국가")
    region: Mapped[str | None] = mapped_column(String(50), comment="지역")
    city: Mapped[str | None] = mapped_column(String(50), comment="도시")
    user_agent: Mapped[str] = mapped_column(String(255), comment="요청 헤더")
    os: Mapped[str | None] = mapped_column(String(50), comment="운영 체제")
    browser: Mapped[str | None] = mapped_column(String(50), comment="브라우저")
    device: Mapped[str | None] = mapped_column(String(50), comment="기기")
    msg: Mapped[str] = mapped_column(LONGTEXT, comment="알림 메시지")
    login_time: Mapped[datetime] = mapped_column(comment="로그인 시간")
    created_time: Mapped[datetime] = mapped_column(
        init=False, default_factory=timezone.now, comment="생성 시간"
    )
