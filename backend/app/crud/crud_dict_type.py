#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import Select, delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.crud.base import CRUDBase
from backend.app.models.sys_dict_type import DictType
from backend.app.schemas.dict_type import CreateDictTypeParam, UpdateDictTypeParam


class CRUDDictType(CRUDBase[DictType, CreateDictTypeParam, UpdateDictTypeParam]):
    async def get(self, db: AsyncSession, pk: int) -> DictType | None:
        return await self.get_(db, pk=pk)

    async def get_all(self, *, name: str = None, code: str = None, status: int = None) -> Select:
        se = select(self.model).order_by(desc(self.model.created_time))
        where_list = []
        if name:
            where_list.append(self.model.name.like(f'%{name}%'))
        if code:
            where_list.append(self.model.code.like(f'%{code}%'))
        if status is not None:
            where_list.append(self.model.status == status)
        if where_list:
            se = se.where(*where_list)
        return se

    async def get_by_code(self, db: AsyncSession, code: str) -> DictType | None:
        dept = await db.execute(select(self.model).where(self.model.code == code))
        return dept.scalars().first()

    async def create(self, db: AsyncSession, obj_in: CreateDictTypeParam) -> None:
        await self.create_(db, obj_in)

    async def update(self, db: AsyncSession, pk: int, obj_in: UpdateDictTypeParam) -> int:
        return await self.update_(db, pk, obj_in)

    async def delete(self, db: AsyncSession, pk: list[int]) -> int:
        apis = await db.execute(delete(self.model).where(self.model.id.in_(pk)))
        return apis.rowcount


dict_type_dao: CRUDDictType = CRUDDictType(DictType)
