import React, { useState } from "react";
import EligibilityForm from "./components/EligibilityForm";
import ResultsList from "./components/ResultsList";
import ChatPanel from "./components/ChatPanel";
import Disclaimer from "./components/Disclaimer";
import CookieBanner from "./components/CookieBanner";
import CookieModal from "./components/CookieModal";
import enTranslations from "./i18n/en.json";
import knTranslations from "./i18n/kn.json";
import { checkEligibility } from "./api";

const INITIAL_FORM_DATA = {
  age: "",
  annual_income: "",
  state: null,
  category: null,
  occupation: null,
};

export default function App() {
  const [lang, setLang] = useState("en"); // 'en' or 'kn'
  const [currentView, setCurrentView] = useState("form"); // 'form' or 'results'
  const [formData, setFormData] = useState(INITIAL_FORM_DATA);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isCookieModalOpen, setIsCookieModalOpen] = useState(false);

  const t = lang === "kn" ? knTranslations : enTranslations;

  const handleFieldChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleReset = () => {
    setFormData(INITIAL_FORM_DATA);
    setResults([]);
    setError(null);
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);

    // Build payload with numbers parsed or null
    const payload = {};
    if (formData.age !== "" && formData.age !== null) {
      payload.age = parseInt(formData.age, 10);
    }
    if (formData.annual_income !== "" && formData.annual_income !== null) {
      payload.annual_income = parseInt(formData.annual_income, 10);
    }
    if (formData.state) {
      payload.state = formData.state;
    }
    if (formData.category) {
      payload.category = formData.category;
    }
    if (formData.occupation) {
      payload.occupation = formData.occupation;
    }

    try {
      const data = await checkEligibility(payload);
      setResults(data);
      setCurrentView("results");
    } catch (err) {
      console.error("Eligibility check error:", err);
      setError(err.message || t.errorCheck);
    } finally {
      setLoading(false);
    }
  };

  const toggleLanguage = () => {
    setLang((prev) => (prev === "en" ? "kn" : "en"));
  };

  return (
    <div className="app-layout">
      {/* Top Navigation & Language Toggle */}
      <header className="app-header" role="banner">
        <div className="header-inner">
          <div className="brand-group">
            <span className="app-emblem" aria-hidden="true">🏛️</span>
            <div>
              <h1 className="app-title">{t.appTitle}</h1>
              <p className="app-subtitle">{t.appSubtitle}</p>
            </div>
          </div>

          <div className="header-controls">
            <button
              type="button"
              onClick={toggleLanguage}
              className="btn btn-lang-toggle"
              aria-label={`Switch language to ${lang === "en" ? "Kannada" : "English"}`}
              id="btn-lang-toggle"
            >
              <span className="globe-icon" aria-hidden="true">🌐</span>
              <span className="lang-name">{lang === "en" ? "ಕನ್ನಡ" : "English"}</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="main-content" role="main">
        {currentView === "form" ? (
          <div className="view-container view-form">
            <EligibilityForm
              formData={formData}
              onChange={handleFieldChange}
              onSubmit={handleSubmit}
              onReset={handleReset}
              loading={loading}
              error={error}
              t={t}
            />
          </div>
        ) : (
          <div className="view-container view-results">
            <div className="results-and-chat-grid">
              <div className="results-column">
                <ResultsList
                  results={results}
                  onBack={() => setCurrentView("form")}
                  lang={lang}
                  t={t}
                />
              </div>
              <div className="chat-column">
                <ChatPanel
                  profile={formData}
                  lang={lang}
                  t={t}
                />
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Mandatory Disclaimer Footer */}
      <Disclaimer
        t={t}
        onOpenCookieModal={() => setIsCookieModalOpen(true)}
      />

      {/* Modern Cookie Notice & Consent Banner */}
      <CookieBanner
        onOpenDetails={() => setIsCookieModalOpen(true)}
        t={t}
      />

      {/* Full Cookie & Civic Privacy Policy Modal */}
      <CookieModal
        isOpen={isCookieModalOpen}
        onClose={() => setIsCookieModalOpen(false)}
        t={t}
      />
    </div>
  );
}

