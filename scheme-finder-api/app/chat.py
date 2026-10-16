"""Chatbot service with language detection, grounded prompt, and Gemini LLM integration."""

import logging
import os
import unicodedata
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from google import genai
from google.genai import errors as genai_errors
from app.models import ChatResponse, Profile
from app.retrieval import retrieve_relevant_schemes

logger = logging.getLogger("scheme_finder.chat")


def detect_language(text: str) -> str:
    """Return 'kn' if any character's unicodedata name starts with 'KANNADA', else 'en'."""
    for ch in text:
        try:
            name = unicodedata.name(ch, "")
            if name.startswith("KANNADA"):
                return "kn"
        except (ValueError, TypeError):
            continue
    return "en"


def _build_grounded_prompt(
    question: str,
    records: List[Dict[str, Any]],
    language: str,
) -> str:
    """Construct a strictly grounded prompt adhering to safety and domain constraints."""
    schemes_text_parts = []
    for r in records:
        part = (
            f"Scheme ID: {r.get('id')}\n"
            f"Name (English): {r.get('name')}\n"
            f"Name (Kannada): {r.get('name_kn') or 'N/A'}\n"
            f"Benefit: {r.get('benefit')}\n"
            f"Official URL: {r.get('source_url')}\n"
        )
        schemes_text_parts.append(part)

    schemes_context = "\n---\n".join(schemes_text_parts) if schemes_text_parts else "No schemes provided."

    lang_instruction = (
        "Respond fluently in Kannada (ಕನ್ನಡ)."
        if language == "kn"
        else "Respond in clear, professional English."
    )

    prompt = f"""You are the Government Scheme Finder Assistant for Naveen, NHCE Bengaluru.
You assist citizens by explaining official government schemes.

Strict instructions you MUST follow:
1. Answer ONLY using the facts from the provided scheme records below.
2. If the user's question cannot be answered completely from the provided records, state clearly that you do not know the answer based on current records and point the citizen to the official government portal (https://www.myscheme.gov.in).
3. NEVER state or decide whether the user is eligible for any scheme. Always state that eligibility verdicts are determined exclusively by the deterministic eligibility checker.
4. {lang_instruction}
5. Keep your entire answer concise and under 150 words.
6. Do NOT invent or extrapolate amounts, dates, quotas, or rules not present in the records.

Provided Scheme Records:
{schemes_context}

Citizen Question:
{question}

Answer:"""
    return prompt


def generate_chat_answer(
    question: str,
    all_schemes: List[Dict[str, Any]],
    profile: Optional[Profile] = None,
) -> ChatResponse:
    """Process a citizen chat question against stored scheme records."""
    language = detect_language(question)
    relevant_schemes = retrieve_relevant_schemes(all_schemes, question, profile)

    if not relevant_schemes:
        if language == "kn":
            fallback_answer = (
                "ಕ್ಷಮಿಸಿ, ಈ ಪ್ರಶ್ನೆಗೆ ಸಂಬಂಧಿಸಿದ ಮಾಹಿತಿ ನಮ್ಮ ಯೋಜನಾ ದಾಖಲೆಗಳಲ್ಲಿ ಲಭ್ಯವಿಲ್ಲ. "
                "ದಯವಿಟ್ಟು ಹೆಚ್ಚಿನ ವಿವರಗಳಿಗಾಗಿ ಅಧಿಕೃತ ಸರ್ಕಾರಿ ಪೋರ್ಟಲ್ (https://www.myscheme.gov.in) ಪರಿಶೀಲಿಸಿ."
            )
        else:
            fallback_answer = (
                "I'm sorry, information addressing your question was not found in the stored scheme records. "
                "Please check the official government portal (https://www.myscheme.gov.in) for verified details."
            )
        return ChatResponse(
            answer=fallback_answer,
            language=language,
            sources=["https://www.myscheme.gov.in"],
            used_scheme_ids=[],
        )

    sources = list(dict.fromkeys([s.get("source_url") for s in relevant_schemes if s.get("source_url")]))
    used_ids = [s.get("id") for s in relevant_schemes if s.get("id")]

    gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model_name = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest").strip()

    if not gemini_api_key:
        logger.warning("GEMINI_API_KEY not configured. Returning 503.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI chat service is currently unavailable. Please verify GEMINI_API_KEY in backend .env.",
        )

    prompt = _build_grounded_prompt(question, relevant_schemes, language)

    try:
        client = genai.Client(api_key=gemini_api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        answer_text = response.text or ""
        return ChatResponse(
            answer=answer_text.strip(),
            language=language,
            sources=sources,
            used_scheme_ids=used_ids,
        )
    except genai_errors.APIError as api_err:
        logger.error("Gemini API Error: %s", api_err.message if hasattr(api_err, "message") else str(api_err))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI chat service is currently experiencing high load or quota limits. Please try again shortly.",
        )
    except Exception as exc:
        logger.error("Unexpected error during Gemini invocation: %s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI chat service is temporarily unavailable. Please try again later.",
        )
