import React from "react";

export default function Disclaimer({ t, onOpenCookieModal }) {
  return (
    <footer className="disclaimer-footer" role="contentinfo">
      <div className="disclaimer-content">
        <span className="disclaimer-icon" aria-hidden="true">⚠️</span>
        <p className="disclaimer-text">
          {t.disclaimerText ||
            "This tool gives guidance only. Verify eligibility and application details on official government portals."}
        </p>
      </div>
      <div className="disclaimer-author">
        <span>{t.collegeTag || "NHCE Bengaluru • Full Stack Technologies (AAT-1)"}</span>
        <span className="divider">•</span>
        <span>Naveen (1NH21CS...)</span>
        <span className="divider">•</span>
        <button
          type="button"
          onClick={onOpenCookieModal}
          className="disclaimer-cookie-btn"
          id="btn-footer-cookie-policy"
          aria-label={t.cookieFooterLink}
        >
          <span aria-hidden="true">🍪</span> {t.cookieFooterLink}
        </button>
      </div>
    </footer>
  );
}

