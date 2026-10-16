"""Retrieval module for finding relevant scheme records for chat questions."""

import re
from typing import Any, Dict, List, Optional, Tuple, Union
from app.eligibility import check_scheme
from app.models import Profile


# Basic common English stopwords to avoid matching noise
STOPWORDS = {
    "a", "an", "the", "in", "on", "at", "for", "to", "of", "and", "or", "is",
    "are", "am", "was", "were", "what", "how", "which", "who", "whom", "can",
    "could", "do", "does", "did", "i", "me", "my", "we", "us", "our", "you",
    "your", "it", "its", "scheme", "schemes", "yojana", "give", "tell", "about",
    "details", "information", "government",
    # Kannada common query words
    "ಯೋಜನೆ", "ಯೋಜನೆಗಳು", "ಸರ್ಕಾರ", "ಸರ್ಕಾರದಿಂದ", "ಬಗ್ಗೆ", "ತಿಳಿಸಿ", "ಹೇಳಿ",
    "ಇದೆ", "ಯಾವ", "ಮತ್ತು", "ಅಥವಾ", "ನನಗೆ", "ನನ್ನ", "ಯಾವುದು"
}


def _tokenize(text: str) -> List[str]:
    """Tokenize query into lowercase alphanumeric words, filtering stopwords."""
    words = re.findall(r"\w+", text.lower(), re.UNICODE)
    return [w for w in words if len(w) > 1 and w not in STOPWORDS]


def retrieve_relevant_schemes(
    schemes: List[Dict[str, Any]],
    question: str,
    profile: Optional[Union[Profile, Dict[str, Any]]] = None,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """Retrieve up to top `limit` relevant schemes based on question and optional profile.

    Rules:
    - If a profile is given, filter to schemes that are NOT not_eligible.
      Otherwise, start from all schemes.
    - Score each scheme by keyword overlap with the question across name, name_kn, and benefit.
    - Return top candidates with overlap > 0.
    - If nothing overlaps and profile is given, return up to candidates in eligible-first order.
    - If nothing overlaps and no profile is given, return an empty list.
    """
    candidates_with_verdicts: List[Tuple[Dict[str, Any], str]] = []

    if profile is not None:
        for s in schemes:
            verdict, _ = check_scheme(s, profile)
            if verdict != "not_eligible":
                candidates_with_verdicts.append((s, verdict))
    else:
        for s in schemes:
            candidates_with_verdicts.append((s, "possibly_eligible"))

    if not candidates_with_verdicts:
        return []

    tokens = _tokenize(question)

    # Score each candidate by keyword overlap
    scored_candidates = []
    for s, verdict in candidates_with_verdicts:
        target_text = (
            f"{s.get('name', '')} {s.get('name_kn') or ''} {s.get('benefit', '')}"
        ).lower()

        score = 0
        for token in tokens:
            if token in target_text:
                score += 1

        scored_candidates.append((score, verdict, s))

    # Candidates with overlap
    matching = [item for item in scored_candidates if item[0] > 0]

    if matching:
        # Sort by keyword score descending, then eligible-first
        matching.sort(key=lambda x: (x[0], 1 if x[1] == "eligible" else 0), reverse=True)
        return [item[2] for item in matching[:limit]]

    # If nothing overlaps
    if profile is not None:
        # Return up to `limit` candidates in eligible-first order
        scored_candidates.sort(key=lambda x: (1 if x[1] == "eligible" else 0), reverse=True)
        return [item[2] for item in scored_candidates[:limit]]

    return []
