import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from DrissionPage import ChromiumPage, ChromiumOptions
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from fastapi_utils.tasks import repeat_every


from WarthunderScraping import WarthunderScraping

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


app = FastAPI(lifespan=lifespan)


@cache(namespace="warthunder", expire=300)
async def cache_get_player_stat(name: str):
    return await scraping.get_player_stat(name)


@app.get("/")
async def root():
    return {"code": 200, "message": "Welcome to War Thunder Player API! Documentation can be viewed at /docs"}


@cache(namespace="warthunder")
@app.get("/player/{name}")
async def player_stat(name: str):
    result = await cache_get_player_stat(name)
    return result


@app.get("/favicon.ico")
async def favicon():
    return None

@repeat_every(seconds=60*60*24)
async def clear_cache():
    logging.info("Clearing cache")
    await FastAPICache.clear("warthunder")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5200, log_config="log_config.yaml", reload=True)
