from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging

from app.core.security import SecurityHeadersMiddleware
from app.api.endpoints import main_page, meta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Bitcoin Logarithmic Spiral Visualization API...")
    yield
    logger.info("Shutting down Bitcoin Logarithmic Spiral Visualization API...")

app = FastAPI(
    title="Bitcoin Logarithmic Spiral Visualization API",
    description="Secure API for generating logarithmic spiral charts of Bitcoin prices",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(SecurityHeadersMiddleware)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(main_page.router)
app.include_router(meta.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 