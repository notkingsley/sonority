from fastapi import FastAPI
from fastapi.responses import RedirectResponse


app = FastAPI()


@app.get("/")
async def root():
    return RedirectResponse(url="/ping")


@app.get("/ping")
async def ping():
    return {"Sonority": "pong!"}
