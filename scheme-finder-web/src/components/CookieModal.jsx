import React, { useState, useEffect } from "react";

export default function CookieModal({ isOpen, onClose, onSave, t }) {
  const [preferences, setPreferences] = useState(() => {
    try {
      const saved = localStorage.getItem("scheme_finder_cookie_prefs");
      if (saved) {
        return JSON.parse(saved);
      }
    } catch {
      // Ignore localStorage errors in private browsing
    }
    return {
      essential: true,
      preferences: true,
      analytics: false,
    };
  });


  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleSave = () => {
    try {
      localStorage.setItem("scheme_finder_cookie_prefs", JSON.stringify(preferences));
      localStorage.setItem("scheme_finder_cookie_consent", "customized");
    } catch {
      // Ignore
    }
    if (onSave) onSave(preferences);
    onClose();
  };

  const handleAcceptAll = () => {
    const all = { essential: true, preferences: true, analytics: true };
    try {
      localStorage.setItem("scheme_finder_cookie_prefs", JSON.stringify(all));
      localStorage.setItem("scheme_finder_cookie_consent", "all");
    } catch {
      // Ignore
    }
    if (onSave) onSave(all);
    onClose();
  };

  return (
    <div className="cookie-modal-backdrop" onClick={onClose} role="presentation">
      <div
        className="cookie-modal-card"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="cookie-modal-title"
      >
        <div className="cookie-modal-header">
          <div className="cookie-modal-title-group">
            <span className="cookie-modal-icon" aria-hidden="true">🍪</span>
            <div>
              <h2 id="cookie-modal-title" className="cookie-modal-title">
                {t.cookieModalTitle}
              </h2>
              <span className="dpdp-badge">{t.cookieModalSubtitle}</span>
            </div>
          </div>
          <button
            type="button"
            className="cookie-modal-close-btn"
            onClick={onClose}
            aria-label={t.cookieClose}
          >
            ✕
          </button>
        </div>

        <div className="cookie-modal-body">
          {/* Citizen Privacy Guarantee Callout */}
          <div className="citizen-privacy-callout">
            <div className="callout-badge">
              <span aria-hidden="true">🛡️</span> {t.cookiePledgeTitle}
            </div>
            <p className="callout-text">{t.cookiePledgeText}</p>
          </div>

          {/* Category 1: Essential */}
          <div className="cookie-category-box">
            <div className="cookie-category-header">
              <div className="cookie-category-info">
                <span className="category-name">{t.cookieEssentialTitle}</span>
                <span className="badge-active-pill">Always Active</span>
              </div>
              <input
                type="checkbox"
                checked={true}
                disabled={true}
                aria-label={t.cookieEssentialTitle}
                className="cookie-toggle-checkbox"
              />
            </div>
            <p className="cookie-category-desc">{t.cookieEssentialDesc}</p>
          </div>

          {/* Category 2: Preferences */}
          <div className="cookie-category-box">
            <div className="cookie-category-header">
              <div className="cookie-category-info">
                <span className="category-name">{t.cookiePrefsTitle}</span>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={preferences.preferences}
                  onChange={(e) =>
                    setPreferences((prev) => ({
                      ...prev,
                      preferences: e.target.checked,
                    }))
                  }
                  aria-label={t.cookiePrefsTitle}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
            <p className="cookie-category-desc">{t.cookiePrefsDesc}</p>
          </div>

          {/* Category 3: Analytics */}
          <div className="cookie-category-box">
            <div className="cookie-category-header">
              <div className="cookie-category-info">
                <span className="category-name">{t.cookieAnalyticsTitle}</span>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={preferences.analytics}
                  onChange={(e) =>
                    setPreferences((prev) => ({
                      ...prev,
                      analytics: e.target.checked,
                    }))
                  }
                  aria-label={t.cookieAnalyticsTitle}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
            <p className="cookie-category-desc">{t.cookieAnalyticsDesc}</p>
          </div>
        </div>

        <div className="cookie-modal-footer">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onClose}
          >
            {t.cookieClose}
          </button>
          <button
            type="button"
            className="btn btn-outline"
            onClick={handleSave}
          >
            {t.cookieSavePreferences}
          </button>
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleAcceptAll}
          >
            {t.cookieAcceptAll}
          </button>
        </div>
      </div>
    </div>
  );
}
