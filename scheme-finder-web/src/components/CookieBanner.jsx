import React, { useState, useEffect } from "react";

export default function CookieBanner({ onOpenDetails, t }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    let timer;
    try {
      const consent = localStorage.getItem("scheme_finder_cookie_consent");
      if (!consent) {
        // Small delay for smooth entry animation after page load
        timer = setTimeout(() => setVisible(true), 600);
      }
    } catch {
      timer = setTimeout(() => setVisible(true), 600);
    }
    return () => clearTimeout(timer);
  }, []);


  if (!visible) return null;

  const handleAcceptAll = () => {
    try {
      localStorage.setItem("scheme_finder_cookie_consent", "all");
      localStorage.setItem(
        "scheme_finder_cookie_prefs",
        JSON.stringify({ essential: true, preferences: true, analytics: true })
      );
    } catch {
      // Ignore
    }
    setVisible(false);
  };

  const handleEssentialOnly = () => {
    try {
      localStorage.setItem("scheme_finder_cookie_consent", "essential");
      localStorage.setItem(
        "scheme_finder_cookie_prefs",
        JSON.stringify({ essential: true, preferences: false, analytics: false })
      );
    } catch {
      // Ignore
    }
    setVisible(false);
  };

  return (
    <aside
      className="cookie-banner-wrapper"
      role="region"
      aria-label={t.cookieBannerTitle}
    >
      <div className="cookie-banner-inner">
        <div className="cookie-banner-content">
          <span className="cookie-banner-icon" aria-hidden="true">🍪</span>
          <div className="cookie-banner-text-group">
            <h3 className="cookie-banner-title">{t.cookieBannerTitle}</h3>
            <p className="cookie-banner-desc">{t.cookieBannerText}</p>
          </div>
        </div>

        <div className="cookie-banner-actions">
          <button
            type="button"
            className="btn btn-cookie-link"
            onClick={onOpenDetails}
          >
            {t.cookieLearnMore}
          </button>
          <button
            type="button"
            className="btn btn-cookie-secondary"
            onClick={handleEssentialOnly}
          >
            {t.cookieEssentialOnly}
          </button>
          <button
            type="button"
            className="btn btn-cookie-primary"
            onClick={handleAcceptAll}
          >
            {t.cookieAcceptAll}
          </button>
        </div>
      </div>
    </aside>
  );
}
