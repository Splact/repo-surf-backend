import asyncio_redis


class RedisPool:
    """
    A simple wrapper class that allows you to share a connection
    pool across your application.
    """

    _pool = None

    async def get_redis_pool(self, config):
        if not self._pool:
            self._pool = await asyncio_redis.Pool.create(
                host=config["REDIS_HOST"], port=6379, db=config["REDIS_DB"], poolsize=10
            )

        return self._pool
