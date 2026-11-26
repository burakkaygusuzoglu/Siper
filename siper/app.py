import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from siper.config import get_settings

app = FastAPI(title="Siper")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    settings = get_settings()
    body = await request.json()

    url = f"{settings.upstream_base_url}/v1/chat/completions"
    try:
        async with httpx.AsyncClient(timeout=settings.upstream_timeout) as client:
            upstream = await client.post(url, json=body)
    except httpx.ConnectError:
        return JSONResponse(content={"error": "upstream unreachable"}, status_code=502)

    return JSONResponse(content=upstream.json(), status_code=upstream.status_code)
