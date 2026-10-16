import React from "react";

const INDIAN_STATES = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
  "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
  "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
  "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
  "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
  "Andaman and Nicobar Islands", "Chandigarh",
  "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir",
  "Ladakh", "Lakshadweep", "Puducherry"
];

const CATEGORIES = [
  { value: "SC", key: "cat_SC" },
  { value: "ST", key: "cat_ST" },
  { value: "OBC", key: "cat_OBC" },
  { value: "General", key: "cat_General" },
  { value: "EWS", key: "cat_EWS" },
  { value: "Other", key: "cat_Other" },
];

const OCCUPATIONS = [
  { value: "student", key: "occ_student" },
  { value: "farmer", key: "occ_farmer" },
  { value: "daily_wage", key: "occ_daily_wage" },
  { value: "salaried", key: "occ_salaried" },
  { value: "self_employed", key: "occ_self_employed" },
  { value: "unemployed", key: "occ_unemployed" },
  { value: "homemaker", key: "occ_homemaker" },
  { value: "retired", key: "occ_retired" },
  { value: "other", key: "occ_other" },
];

export default function EligibilityForm({
  formData,
  onChange,
  onSubmit,
  onReset,
  loading,
  error,
  t,
}) {
  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit();
  };

  return (
    <section className="form-card" aria-labelledby="form-heading">
      <div className="form-header">
        <h2 id="form-heading">{t.formHeading}</h2>
        <p className="form-hint" id="form-hint-desc">{t.formHint}</p>
      </div>

      {error && (
        <div className="alert-error" role="alert">
          <span aria-hidden="true">⚠️</span>
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate className="questionnaire-form">
        {/* Age */}
        <div className="form-group">
          <label htmlFor="field-age" className="form-label">
            {t.ageLabel}
          </label>
          <input
            id="field-age"
            name="age"
            type="number"
            min="0"
            max="120"
            className="form-input"
            placeholder={t.agePlaceholder}
            value={formData.age !== "" && formData.age !== null ? formData.age : ""}
            onChange={(e) => onChange("age", e.target.value)}
            aria-describedby="form-hint-desc"
          />
        </div>

        {/* Annual Income */}
        <div className="form-group">
          <label htmlFor="field-income" className="form-label">
            {t.incomeLabel}
          </label>
          <input
            id="field-income"
            name="annual_income"
            type="number"
            min="0"
            step="5000"
            className="form-input"
            placeholder={t.incomePlaceholder}
            value={
              formData.annual_income !== "" && formData.annual_income !== null
                ? formData.annual_income
                : ""
            }
            onChange={(e) => onChange("annual_income", e.target.value)}
            aria-describedby="form-hint-desc"
          />
        </div>

        {/* State */}
        <div className="form-group">
          <label htmlFor="field-state" className="form-label">
            {t.stateLabel}
          </label>
          <select
            id="field-state"
            name="state"
            className="form-select"
            value={formData.state || ""}
            onChange={(e) => onChange("state", e.target.value || null)}
          >
            <option value="">{t.stateSelectPlaceholder}</option>
            {INDIAN_STATES.map((st) => (
              <option key={st} value={st}>
                {st}
              </option>
            ))}
          </select>
        </div>

        {/* Social Category */}
        <div className="form-group">
          <label htmlFor="field-category" className="form-label">
            {t.categoryLabel}
          </label>
          <select
            id="field-category"
            name="category"
            className="form-select"
            value={formData.category || ""}
            onChange={(e) => onChange("category", e.target.value || null)}
          >
            <option value="">{t.categorySelectPlaceholder}</option>
            {CATEGORIES.map((cat) => (
              <option key={cat.value} value={cat.value}>
                {t[cat.key] || cat.value}
              </option>
            ))}
          </select>
        </div>

        {/* Occupation */}
        <div className="form-group">
          <label htmlFor="field-occupation" className="form-label">
            {t.occupationLabel}
          </label>
          <select
            id="field-occupation"
            name="occupation"
            className="form-select"
            value={formData.occupation || ""}
            onChange={(e) => onChange("occupation", e.target.value || null)}
          >
            <option value="">{t.occupationSelectPlaceholder}</option>
            {OCCUPATIONS.map((occ) => (
              <option key={occ.value} value={occ.value}>
                {t[occ.key] || occ.value}
              </option>
            ))}
          </select>
        </div>

        {/* Action Buttons */}
        <div className="form-actions">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            id="btn-check-eligibility"
          >
            {loading ? t.checking : t.checkButton}
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onReset}
            disabled={loading}
            id="btn-reset-form"
          >
            {t.resetButton}
          </button>
        </div>
      </form>
    </section>
  );
}
