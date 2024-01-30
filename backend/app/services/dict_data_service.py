#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import Select

from backend.app.common.exception import errors
from backend.app.crud.crud_dict_data import dict_data_dao
from backend.app.crud.crud_dict_type import dict_type_dao
from backend.app.database.db_mysql import async_db_session
from backend.app.models.sys_dict_data import DictData
from backend.app.schemas.dict_data import CreateDictDataParam, UpdateDictDataParam


class DictDataService:
    @staticmethod
    async def get(*, pk: int) -> DictData:
        async with async_db_session() as db:
            dict_data = await dict_data_dao.get_with_relation(db, pk)
            if not dict_data:
                raise errors.NotFoundError(msg="사전 데이터가 존재하지 않습니다.")
            return dict_data

    @staticmethod
    async def get_select(
        *, label: str = None, value: str = None, status: int = None
    ) -> Select:
        return await dict_data_dao.get_all(label=label, value=value, status=status)

    @staticmethod
    async def create(*, obj: CreateDictDataParam) -> None:
        async with async_db_session.begin() as db:
            dict_data = await dict_data_dao.get_by_label(db, obj.label)
            if dict_data:
                raise errors.ForbiddenError(msg="사전 데이터가 이미 존재합니다.")
            dict_type = await dict_type_dao.get(db, obj.type_id)
            if not dict_type:
                raise errors.ForbiddenError(msg="사전 유형이 존재하지 않습니다.")
            await dict_data_dao.create(db, obj)

    @staticmethod
    async def update(*, pk: int, obj: UpdateDictDataParam) -> int:
        async with async_db_session.begin() as db:
            dict_data = await dict_data_dao.get(db, pk)
            if not dict_data:
                raise errors.NotFoundError(msg="사전 데이터가 존재하지 않습니다.")
            if dict_data.label != obj.label:
                if await dict_data_dao.get_by_label(db, obj.label):
                    raise errors.ForbiddenError(msg="사전 데이터가 이미 존재합니다.")
            dict_type = await dict_type_dao.get(db, obj.type_id)
            if not dict_type:
                raise errors.ForbiddenError(msg="사전 유형이 존재하지 않습니다.")
            count = await dict_data_dao.update(db, pk, obj)
            return count

    @staticmethod
    async def delete(*, pk: list[int]) -> int:
        async with async_db_session.begin() as db:
            count = await dict_data_dao.delete(db, pk)
            return count


dict_data_service: DictDataService = DictDataService()
