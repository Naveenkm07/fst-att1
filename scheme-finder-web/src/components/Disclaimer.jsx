import React from "react";

export default function Disclaimer({ t }) {
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
      </div>
    </footer>
  );
}
