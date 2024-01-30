#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any

from backend.app.common.exception import errors
from backend.app.crud.crud_dept import dept_dao
from backend.app.database.db_mysql import async_db_session
from backend.app.models import Dept
from backend.app.schemas.dept import CreateDeptParam, UpdateDeptParam
from backend.app.utils.build_tree import get_tree_data


class DeptService:
    @staticmethod
    async def get(*, pk: int) -> Dept:
        async with async_db_session() as db:
            dept = await dept_dao.get(db, pk)
            if not dept:
                raise errors.NotFoundError(msg="부서가 존재하지 않습니다")
            return dept

    @staticmethod
    async def get_dept_tree(
        *,
        name: str | None = None,
        leader: str | None = None,
        phone: str | None = None,
        status: int | None = None
    ) -> list[dict[str, Any]]:
        async with async_db_session() as db:
            dept_select = await dept_dao.get_all(
                db=db, name=name, leader=leader, phone=phone, status=status
            )
            tree_data = await get_tree_data(dept_select)
            return tree_data

    @staticmethod
    async def create(*, obj: CreateDeptParam) -> None:
        async with async_db_session.begin() as db:
            dept = await dept_dao.get_by_name(db, obj.name)
            if dept:
                raise errors.ForbiddenError(msg="부서 이름이 이미 존재합니다")
            if obj.parent_id:
                parent_dept = await dept_dao.get(db, obj.parent_id)
                if not parent_dept:
                    raise errors.NotFoundError(msg="상위 부서가 존재하지 않습니다")
            await dept_dao.create(db, obj)

    @staticmethod
    async def update(*, pk: int, obj: UpdateDeptParam) -> int:
        async with async_db_session.begin() as db:
            dept = await dept_dao.get(db, pk)
            if not dept:
                raise errors.NotFoundError(msg="부서가 존재하지 않습니다")
            if dept.name != obj.name:
                if await dept_dao.get_by_name(db, obj.name):
                    raise errors.ForbiddenError(msg="부서 이름이 이미 존재합니다")
            if obj.parent_id:
                parent_dept = await dept_dao.get(db, obj.parent_id)
                if not parent_dept:
                    raise errors.NotFoundError(msg="상위 부서가 존재하지 않습니다")
            if obj.parent_id == dept.id:
                raise errors.ForbiddenError(
                    msg="자기 자신을 상위 부서로 설정할 수 없습니다"
                )
            count = await dept_dao.update(db, pk, obj)
            return count

    @staticmethod
    async def delete(*, pk: int) -> int:
        async with async_db_session.begin() as db:
            dept_user = await dept_dao.get_user_relation(db, pk)
            if dept_user:
                raise errors.ForbiddenError(
                    msg="부서에 속한 사용자가 존재하여 삭제할 수 없습니다"
                )
            children = await dept_dao.get_children(db, pk)
            if children:
                raise errors.ForbiddenError(
                    msg="하위 부서가 존재하여 삭제할 수 없습니다"
                )
            count = await dept_dao.delete(db, pk)
            return count


dept_service: DeptService = DeptService()
