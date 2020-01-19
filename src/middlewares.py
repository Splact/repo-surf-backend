from .redis_pool import RedisPool


REDIS_POOL = RedisPool()


def setup(app):
    @app.middleware("request")
    async def make_redis_available(request):
        request.ctx.redis = await REDIS_POOL.get_redis_pool(request.app.config)
