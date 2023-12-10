from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from sonority import auth, database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for the lifespan of the app.
    """
    import asyncio

    loop = asyncio.get_event_loop()

    await loop.run_in_executor(None, database.init_db)
    yield


app = FastAPI(lifespan=lifespan, exception_handlers={**auth.exception_handlers})

app.include_router(auth.router)


@app.get("/")
async def root():
    return RedirectResponse(url="/ping")


@app.get("/ping")
async def ping():
    return {"Sonority": "pong!"}
