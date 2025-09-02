from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.data.loader import load_all  # implement to fill cache
from app.api.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load HDF5 & CSV once
    load_all()
    yield
    # (optional) shutdown cleanup

app = FastAPI(title="Forecast Statistics API", version="0.1.0", lifespan=lifespan)
app.include_router(router, prefix="/forecast_statistic")