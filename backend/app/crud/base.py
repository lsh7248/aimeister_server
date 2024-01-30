#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any, Dict, Generic, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import and_, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.base import MappedBase

ModelType = TypeVar("ModelType", bound=MappedBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_(
        self,
        db: AsyncSession,
        *,
        pk: int | None = None,
        name: str | None = None,
        status: int | None = None,
        del_flag: int | None = None,
    ) -> ModelType | None:
        """
        주키인 id 또는 name을 통해 데이터 가져오기

        :param db:
        :param pk:
        :param name:
        :param status:
        :param del_flag:
        :return:
        """
        assert (
            pk is not None or name is not None
        ), "쿼리 오류, pk와 name 매개변수는 동시에 비어 있을 수 없습니다"
        assert (
            pk is None or name is None
        ), "쿼리 오류, pk와 name 매개변수는 동시에 존재할 수 없습니다"
        where_list = (
            [self.model.id == pk] if pk is not None else [self.model.name == name]
        )
        if status is not None:
            assert status in (
                0,
                1,
            ), "쿼리 오류, status 매개변수는 0 또는 1이어야 합니다"
            where_list.append(self.model.status == status)
        if del_flag is not None:
            assert del_flag in (
                0,
                1,
            ), "쿼리 오류, del_flag 매개변수는 0 또는 1이어야 합니다"
            where_list.append(self.model.del_flag == del_flag)

        result = await db.execute(select(self.model).where(and_(*where_list)))
        return result.scalars().first()

    async def create_(
        self, db: AsyncSession, obj_in: CreateSchemaType, user_id: int | None = None
    ) -> None:
        """
        데이터 추가

        :param db:
        :param obj_in: Pydantic 모델 클래스
        :param user_id:
        :return:
        """
        if user_id:
            create_data = self.model(**obj_in.model_dump(), create_user=user_id)
        else:
            create_data = self.model(**obj_in.model_dump())
        db.add(create_data)

    async def update_(
        self,
        db: AsyncSession,
        pk: int,
        obj_in: UpdateSchemaType | Dict[str, Any],
        user_id: int | None = None,
    ) -> int:
        """
        주키인 id를 통해 데이터 업데이트

        :param db:
        :param pk:
        :param obj_in: Pydantic 모델 클래스 또는 해당 데이터베이스 필드의 딕셔너리
        :param user_id:
        :return:
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        if user_id:
            update_data.update({"update_user": user_id})
        result = await db.execute(
            update(self.model).where(self.model.id == pk).values(**update_data)
        )
        return result.rowcount

    async def delete_(
        self, db: AsyncSession, pk: int, *, del_flag: int | None = None
    ) -> int:
        """
        주키인 id를 통해 데이터 삭제

        :param db:
        :param pk:
        :param del_flag:
        :return:
        """
        if del_flag is None:
            result = await db.execute(delete(self.model).where(self.model.id == pk))
        else:
            assert del_flag == 1, "삭제 오류, del_flag 매개변수는 1이어야 합니다"
            result = await db.execute(
                update(self.model).where(self.model.id == pk).values(del_flag=del_flag)
            )
        return result.rowcount
