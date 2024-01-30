#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import String
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import MappedBase, id_key


class CasbinRule(MappedBase):
    """casbin의 CasbinRule 모델 클래스를 재정의하여 사용자 정의 Base를 사용하고 alembic 마이그레이션 문제를 피합니다."""

    __tablename__ = "sys_casbin_rule"

    id: Mapped[id_key]
    ptype: Mapped[str] = mapped_column(String(255), comment="정책 유형: p / g")
    v0: Mapped[str] = mapped_column(String(255), comment="역할 ID / 사용자 UUID")
    v1: Mapped[str] = mapped_column(LONGTEXT, comment="API 경로 / 역할 이름")
    v2: Mapped[str | None] = mapped_column(String(255), comment="요청 메서드")
    v3: Mapped[str | None] = mapped_column(String(255))
    v4: Mapped[str | None] = mapped_column(String(255))
    v5: Mapped[str | None] = mapped_column(String(255))

    def __str__(self):
        arr = [self.ptype]
        for v in (self.v0, self.v1, self.v2, self.v3, self.v4, self.v5):
            if v is None:
                break
            arr.append(v)
        return ", ".join(arr)

    def __repr__(self):
        return '<CasbinRule {}: "{}">'.format(self.id, str(self))
