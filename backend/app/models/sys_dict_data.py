#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, id_key


class DictData(Base):
    """사전 데이터"""

    __tablename__ = "sys_dict_data"

    id: Mapped[id_key] = mapped_column(init=False)
    label: Mapped[str] = mapped_column(String(32), unique=True, comment="사전 레이블")
    value: Mapped[str] = mapped_column(String(32), unique=True, comment="사전 값")
    sort: Mapped[int] = mapped_column(default=0, comment="정렬")
    status: Mapped[int] = mapped_column(default=1, comment="상태 (0: 중지, 1: 정상)")
    remark: Mapped[str | None] = mapped_column(LONGTEXT, default=None, comment="비고")
    # 사전 타입 일대다
    type_id: Mapped[int] = mapped_column(
        ForeignKey("sys_dict_type.id"), default=None, comment="사전 타입 관련 ID"
    )
    type: Mapped["DictType"] = relationship(
        init=False, back_populates="datas"
    )  # noqa: F821
