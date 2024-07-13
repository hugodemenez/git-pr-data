from pathlib import Path
import logging
from fastapi import FastAPI, BackgroundTasks
import uvicorn
from routers import pr
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(pr.router)

@app.get("/")
def read_root():
    logger.error("Hello World")
    return {"Hello": "World"}


if __name__ == "__main__":
    logger.info("Starting the application")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", reload=True, reload_excludes=['cloned_repo/*'])
