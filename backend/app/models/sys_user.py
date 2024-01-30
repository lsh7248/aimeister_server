#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Union

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.db_mysql import uuid4_str
from backend.app.models.base import Base, id_key
from backend.app.models.sys_user_role import sys_user_role
from backend.app.utils.timezone import timezone


class User(Base):
    """사용자 테이블"""

    __tablename__ = "sys_user"

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(
        String(50), init=False, default_factory=uuid4_str, unique=True
    )
    username: Mapped[str] = mapped_column(
        String(20), unique=True, index=True, comment="사용자명"
    )
    nickname: Mapped[str] = mapped_column(String(20), unique=True, comment="닉네임")
    password: Mapped[str] = mapped_column(String(255), comment="비밀번호")
    salt: Mapped[str] = mapped_column(String(5), comment="암호화 소금")
    email: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, comment="이메일"
    )
    is_superuser: Mapped[bool] = mapped_column(
        default=False, comment="슈퍼권한(0아니오 1예)"
    )
    is_staff: Mapped[bool] = mapped_column(
        default=False, comment="백엔드 관리자 로그인(0아니오 1예)"
    )
    status: Mapped[int] = mapped_column(
        default=1, comment="사용자 계정 상태(0비활성화 1정상)"
    )
    is_multi_login: Mapped[bool] = mapped_column(
        default=False, comment="중복 로그인 여부(0아니오 1예)"
    )
    avatar: Mapped[str | None] = mapped_column(
        String(255), default=None, comment="아바타"
    )
    phone: Mapped[str | None] = mapped_column(
        String(11), default=None, comment="휴대폰 번호"
    )
    join_time: Mapped[datetime] = mapped_column(
        init=False, default_factory=timezone.now, comment="가입 시간"
    )
    last_login_time: Mapped[datetime | None] = mapped_column(
        init=False, onupdate=timezone.now, comment="마지막 로그인"
    )
    # 부서-사용자 1대다 관계
    dept_id: Mapped[int | None] = mapped_column(
        ForeignKey("sys_dept.id", ondelete="SET NULL"),
        default=None,
        comment="부서 연관 ID",
    )
    dept: Mapped[Union["Dept", None]] = relationship(
        init=False, back_populates="users"
    )  # noqa: F821
    # 사용자 역할 다대다 관계
    roles: Mapped[list["Role"]] = relationship(  # noqa: F821
        init=False, secondary=sys_user_role, back_populates="users"
    )
