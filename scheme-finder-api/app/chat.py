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


def _build_offline_fallback_answer(
    records: List[Dict[str, Any]],
    language: str,
) -> str:
    """Construct an official grounded response directly from stored scheme records if LLM is unreachable."""
    if language == "kn":
        lines = ["ಅಧಿಕೃತ ಯೋಜನಾ ದಾಖಲೆಗಳ ಪ್ರಕಾರ ಸಂಬಂಧಿತ ಮಾಹಿತಿಯು ಹೀಗಿದೆ:"]
        for r in records[:3]:
            name = r.get("name_kn") or r.get("name", "")
            benefit = r.get("benefit", "")
            lines.append(f"\n• {name}:\n  {benefit}")
        lines.append(
            "\n\nಗಮನಿಸಿ: ಅರ್ಹತೆಯನ್ನು ಅರ್ಹತಾ ಪರೀಕ್ಷಕರು (deterministic eligibility checker) ಮಾತ್ರ ನಿರ್ಧರಿಸುತ್ತಾರೆ. ಹೆಚ್ಚಿನ ವಿವರಗಳಿಗಾಗಿ ಮತ್ತು ಅರ್ಜಿ ಸಲ್ಲಿಸಲು ಅಧಿಕೃತ ಸರ್ಕಾರಿ ಪೋರ್ಟಲ್ (https://www.myscheme.gov.in) ಪರಿಶೀಲಿಸಿ."
        )
        return "\n".join(lines)
    else:
        lines = ["Based on official government records, here is the relevant scheme information:"]
        for r in records[:3]:
            name = r.get("name", "")
            benefit = r.get("benefit", "")
            lines.append(f"\n• {name}:\n  {benefit}")
        lines.append(
            "\n\nNote: Eligibility verdicts are determined exclusively by the deterministic eligibility checker. For verified guidelines and application procedures, please check the official government portal (https://www.myscheme.gov.in)."
        )
        return "\n".join(lines)


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
        logger.warning("GEMINI_API_KEY not configured. Returning grounded record fallback.")
        return ChatResponse(
            answer=_build_offline_fallback_answer(relevant_schemes, language),
            language=language,
            sources=sources,
            used_scheme_ids=used_ids,
        )

    prompt = _build_grounded_prompt(question, relevant_schemes, language)

    models_to_try = [model_name]
    fallback_pool = ["gemini-flash-lite-latest", "gemini-3.8-flash", "gemini-flash-latest"]
    for fb in fallback_pool:
        if fb not in models_to_try:
            models_to_try.append(fb)

    last_error = None
    try:
        client = genai.Client(api_key=gemini_api_key)
    except Exception as init_err:
        logger.warning("Failed to initialize Gemini Client: %s. Using record fallback.", init_err)
        return ChatResponse(
            answer=_build_offline_fallback_answer(relevant_schemes, language),
            language=language,
            sources=sources,
            used_scheme_ids=used_ids,
        )

    for current_model in models_to_try:
        try:
            response = client.models.generate_content(
                model=current_model,
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
            last_error = api_err
            err_msg = api_err.message if hasattr(api_err, "message") else str(api_err)
            logger.warning("Gemini model '%s' error: %s. Trying fallback...", current_model, err_msg)
            continue
        except Exception as exc:
            last_error = exc
            logger.warning("Gemini invocation '%s' unexpected error: %s. Trying fallback...", current_model, exc)
            continue

    logger.warning("All Gemini model attempts exhausted (%s). Returning grounded record fallback.", last_error)
    return ChatResponse(
        answer=_build_offline_fallback_answer(relevant_schemes, language),
        language=language,
        sources=sources,
        used_scheme_ids=used_ids,
    )

