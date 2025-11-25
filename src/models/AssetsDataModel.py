from .BaseDataModel import BaseDataModel
from .db_schemas import Asset
from .enums.DataBaseEnum import DataBaseEnum
from bson import ObjectId
from sqlalchemy.future import select
from sqlalchemy import func, delete


class AssetsDataModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance

    async def create_asset(self, asset: Asset) -> Asset:
        async with self.db_client() as session:
            async with session.begin():
                session.add(asset)
                await session.flush()
                await session.refresh(asset)
        return asset

    async def get_all_project_assets(
        self, asset_project_id: int, asset_type: str
    ) -> list[Asset]:
        async with self.db_client() as session:
            async with session.begin():
                query = select(Asset).where(
                    Asset.asset_project_id == asset_project_id,
                    Asset.asset_type == asset_type,
                )
                result = await session.execute(query)
                assets = result.scalars().all()
                return assets

        # assets = []
        # async for record in records:
        #     assets.append(Asset(**record))
        # return assets

    async def get_asset_by_id(
        self, asset_project_id: int, asset_name: str
    ) -> Asset | None:
        async with self.db_client() as session:
            async with session.begin():
                query = select(Asset).where(
                    Asset.asset_project_id == asset_project_id,
                    Asset.asset_name == asset_name,
                )
                result = await session.execute(query)
                asset = result.scalar_one_or_none()
                return asset
