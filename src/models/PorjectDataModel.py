import re
from tkinter import N

from yarl import Query
from .BaseDataModel import BaseDataModel
from .db_schemas import Project
from .enums.DataBaseEnum import DataBaseEnum
from sqlalchemy.future import select
from sqlalchemy import func


class ProjectDataModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance

    async def create_project(self, project: Project) -> str:
        async with self.db_client() as session:
            async with session.begin():
                session.add(project)
                await session.flush()
                await session.refresh(project)
        return project

    async def get_project_or_create_one(self, project_id: int) -> Project:

        async with self.db_client() as session:
            async with session.begin():
                query = select(Project).where(Project.project_id == project_id)

                project_record_result = await session.execute(query)
                project_record = project_record_result.scalar_one_or_none()
                if project_record is None:
                    project = Project(project_id=project_id)
                    project = await self.create_project(project)
                    return project
                return project_record

        # record = await self.collection.find_one({"project_id": project_id})

        # if record is None:
        #     project = Project(project_id=project_id)
        #     project = await self.create_project(project)
        #     return project
        # return Project(**record)

    async def get_all_projects(self, page: int = 1, page_size: int = 10):

        async with self.db_client() as session:
            async with session.begin():
                total_projects_query = select(func.count(Project.project_id))
                total_projects_result = await session.execute(total_projects_query)
                total_projects = total_projects_result.scalar_one()

                total_pages = total_projects // page_size
                if total_projects % page_size != 0:
                    total_pages += 1

                projects_query = (
                    select(Project).offset((page - 1) * page_size).limit(page_size)
                )
                projects_result = await session.execute(projects_query)
                projects = projects_result.scalars().all()

                return projects, total_pages
