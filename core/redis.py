from typing import Optional, Callable

from aioredis import Redis, create_redis_pool


def make_cache_key(*args, **kwargs):
    args = '::'.join(map(str, args))
    kwargs = '::'.join(['%s=%s' % (k, v) for k, v in sorted(kwargs.items())])
    return args if not kwargs else kwargs if not args else '%s::%s' % (args, kwargs)


class RedisCache(object):

    def __init__(self):
        self.redis: Optional[Redis] = None

    async def init(self):
        self.redis = await create_redis_pool("redis://localhost:6379/0?encoding=utf-8")

    async def keys(self, pattern):
        return await self.redis.keys(pattern)

    async def set(self, key, value, *, encoder: Optional[Callable]):
        if encoder is not None:
            value = encoder(value)
        return await self.redis.set(key, value)

    async def get(self, key, *, decoder: Optional[Callable]):
        value = await self.redis.get(key)
        if decoder is not None:
            value = decoder(value)
        return value

    async def close(self):
        self.redis.close()
        await self.redis.wait_closed()


cache = RedisCache()
