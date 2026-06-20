from __future__ import annotations

import os

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import MissionRequest, RequestValidationError
from .orchestrator import PatchPilot
from .evidence import latest, store

app = FastAPI(title="PatchPilot API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "mode": os.getenv("PATCHPILOT_MODE", "mock")}


@app.get("/api/demo")
def demo() -> dict:
    request = MissionRequest.from_dict(
        {
            "repo_url": "https://github.com/patchpilot/demo-calculator",
            "commit_sha": "demo-bug-001",
            "issue": "Division incorrectly truncates fractional results.",
            "acceptance_criteria": ["Division preserves fractional results"],
            "max_budget_usdc": 2,
        }
    )
    live = latest()
    return live or {"request": request.to_dict(), "result": PatchPilot().run(request).to_dict()}


@app.post("/api/live-evidence", status_code=202)
def ingest_live_evidence(payload: dict, authorization: str | None = Header(default=None)) -> dict:
    expected = os.getenv("EVIDENCE_INGEST_TOKEN", "")
    if not expected or authorization != f"Bearer {expected}":
        raise HTTPException(status_code=401, detail="invalid evidence ingest token")
    result = payload.get("result", {})
    if result.get("mode") != "live":
        raise HTTPException(status_code=422, detail="only live CROO evidence can be ingested")
    store(payload)
    return {"accepted": True}


@app.post("/api/missions")
def create_mission(payload: dict) -> dict:
    try:
        request = MissionRequest.from_dict(payload)
        return PatchPilot().run(request).to_dict()
    except RequestValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def run() -> None:
    import uvicorn

    uvicorn.run("patchpilot.api:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
