import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from fastapi_utils.tasks import repeat_every
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from scraping import Scraping

logging.basicConfig(level="INFO", format='%(process)d | %(levelname)s | %(asctime)s | %(name)s | %(message)s')

# 从环境变量获取代理配置，设置默认值
PROXY_HOST = os.getenv('PROXY_HOST', '')
PROXY_PORT = int(os.getenv('PROXY_PORT', 0))


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await clear_cache()
    FastAPICache.init(InMemoryBackend())
    yield
    await FastAPICache.clear("warthunder")


limiter = Limiter(key_func=get_remote_address)
app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

scraper = Scraping(proxy_host=PROXY_HOST, proxy_port=PROXY_PORT)


@cache(namespace="warthunder", expire=300)
async def cache_get_player_stat(name: str):
    return await scraper.get_player_stat(name)


@app.get("/")
async def root():
    # redirect to the documentation
    return RedirectResponse(url="/docs")


@cache(namespace="warthunder")
@app.get("/player")
async def player_stat(request: Request, response: Response, nick: str = None):
    if not nick:
        response.status_code = 400
        return {
            "code": 400,
            "message": "Parameter \"nick\" is required",
            "data": None
        }
    
    if not isinstance(nick, str) or len(nick.strip()) == 0:
        response.status_code = 400
        return {
            "code": 400,
            "message": "Provided nick is invalid",
            "data": None
        }
        

    result = await cache_get_player_stat(nick)
    return result


@app.get("/favicon.ico")
async def favicon():
    return None


@repeat_every(seconds=60 * 60 * 24)
async def clear_cache():
    logging.info("Clearing cache")
    await FastAPICache.clear("warthunder")
