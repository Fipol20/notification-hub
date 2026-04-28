from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import Base, engine
from app.routers import notifications, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Notification Hub",
    description="Realtime-уведомления через SSE с rate limiting и историей.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(users.router)
app.include_router(notifications.router)


@app.get("/health")
def health():
    return {"status": "ok"}
