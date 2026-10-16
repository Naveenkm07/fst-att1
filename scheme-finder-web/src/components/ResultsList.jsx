import React from "react";
import SchemeCard from "./SchemeCard";

export default function ResultsList({ results, onBack, lang, t }) {
  const eligibleSchemes = results.filter((r) => r.verdict === "eligible");
  const possiblyEligibleSchemes = results.filter(
    (r) => r.verdict === "possibly_eligible"
  );

  return (
    <section className="results-container" aria-labelledby="results-heading">
      <div className="results-header">
        <div>
          <h2 id="results-heading">{t.resultsTitle}</h2>
          <p className="results-summary">
            {results.length} {t.resultsCount}
          </p>
        </div>
        <button
          type="button"
          onClick={onBack}
          className="btn btn-outline"
          id="btn-modify-profile"
        >
          ← {t.recheckButton}
        </button>
      </div>

      {results.length === 0 ? (
        <div className="empty-results-box">
          <p>{t.noEligibleFound}</p>
          <button type="button" onClick={onBack} className="btn btn-primary">
            {t.recheckButton}
          </button>
        </div>
      ) : (
        <>
          {/* Group 1: Deterministically Eligible */}
          {eligibleSchemes.length > 0 && (
            <div className="scheme-group">
              <div className="group-header">
                <span className="group-badge eligible-count">
                  {eligibleSchemes.length}
                </span>
                <h3 className="group-title">{t.eligibleSectionTitle}</h3>
              </div>
              <div className="cards-grid">
                {eligibleSchemes.map((scheme) => (
                  <SchemeCard
                    key={scheme.scheme_id}
                    scheme={scheme}
                    lang={lang}
                    t={t}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Group 2: Possibly Eligible - Needs Details */}
          {possiblyEligibleSchemes.length > 0 && (
            <div className="scheme-group">
              <div className="group-header">
                <span className="group-badge possibly-count">
                  {possiblyEligibleSchemes.length}
                </span>
                <h3 className="group-title">
                  {t.possiblyEligibleSectionTitle}
                </h3>
              </div>
              <div className="cards-grid">
                {possiblyEligibleSchemes.map((scheme) => (
                  <SchemeCard
                    key={scheme.scheme_id}
                    scheme={scheme}
                    lang={lang}
                    t={t}
                  />
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </section>
  );
}
