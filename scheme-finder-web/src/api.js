/**
 * API client module for Scheme Finder API.
 * Uses native fetch without third-party libraries.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Deterministically check eligibility based on citizen profile.
 */
export async function checkEligibility(profile) {
  const response = await fetch(`${API_BASE_URL}/api/eligibility`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(profile),
  });

  if (!response.ok) {
    let errorDetail = "Failed to evaluate eligibility";
    try {
      const errorData = await response.json();
      errorDetail = errorData.detail || errorDetail;
    } catch {
      // ignore json parse error
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

/**
 * Send citizen question to the grounded chat assistant.
 */
export async function sendChatMessage(question, profile = null) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
      profile,
    }),
  });

  if (!response.ok) {
    let errorDetail = "Failed to communicate with chat service";
    try {
      const errorData = await response.json();
      errorDetail = errorData.detail || errorDetail;
    } catch {
      // ignore json parse error
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

/**
 * Fetch scheme record by ID.
 */
export async function fetchScheme(schemeId) {
  const response = await fetch(`${API_BASE_URL}/api/schemes/${encodeURIComponent(schemeId)}`);
  if (!response.ok) {
    throw new Error(`Scheme '${schemeId}' not found`);
  }
  return response.json();
}
