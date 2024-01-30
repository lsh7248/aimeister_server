#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Union

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, id_key


class Dept(Base):
    """부서 테이블"""

    __tablename__ = "sys_dept"

    id: Mapped[id_key] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(String(50), comment="부서명")
    level: Mapped[int] = mapped_column(default=0, comment="부서 레벨")
    sort: Mapped[int] = mapped_column(default=0, comment="정렬")
    leader: Mapped[str | None] = mapped_column(
        String(20), default=None, comment="책임자"
    )
    phone: Mapped[str | None] = mapped_column(
        String(11), default=None, comment="휴대폰"
    )
    email: Mapped[str | None] = mapped_column(
        String(50), default=None, comment="이메일"
    )
    status: Mapped[int] = mapped_column(
        default=1, comment="부서 상태(0 비활성화 1 활성화)"
    )
    del_flag: Mapped[bool] = mapped_column(
        default=False, comment="삭제 표시 (0 삭제 1 존재)"
    )
    # 상위 부서 일대다
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("sys_dept.id", ondelete="SET NULL"),
        default=None,
        index=True,
        comment="부모 부서 ID",
    )
    parent: Mapped[Union["Dept", None]] = relationship(
        init=False, back_populates="children", remote_side=[id]
    )
    children: Mapped[list["Dept"] | None] = relationship(
        init=False, back_populates="parent"
    )
    # 부서 사용자 일대다
    users: Mapped[list["User"]] = relationship(
        init=False, back_populates="dept"
    )  # noqa: F821
