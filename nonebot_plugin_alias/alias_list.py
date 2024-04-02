import uuid
from sqlalchemy import select
from .utils import use_ac_session, use_redis_client
from .orm import AliasORM


class AliasList:

    @staticmethod
    async def load_alias_from_db():
        alist = dict()
        async with use_ac_session() as session:
            stmt = select(AliasORM)
            async for x in await session.stream_scalars(stmt):
                if x.id in alist:
                    alist[x.id][x.name] = x.command
                else:
                    alist[x.id] = dict()
        async with use_redis_client() as client:
            for id in alist:
                if len(alist[id]):
                    await client.hmset(f'alias_{id}', alist[id])
        return alist
    
    # @classmethod
    # async def create(cls):
    #     return cls(await cls.load_alias_from_db())

    @staticmethod
    async def add_alias(id: str, name: str, command: str) -> bool:
        async with use_ac_session() as session:
            stmt = select(AliasORM).where(AliasORM.id==id, AliasORM.name==name).with_for_update(read=True)
            exsist_alias = (await session.execute(stmt)).first()
            if exsist_alias:
                exsist_alias[0].command = command
            else:
                session.add(AliasORM(id, name, command))
            await session.commit()
        
        async with use_redis_client() as client:
            await client.hset(f'alias_{id}', name, command)

        return True

    @staticmethod
    async def del_alias(self, id: str, name: str) -> bool:
        async with use_ac_session() as session:
            stmt = select(AliasORM).where(AliasORM.id==id, AliasORM.name==name).with_for_update(read=True)
            alias_r = (await session.execute(stmt)).first()
            if alias_r:
                await session.delete(alias_r[0])
                await session.commit()
        
        async with use_redis_client() as client:
            del_num = await client.hdel(f'alias_{id}', name)
        return del_num

    @staticmethod
    async def del_alias_all(id: str) -> bool:
        async with use_redis_client() as client:
            del_num = await client.delete(f'alias_{id}')

        async with use_ac_session() as session:
            stmt = select(AliasORM).where(AliasORM.id==id).with_for_update(read=True)
            async for x in await session.stream_scalars(stmt):
                await session.delete(x)
            await session.commit()
        return True

    @staticmethod
    async def get_alias(id: str, name: str) -> str:
        async with use_redis_client() as client:
            command = await client.hget(f'alias_{id}', name)
        return command

    @staticmethod
    async def get_alias_all(self, id: str) -> dict:
        async with use_redis_client() as client:
            commands = await client.hgetall(f'alias_{id}')
        return commands

# class AliasFactory():
#     _alias = None

#     @classmethod
#     async def get_alias(cls):
#         if cls._alias is None:
#             cls._alias = await AliasList.create()
#         return cls._alias

# aliases = AliasList(data_path / "aliases.json")

__all__ = ['AliasList']