#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Union

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, id_key
from backend.app.models.sys_role_menu import sys_role_menu


class Menu(Base):
    """메뉴 테이블"""

    __tablename__ = "sys_menu"

    id: Mapped[id_key] = mapped_column(init=False)
    title: Mapped[str] = mapped_column(String(50), comment="메뉴 제목")
    name: Mapped[str] = mapped_column(String(50), comment="메뉴 이름")
    level: Mapped[int] = mapped_column(default=0, comment="메뉴 레벨")
    sort: Mapped[int] = mapped_column(default=0, comment="정렬")
    icon: Mapped[str | None] = mapped_column(
        String(100), default=None, comment="메뉴 아이콘"
    )
    path: Mapped[str | None] = mapped_column(
        String(200), default=None, comment="라우트 주소"
    )
    menu_type: Mapped[int] = mapped_column(
        default=0, comment="메뉴 유형 (0 디렉토리 1 메뉴 2 버튼)"
    )
    component: Mapped[str | None] = mapped_column(
        String(255), default=None, comment="컴포넌트 경로"
    )
    perms: Mapped[str | None] = mapped_column(
        String(100), default=None, comment="권한 식별자"
    )
    status: Mapped[int] = mapped_column(
        default=1, comment="메뉴 상태 (0 비활성화 1 정상)"
    )
    show: Mapped[int] = mapped_column(default=1, comment="표시 여부 (0 아니오 1 예)")
    cache: Mapped[int] = mapped_column(default=1, comment="캐시 여부 (0 아니오 1 예)")
    remark: Mapped[str | None] = mapped_column(LONGTEXT, default=None, comment="비고")
    # 부모 메뉴 일대다
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("sys_menu.id", ondelete="SET NULL"),
        default=None,
        index=True,
        comment="부모 메뉴 ID",
    )
    parent: Mapped[Union["Menu", None]] = relationship(
        init=False, back_populates="children", remote_side=[id]
    )
    children: Mapped[list["Menu"] | None] = relationship(
        init=False, back_populates="parent"
    )
    # 메뉴 역할 다대다
    roles: Mapped[list["Role"]] = relationship(
        init=False, secondary=sys_role_menu, back_populates="menus"
    )
