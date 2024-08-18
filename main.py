import logging

import uvicorn
from fastapi import FastAPI

from WarthunderScraping import warthunder_scraping

app = FastAPI()
logging.basicConfig(level="INFO", format='%(process)d | %(levelname)s | %(asctime)s | %(name)s | %(message)s')


@app.get("/")
async def root():
    return {"code": 200, "message": "Welcome to War Thunder Player API! Documentation can be viewed at /docs"}


@app.get("/player/{name}")
async def player_stat(name: str):
    result = await warthunder_scraping.get_player_stat(name)
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
