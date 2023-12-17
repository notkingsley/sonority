from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from sonority import artists, auth


exception_handlers = {
    **artists.exception_handlers,
    **auth.exception_handlers,
}

app = FastAPI(exception_handlers=exception_handlers)

app.include_router(auth.router)
app.include_router(artists.router)


@app.get("/")
async def root():
    return RedirectResponse(url="/ping")


@app.get("/ping")
async def ping():
    return {"sonority": "pong!"}
