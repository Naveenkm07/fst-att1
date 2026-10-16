"""Main FastAPI application for Government Scheme Finder Bot."""

import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from app.chat import generate_chat_answer
from app.db import fetch_all_schemes, fetch_scheme_by_id
from app.eligibility import check_scheme
from app.models import (
    ChatRequest,
    ChatResponse,
    EligibilityResult,
    Profile,
    Scheme,
)

# Load environment variables from .env
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

app = FastAPI(
    title="Government Scheme Finder Bot API",
    description="Deterministic eligibility verification and grounded bilingual chat for official Indian welfare schemes.",
    version="1.0.0",
)

# CORS setup
cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
for default_origin in ["http://localhost:5173", "http://127.0.0.1:5173"]:
    if default_origin not in origins:
        origins.append(default_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", summary="Health check endpoint")
def health_check():
    """Return health status."""
    return {"status": "ok"}


@app.post(
    "/api/eligibility",
    response_model=List[EligibilityResult],
    summary="Evaluate citizen eligibility for government schemes",
)
def evaluate_eligibility(
    profile: Profile,
    include_not_eligible: bool = Query(
        default=False,
        description="Include schemes where citizen is deterministically not eligible",
    ),
):
    """Deterministically compute eligibility across all stored schemes."""
    schemes = fetch_all_schemes()
    results: List[EligibilityResult] = []

    for s in schemes:
        verdict, missing = check_scheme(s, profile)
        if verdict != "not_eligible" or include_not_eligible:
            results.append(
                EligibilityResult(
                    scheme_id=s.get("id", ""),
                    name=s.get("name", ""),
                    name_kn=s.get("name_kn"),
                    benefit=s.get("benefit", ""),
                    source_url=s.get("source_url", ""),
                    verdict=verdict,
                    missing_fields=missing,
                )
            )

    # Sort results: eligible first, then possibly_eligible, then not_eligible
    verdict_priority = {"eligible": 0, "possibly_eligible": 1, "not_eligible": 2}
    results.sort(key=lambda r: verdict_priority.get(r.verdict, 3))
    return results


@app.get(
    "/api/schemes/{scheme_id}",
    response_model=Scheme,
    summary="Get details of a specific scheme by ID",
)
def get_scheme(scheme_id: str):
    """Retrieve full details of one scheme, or 404 if not found."""
    scheme = fetch_scheme_by_id(scheme_id)
    if not scheme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheme with id '{scheme_id}' was not found.",
        )
    return scheme


@app.post(
    "/api/chat",
    response_model=ChatResponse,
    summary="Grounded chatbot for scheme explanations",
)
def chat_with_schemes(payload: ChatRequest):
    """Answer citizen questions grounded strictly in stored scheme records."""
    all_schemes = fetch_all_schemes()
    return generate_chat_answer(
        question=payload.question,
        all_schemes=all_schemes,
        profile=payload.profile,
    )
