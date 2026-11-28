import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from siper.config import get_settings
from siper.pii.masker import Masker

app = FastAPI(title="Siper")


@app.get("/health")
async def health():
    return {"status": "ok"}


def _mask_messages(body: dict, masker: Masker) -> None:
    """Mask personal data in every chat message, in place."""
    for message in body.get("messages", []):
        content = message.get("content")
        if isinstance(content, str):
            message["content"] = masker.mask(content)
        elif isinstance(content, list):  # multi-part content: [{"type": "text", "text": ...}]
            for part in content:
                if isinstance(part, dict) and isinstance(part.get("text"), str):
                    part["text"] = masker.mask(part["text"])


def _unmask_strings(value, masker: Masker):
    """Walk any JSON value and restore the real values in every string."""
    if isinstance(value, str):
        return masker.unmask(value)
    if isinstance(value, list):
        return [_unmask_strings(item, masker) for item in value]
    if isinstance(value, dict):
        return {key: _unmask_strings(item, masker) for key, item in value.items()}
    return value


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    settings = get_settings()
    body = await request.json()
    url = f"{settings.upstream_base_url}/v1/chat/completions"

    # The vault lives only for this request; `with` empties it even if something fails.
    with Masker() as masker:
        _mask_messages(body, masker)
        try:
            async with httpx.AsyncClient(timeout=settings.upstream_timeout) as client:
                upstream = await client.post(url, json=body)
        except httpx.ConnectError:
            return JSONResponse(content={"error": "upstream unreachable"}, status_code=502)

        content = _unmask_strings(upstream.json(), masker)
        return JSONResponse(content=content, status_code=upstream.status_code)
