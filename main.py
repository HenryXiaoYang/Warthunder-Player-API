import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from DrissionPage import ChromiumPage, ChromiumOptions
from fastapi import FastAPI, Request, Response
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from fastapi_utils.tasks import repeat_every
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from fastapi.responses import StreamingResponse

from WarthunderScraping import WarthunderScraping
from card_generator import card_generator

logging.basicConfig(level="INFO", format='%(process)d | %(levelname)s | %(asctime)s | %(name)s | %(message)s')

browser_path = "/usr/bin/google-chrome"
options = ChromiumOptions()
options.set_paths(browser_path=browser_path)
options.headless(True)
options.set_argument("--no-sandbox")  # Necessary for Docker
options.set_argument("--disable-gpu")  # Optional, helps in some cases
options.set_user_agent(
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
options.set_proxy("http://127.0.0.1:7890")

driver = ChromiumPage(addr_or_opts=options, timeout=60)

scraping = WarthunderScraping(driver)


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


@cache(namespace="warthunder", expire=300)
async def cache_get_player_stat(name: str):
    return await scraping.get_player_stat(name)


@app.get("/")
async def root():
    return {"code": 200, "message": "Welcome to War Thunder Player API! Documentation can be viewed at /docs"}


@cache(namespace="warthunder")
@app.get("/player/{name}")
@limiter.limit("5/minute")
async def player_stat(request: Request, response: Response, name: str):
    result = await cache_get_player_stat(name)
    return result

@app.get("/card/{name}")
async def card(request: Request, response: Response, name: str):
    data = await player_stat(request=request, response=response, name=name)

    card_buf = await card_generator(data)

    return StreamingResponse(card_buf, media_type="image/png")

@app.get("/favicon.ico")
async def favicon():
    return None


@repeat_every(seconds=60 * 60 * 24)
async def clear_cache():
    logging.info("Clearing cache")
    await FastAPICache.clear("warthunder")
