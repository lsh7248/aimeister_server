#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Annotated

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    declared_attr,
    mapped_column,
)

from backend.app.utils.timezone import timezone

# 공통 Mapped 타입 Primary Key, 수동으로 추가해야 함. 아래 사용 예시 참조
# MappedBase -> id: Mapped[id_key]
# DataClassBase && Base -> id: Mapped[id_key] = mapped_column(init=False)
id_key = Annotated[
    int,
    mapped_column(
        primary_key=True,
        index=True,
        autoincrement=True,
        sort_order=-999,
        comment="주 키 id",
    ),
]


# Mixin: 객체 지향 프로그래밍 개념으로, 구조를 더 명확하게 만들어줌, `위키 <https://en.wikipedia.org/wiki/Mixin/>`__
class UserMixin(MappedAsDataclass):
    """사용자 Mixin 데이터 클래스"""

    create_user: Mapped[int] = mapped_column(sort_order=998, comment="생성자")
    update_user: Mapped[int | None] = mapped_column(
        init=False, default=None, sort_order=998, comment="수정자"
    )


class DateTimeMixin(MappedAsDataclass):
    """날짜시간 Mixin 데이터 클래스"""

    created_time: Mapped[datetime] = mapped_column(
        init=False, default_factory=timezone.now, sort_order=999, comment="생성 시간"
    )
    updated_time: Mapped[datetime | None] = mapped_column(
        init=False, onupdate=timezone.now, sort_order=999, comment="수정 시간"
    )


class MappedBase(DeclarativeBase):
    """
    선언적 기본 클래스, 원래의 DeclarativeBase 클래스, 기본 클래스 또는 데이터 모델 클래스의 부모로 사용됨

    `DeclarativeBase <https://docs.sqlalchemy.org/en/20/orm/declarative_config.html>`__
    `mapped_column() <https://docs.sqlalchemy.org/en/20/orm/mapping_api.html#sqlalchemy.orm.mapped_column>`__
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class DataClassBase(MappedAsDataclass, MappedBase):
    """
    선언적 데이터 클래스 기본 클래스, 데이터 클래스를 통합하여 더 고급 구성을 사용할 수 있도록 함. 특히 DeclarativeBase와 함께 사용할 때 주의해야 함

    `MappedAsDataclass <https://docs.sqlalchemy.org/en/20/orm/dataclasses.html#orm-declarative-native-dataclasses>`__
    """  # noqa: E501

    __abstract__ = True


class Base(DataClassBase, DateTimeMixin):
    """
    선언적 Mixin 데이터 클래스 기본 클래스, 데이터 클래스를 통합하고 MiXin 데이터 클래스 기본 테이블 구조를 포함하고 있는 기본 클래스로 이해할 수 있음
    """  # noqa: E501

    __abstract__ = True
