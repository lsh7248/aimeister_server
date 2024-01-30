#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import String
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, id_key


class DictType(Base):
    """사전 유형"""

    __tablename__ = "sys_dict_type"

    id: Mapped[id_key] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(String(32), unique=True, comment="사전 유형 이름")
    code: Mapped[str] = mapped_column(String(32), unique=True, comment="사전 유형 코드")
    status: Mapped[int] = mapped_column(default=1, comment="상태 (0 중지, 1 정상)")
    remark: Mapped[str | None] = mapped_column(LONGTEXT, default=None, comment="비고")
    # 사전 유형 일대다
    datas: Mapped[list["DictData"]] = relationship(
        init=False, back_populates="type"
    )  # noqa: F821
