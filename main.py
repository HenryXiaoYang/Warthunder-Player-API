import logging

from DrissionPage import ChromiumPage, ChromiumOptions
from fastapi import FastAPI

from WarthunderScraping import WarthunderScraping

app = FastAPI()
logging.basicConfig(level="INFO", format='%(process)d | %(levelname)s | %(asctime)s | %(name)s | %(message)s')

browser_path = "/usr/bin/google-chrome"
options = ChromiumOptions()
options.set_paths(browser_path=browser_path)
options.headless(True)
options.set_argument("--no-sandbox")  # Necessary for Docker
options.set_argument("--disable-gpu")  # Optional, helps in some cases
options.set_user_agent(
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
options.set_load_mode("eager")
driver = ChromiumPage(addr_or_opts=options, timeout=60)

scraping = WarthunderScraping(driver)


@app.get("/")
async def root():
    return {"code": 200, "message": "Welcome to War Thunder Player API! Documentation can be viewed at /docs"}


@app.get("/player/{name}")
async def player_stat(name: str):
    result = await scraping.get_player_stat(name)
    return result


@app.get("/favicon.ico")
async def favicon():
    return None
