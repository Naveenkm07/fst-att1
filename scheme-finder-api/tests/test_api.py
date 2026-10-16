"""Integration tests for FastAPI endpoints using TestClient."""

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_returns_200():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_invalid_age_returns_422():
    response = client.post("/api/eligibility", json={"age": -5})
    assert response.status_code == 422


def test_eligibility_returns_verdicts():
    # Farmer profile
    payload = {
        "occupation": "farmer",
        "state": "Karnataka",
    }
    response = client.post("/api/eligibility", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # PM-KISAN should be eligible
    pm_kisan = next((item for item in data if item["scheme_id"] == "pm-kisan-samman-nidhi"), None)
    assert pm_kisan is not None
    assert pm_kisan["verdict"] == "eligible"


def test_unknown_scheme_id_returns_404():
    response = client.get("/api/schemes/non-existent-scheme-xyz-123")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_chat_with_mocked_gemini_answers_in_kannada():
    kannada_question = "ರೈತರಿಗೆ ಸರ್ಕಾರದಿಂದ ಯಾವ ಯೋಜನೆ ಇದೆ?"  # Which scheme is for farmers?

    mock_gemini_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "ರೈತರಿಗೆ ಪ್ರಧಾನ ಮಂತ್ರಿ ಕಿಸಾನ್ ಸಮ್ಮಾನ್ ನಿಧಿ ಯೋಜನೆಯು ಲಭ್ಯವಿದೆ."
    mock_gemini_client.models.generate_content.return_value = mock_response

    with patch("os.getenv") as mock_env:
        def getenv_side_effect(key, default=None):
            if key == "GEMINI_API_KEY":
                return "test-fake-key"
            if key == "GEMINI_MODEL":
                return "gemini-2.5-flash"
            return default

        mock_env.side_effect = getenv_side_effect

        with patch("app.chat.genai.Client", return_value=mock_gemini_client):
            response = client.post(
                "/api/chat",
                json={
                    "question": kannada_question,
                    "profile": {"occupation": "farmer"},
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["language"] == "kn"
            assert "ರೈತರಿಗೆ" in data["answer"]
            assert len(data["sources"]) > 0
            assert "pm-kisan-samman-nidhi" in data["used_scheme_ids"]


def test_chat_with_no_matching_records_returns_fallback():
    irrelevant_question = "How do I bake a chocolate cake in an oven?"
    response = client.post(
        "/api/chat",
        json={
            "question": irrelevant_question,
            "profile": None,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "en"
    assert "not found in the stored scheme records" in data["answer"]
    assert data["used_scheme_ids"] == []
    assert "https://www.myscheme.gov.in" in data["sources"]
