import React from "react";

export default function SchemeCard({ scheme, lang, t }) {
  const isKannada = lang === "kn";
  const displayName = isKannada && scheme.name_kn ? scheme.name_kn : scheme.name;
  const isEligible = scheme.verdict === "eligible";

  // Field translation map
  const fieldNames = {
    age: t.fieldAge || "age",
    annual_income: t.fieldIncome || "annual income",
    state: t.fieldState || "state",
    category: t.fieldCategory || "social category",
    occupation: t.fieldOccupation || "occupation",
  };

  const readableMissing = (scheme.missing_fields || [])
    .map((f) => fieldNames[f] || f)
    .join(", ");

  return (
    <article
      className={`scheme-card ${isEligible ? "card-eligible" : "card-possibly-eligible"}`}
      aria-labelledby={`scheme-title-${scheme.scheme_id}`}
    >
      <div className="card-top">
        <h3 id={`scheme-title-${scheme.scheme_id}`} className="scheme-title">
          {displayName}
        </h3>
        <span
          className={`badge ${isEligible ? "badge-success" : "badge-warning"}`}
        >
          {isEligible ? t.badgeEligible : t.badgePossiblyEligible}
        </span>
      </div>

      {/* Secondary English title if displaying Kannada */}
      {isKannada && scheme.name_kn && (
        <p className="scheme-subtitle-en">{scheme.name}</p>
      )}

      <p className="scheme-benefit">{scheme.benefit}</p>

      {!isEligible && scheme.missing_fields && scheme.missing_fields.length > 0 && (
        <div className="missing-fields-hint">
          <span className="hint-icon" aria-hidden="true">ℹ️</span>
          <span>
            <strong>{t.missingFieldsHint}</strong> {readableMissing}
          </span>
        </div>
      )}

      <div className="card-footer">
        <a
          href={scheme.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="link-official-portal"
          aria-label={`${t.officialWebsiteLink} for ${scheme.name} (opens in new tab)`}
        >
          <span>{t.officialWebsiteLink}</span>
          <span aria-hidden="true" className="external-icon">↗</span>
        </a>
      </div>
    </article>
  );
}
