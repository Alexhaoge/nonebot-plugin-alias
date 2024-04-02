import contextvars
from contextlib import AbstractAsyncContextManager, asynccontextmanager

from nonebot import logger
from nonebot_plugin_orm import get_session
from sqlalchemy.ext.asyncio import AsyncSession

import redis.asyncio as redis
from .config import conf

_ac_current_session = contextvars.ContextVar("ac_current_session")
_redis_current_connection_pool = contextvars.ContextVar("redis_current_connection_pool")
_redis_current_client = contextvars.ContextVar("redis_current_client")

@asynccontextmanager
async def use_ac_session() -> AbstractAsyncContextManager[AsyncSession]:
    """
    Helper function for getting sqlalchemy session.
    Source: https://github.com/bot-ssttkkl/nonebot-plugin-access-control/blob/master/src/nonebot_plugin_access_control/repository/utils.py
    """
    try:
        yield _ac_current_session.get()
    except LookupError:
        session = get_session()
        logger.trace("sqlalchemy session was created")
        token = _ac_current_session.set(session)

        try:
            yield session
        finally:
            await session.close()
            logger.trace("sqlalchemy session was closed")
            _ac_current_session.reset(token)


@asynccontextmanager
async def use_redis_client():
    """
    Helper function for getting Redis client.
    """
    try:
        yield _redis_current_client.get()
    except LookupError:
        redis_pool = redis.ConnectionPool.from_url(conf().redis_url, decode_responses=True)
        redis_client = redis.Redis(connection_pool=redis_pool, decode_responses=True)
        logger.trace("Redis connection was created")
        token_pool = _redis_current_connection_pool.set(redis_pool)
        token_client = _redis_current_client.set(redis_client)

        try:
            yield redis_client
        finally:
            await redis_client.aclose()
            await redis_pool.aclose()
            _redis_current_connection_pool.reset(token_pool)
            _redis_current_client.reset(token_client)
            logger.trace("Redis connection was closed")

__all__ = ['use_ac_session', 'use_redis_client']