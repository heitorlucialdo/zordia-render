"""API de render da ZordIA. POST /render -> imagens PNG em base64."""
import base64
import os
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from render_core import render_pngs

TOKEN = os.environ.get("TOKEN", "")

app = FastAPI(title="ZordIA Render")


class RenderIn(BaseModel):
    slides: list[dict]


@app.get("/")
def health():
    return {"ok": True, "service": "zordia-render"}


@app.post("/render")
def render(body: RenderIn, authorization: str = Header(default="")):
    if TOKEN and authorization != f"Bearer {TOKEN}":
        raise HTTPException(status_code=401, detail="token invalido")
    if not body.slides:
        raise HTTPException(status_code=400, detail="sem slides")
    pngs = render_pngs(body.slides)
    return {"images": [base64.b64encode(p).decode() for p in pngs]}
