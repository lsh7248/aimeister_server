#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import String
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, id_key
from backend.app.models.sys_role_menu import sys_role_menu
from backend.app.models.sys_user_role import sys_user_role


class Role(Base):
    """역할 테이블"""

    __tablename__ = "sys_role"

    id: Mapped[id_key] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(String(20), unique=True, comment="역할 이름")
    data_scope: Mapped[int | None] = mapped_column(
        default=2, comment="권한 범위 (1: 전체 데이터 권한 2: 사용자 정의 데이터 권한)"
    )
    status: Mapped[int] = mapped_column(
        default=1, comment="역할 상태 (0: 비활성화 1: 정상)"
    )
    remark: Mapped[str | None] = mapped_column(LONGTEXT, default=None, comment="비고")
    # 역할 사용자 다대다
    users: Mapped[list["User"]] = relationship(
        init=False, secondary=sys_user_role, back_populates="roles"
    )
    # 역할 메뉴 다대다
    menus: Mapped[list["Menu"]] = relationship(
        init=False, secondary=sys_role_menu, back_populates="roles"
    )
