from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from cprag.storage.orm import DbOrm, DbMetadata


class DbClient:
    def __init__(self, dsn: str):
        self._engine = create_async_engine(dsn)
        self._sess = async_sessionmaker(bind=self._engine, expire_on_commit=False)

    def session(self) -> AsyncSession:
        return self._sess()

    async def connect(self):
        pass

    async def close(self):
        await self._engine.dispose()
