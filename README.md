# Government Scheme Finder Bot 🏛️
**Full Stack Technologies Course Project (AAT-1)**  
**Author:** Naveen, Department of Computer Science & Engineering, New Horizon College of Engineering (NHCE), Bengaluru.

---

## 1. Project Overview
The **Government Scheme Finder Bot** is a full-stack, bilingual (English & Kannada) civic web application designed to help Indian citizens quickly discover and understand government welfare schemes they may qualify for. 

A citizen fills out a short, optional 5-question profile (Age, Annual Income, State/UT, Social Category, and Occupation). A deterministic eligibility engine computes matching schemes instantly. Citizens can then ask follow-up questions to an AI chatbot in **English** or **Kannada** (ಕನ್ನಡ).

> [!IMPORTANT]
> **Critical Architectural Rule:** The Large Language Model (Gemini) **never** decides or computes eligibility. Eligibility is calculated 100% deterministically by pure Python rule functions. The LLM is strictly restricted to explaining scheme benefits, rules, and portal links grounded solely in retrieved official records.

---

## 2. Features
- **Deterministic Eligibility Engine:** Pure rule engine matching age, income limits, state domicile, social category (SC/ST/OBC/General/EWS), and occupation without LLM hallucinations.
- **Support for Partial Profiles:** If fields are omitted, the engine categorizes schemes under *"May be eligible: add details"* and indicates exactly which fields are missing.
- **Bilingual Interface (English & Kannada):** Full dynamic i18n localization with instant language switching (`en` and `kn`).
- **Grounded Bilingual Assistant:** Follow-up chat powered by Google Gemini using the `google-genai` SDK, with automatic Kannada script detection via Unicode character data.
- **Official Portals Only:** Every scheme record links strictly to verified government domains (`myscheme.gov.in`, `scholarships.gov.in`, `pmjay.gov.in`, `sevasindhu.karnataka.gov.in`, etc.).
- **Responsive down to 360px:** Accessible, mobile-friendly UI crafted with plain CSS and semantic HTML, with no third-party CSS bloat.
- **Zero LocalStorage:** Stateless citizen privacy by design; no user profiling data is persisted in browser storage.

---

## 3. Tech Stack
| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | React 19 + Vite | Fast Single-Page Application (SPA) using plain CSS and modern vanilla Fetch API |
| **Localization** | Custom JSON i18n | `src/i18n/en.json` and `src/i18n/kn.json` |
| **Backend API** | FastAPI + Uvicorn | Python 3.11+ asynchronous REST API with Pydantic v2 data models |
| **Rule Engine** | Pure Python 3 | Deterministic rule evaluation (`<=`, `>=`, `==`, `in`) with zero external I/O |
| **Database** | MongoDB via pymongo | Document store for schemes collection with automatic JSON fallback |
| **AI / LLM** | Google Gemini | Official `google-genai` SDK with strict grounding instructions |
| **Configuration** | `python-dotenv` | Clean `.env` management with `.env.example` templates |
| **Testing** | pytest & Vite Build | Full backend unit and integration test suite; Vite production bundle |

---

## 4. Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                                  BROWSER (CITIZEN)                                |
|  React + Vite SPA (Plain CSS, Mobile-Responsive down to 360px, English/Kannada)    |
|                                                                                   |
|  [ Questionnaire Form ]            [ Results List ]           [ Chat Panel ]      |
|  (Age, Income, State, Cat, Occ)    (Eligible / Maybe)        (English & Kannada)  |
+--------------------------+------------------------------------------+-------------+
                           | fetch()                                  | fetch()
                           v                                          v
+-----------------------------------------------------------------------------------+
|                             FASTAPI BACKEND SERVER                                |
|                                                                                   |
|  POST /api/eligibility                           POST /api/chat                   |
|         |                                                |                        |
|         v                                                v                        |
|  +---------------------------+             +---------------------------+          |
|  |   ELIGIBILITY ENGINE      |             |     RETRIEVAL MODULE      |          |
|  |   (eligibility.py)        |             |     (retrieval.py)        |          |
|  |   Deterministic Rules:    |             |   - Filters candidates    |          |
|  |   <=, >=, ==, in          |             |   - Keyword token overlap |          |
|  |   (No LLM, No Halluc.)    |             |   - Top 5 candidate pool  |          |
|  +-------------+-------------+             +-------------+-------------+          |
|                |                                         |                        |
|                |                                         v                        |
|                |                           +---------------------------+          |
|                |                           |      CHAT MODULE          |          |
|                |                           |      (chat.py)            |          |
|                |                           |   - unicodedata lang det  |          |
|                |                           |   - Grounded prompt       |          |
|                |                           |   - google-genai SDK      |          |
|                |                           +-------------+-------------+          |
|                |                                         |                        |
|                +--------------------+                    v                        |
|                                     |          Google Gemini LLM                  |
|                                     v          (gemini-2.5-flash)                 |
|                        +---------------------------+                              |
|                        |      DATA LAYER           |                              |
|                        |      (db.py)              |                              |
|                        |  - MongoDB (pymongo)      |                              |
|                        |  - data/schemes.json (fb) |                              |
|                        +---------------------------+                              |
+-----------------------------------------------------------------------------------+
```

---

## 5. Repository Layout
```
scheme-finder/
  README.md                 # Complete documentation and setup guide
  .gitignore                # Excludes virtual environments, secrets, node_modules, and dist
  data/
    schemes.json            # Seed dataset with 7 official government schemes
  scheme-finder-api/
    app/
      __init__.py
      main.py               # FastAPI app, CORS middleware, routes
      models.py             # Pydantic v2 schemas and enums
      eligibility.py        # Pure deterministic rule engine (no DB/IO)
      retrieval.py          # Candidate scheme retrieval for chat
      chat.py               # Kannada detection, grounded prompt, Gemini call
      db.py                 # MongoDB connection with graceful file fallback
    scripts/
      __init__.py
      seed.py               # Loads data/schemes.json into MongoDB collection
    tests/
      __init__.py
      test_eligibility.py   # Unit tests for eligibility engine
      test_api.py           # FastAPI TestClient endpoint integration tests
    requirements.txt        # Python backend dependencies
    .env.example            # Environment variables template
  scheme-finder-web/
    src/
      App.jsx               # Main SPA view switcher and language manager
      api.js                # Native fetch client
      styles.css            # Responsive styles and design tokens
      components/
        EligibilityForm.jsx # 5-field questionnaire form
        ResultsList.jsx     # Grouped results (Eligible & May Be Eligible)
        SchemeCard.jsx      # Individual scheme card with badges & portal links
        ChatPanel.jsx       # Bilingual chat interface with sources
        Disclaimer.jsx      # Persistent official guidance notice
      i18n/
        en.json             # English translations
        kn.json             # Native Kannada translations
      main.jsx              # React DOM entrypoint
    package.json            # Node project configuration
    vite.config.js          # Vite build configuration
    index.html              # HTML shell with accessibility and SEO tags
```

> [!NOTE]
> **Files Dropped/Omitted:** The nested `scheme-finder-web/README.md` scaffolded by Vite was removed to keep documentation centralized in this root `README.md`.

---

## 6. Setup and Installation

### Prerequisites
- **Python 3.11+** installed
- **Node.js v18+** & **npm** installed
- **MongoDB** (optional local instance or free MongoDB Atlas cluster URI)
- **Google Gemini API Key** (from [Google AI Studio](https://aistudio.google.com/))

---

### Step 1: Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd scheme-finder-api
   ```
2. Create and activate a virtual environment (recommended):
   ```bash
   # Windows PowerShell
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your values:
   ```ini
   MONGO_URI=mongodb://localhost:27017/scheme_finder
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   CORS_ORIGINS=http://localhost:5173
   ```

---

### Step 2: Database Seeding
To populate MongoDB with official scheme data from `data/schemes.json`:
```bash
python scripts/seed.py
```
*Note:* If MongoDB is not running, the application will automatically fall back to reading `data/schemes.json` directly, ensuring uninterrupted evaluation and testing.

---

### Step 3: Run Backend Server
Start the Uvicorn development server:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

### Step 4: Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd ../scheme-finder-web
   ```
2. Install frontend dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Open your browser at `http://localhost:5173`.

---

## 7. API Reference & cURL Examples

### 1. Health Check
- **Endpoint:** `GET /api/health`
- **Description:** Verifies service health.
- **cURL:**
  ```bash
  curl -X GET http://localhost:8000/api/health
  ```
- **Response:**
  ```json
  {"status": "ok"}
  ```

---

### 2. Check Scheme Eligibility
- **Endpoint:** `POST /api/eligibility`
- **Description:** Deterministically evaluates citizen profile against all stored schemes.
- **cURL:**
  ```bash
  curl -X POST http://localhost:8000/api/eligibility \
    -H "Content-Type: application/json" \
    -d '{
      "age": 24,
      "annual_income": 120000,
      "state": "Karnataka",
      "category": "OBC",
      "occupation": "unemployed"
    }'
  ```
- **Response Example:**
  ```json
  [
    {
      "scheme_id": "yuva-nidhi-karnataka",
      "name": "Yuva Nidhi Scheme Karnataka",
      "name_kn": "ಯುವ ನಿಧಿ ಯೋಜನೆ ಕರ್ನಾಟಕ",
      "benefit": "Provides monthly unemployment assistance of Rs 3,000 for degree holders and Rs 1,500 for diploma holders who graduated in recent academic years.",
      "source_url": "https://sevasindhu.karnataka.gov.in",
      "verdict": "eligible",
      "missing_fields": []
    }
  ]
  ```

---

### 3. Get Scheme by ID
- **Endpoint:** `GET /api/schemes/{id}`
- **Description:** Retrieves full record of an individual scheme.
- **cURL:**
  ```bash
  curl -X GET http://localhost:8000/api/schemes/pm-kisan-samman-nidhi
  ```
- **Response Example:**
  ```json
  {
    "id": "pm-kisan-samman-nidhi",
    "name": "PM-KISAN Samman Nidhi",
    "name_kn": "ಪ್ರಧಾನ ಮಂತ್ರಿ ಕಿಸಾನ್ ಸಮ್ಮಾನ್ ನಿಧಿ ಯೋಜನೆ (ರೈತರಿಗೆ ಸಹಾಯಧನ)",
    "benefit": "Transfers income support of Rs 6,000 per year in three equal installments directly into the bank accounts of landholding farmer families.",
    "criteria": [
      {
        "field": "occupation",
        "op": "==",
        "value": "farmer"
      }
    ],
    "source_url": "https://pmkisan.gov.in",
    "last_verified": null,
    "status": "draft_unverified"
  }
  ```

---

### 4. Bilingual Grounded Chat
- **Endpoint:** `POST /api/chat`
- **Description:** Answers follow-up queries grounded strictly in stored records in detected language (EN or KN).
- **cURL (Kannada query):**
  ```bash
  curl -X POST http://localhost:8000/api/chat \
    -H "Content-Type: application/json" \
    -d '{
      "question": "ರೈತರಿಗೆ ಸರ್ಕಾರದಿಂದ ಯಾವ ಯೋಜನೆ ಇದೆ?",
      "profile": {"occupation": "farmer"}
    }'
  ```
- **Response Example:**
  ```json
  {
    "answer": "ರೈತರಿಗೆ ಪ್ರಧಾನ ಮಂತ್ರಿ ಕಿಸಾನ್ ಸಮ್ಮಾನ್ ನಿಧಿ (PM-KISAN) ಯೋಜನೆಯು ಲಭ್ಯವಿದೆ...",
    "language": "kn",
    "sources": ["https://pmkisan.gov.in"],
    "used_scheme_ids": ["pm-kisan-samman-nidhi"]
  }
  ```

---

## 8. UI Screenshots

### 1. Questionnaire Form (English View)
```
+-----------------------------------------------------------------------------------+
| 🏛️ Government Scheme Finder       [🌐 ಕನ್ನಡ]                                     |
| Discover government welfare schemes tailored to your profile                      |
+-----------------------------------------------------------------------------------+
|  Check Your Eligibility                                                           |
|  All 5 fields below are optional. Answering more details helps narrow down...     |
|                                                                                   |
|  Age (Years):                [ 22                      ]                          |
|  Annual Income (₹):          [ 180000                  ]                          |
|  State / UT:                 [ Karnataka             v ]                          |
|  Social Category:            [ OBC                   v ]                          |
|  Current Occupation:         [ Student               v ]                          |
|                                                                                   |
|  [ Check Eligibility ]   [ Reset Form ]                                           |
+-----------------------------------------------------------------------------------+
```

### 2. Grouped Eligibility Results
```
+-----------------------------------------------------------------------------------+
| Eligibility Results (3 schemes found)                       [← Modify Profile]    |
|                                                                                   |
| (1) Eligible Schemes                                                              |
| +-------------------------------------------------------------------------------+ |
| | Post Matric Scholarship for SC/ST/OBC Students               [ ELIGIBLE ]     | |
| | Provides financial assistance to cover compulsory non-refundable fees...      | |
| |                                                       [ Official Portal ↗ ]   | |
| +-------------------------------------------------------------------------------+ |
|                                                                                   |
| (2) May Be Eligible: Add Details                                                  |
| +-------------------------------------------------------------------------------+ |
| | Ayushman Bharat - PM-JAY                                [ MAY BE ELIGIBLE ]   | |
| | Offers cashless health insurance coverage up to Rs 5 lakh per family/year...  | |
| | ℹ️ Needs info on: annual income                                                | |
| |                                                       [ Official Portal ↗ ]   | |
| +-------------------------------------------------------------------------------+ |
+-----------------------------------------------------------------------------------+
```

### 3. Grounded Kannada Chatbot Interaction
```
+-----------------------------------------------------------------------------------+
| 💬 ಯೋಜನಾ ಸಹಾಯಕ (Scheme Assistant)                                                |
| ಯೋಜನೆಗಳ ಪ್ರಯೋಜನಗಳು ಮತ್ತು ನಿಯಮಗಳ ಬಗ್ಗೆ ಇಂಗ್ಲಿಷ್ ಅಥವಾ ಕನ್ನಡದಲ್ಲಿ ಪ್ರಶ್ನೆ ಕೇಳಿ      |
+-----------------------------------------------------------------------------------+
| [Scheme Bot]: ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ಸರ್ಕಾರಿ ಯೋಜನಾ ಸಹಾಯಕ...                         |
|                                                                                   |
|                     [Citizen]: ರೈತರಿಗೆ ಸರ್ಕಾರದಿಂದ ಯಾವ ಯೋಜನೆ ಇದೆ?                  |
|                                                                                   |
| [Scheme Bot]: ರೈತರಿಗಾಗಿ ಪ್ರಧಾನ ಮಂತ್ರಿ ಕಿಸಾನ್ ಸಮ್ಮಾನ್ ನಿಧಿ ಯೋಜನೆಯು ಲಭ್ಯವಿದೆ.       |
| ಈ ಯೋಜನೆಯಡಿ ಅರ್ಹ ರೈತ ಕುಟುಂಬಗಳಿಗೆ ವರ್ಷಕ್ಕೆ ₹6,000 ಆರ್ಥಿಕ ನೆರವು ದೊರೆಯುತ್ತದೆ.         |
| ಅಧಿಕೃತ ಮೂಲಗಳು: [pmkisan.gov.in ↗]                                                 |
|                                                                                   |
| [ ಯಾವುದೇ ಯೋಜನೆಯ ಬಗ್ಗೆ ಪ್ರಶ್ನೆ ಕೇಳಿ (ಕನ್ನಡ ಅಥವಾ English)...         ] [ ಕಳುಹಿಸಿ ]  |
+-----------------------------------------------------------------------------------+
```

---

## 9. Testing & Quality Assurance

### Backend Tests (pytest)
The backend test suite covers:
1. `test_all_criteria_met_returns_eligible`
2. `test_income_above_limit_returns_not_eligible`
3. `test_missing_income_returns_possibly_eligible`
4. `test_wrong_category_returns_not_eligible`
5. `test_unknown_operator_raises_value_error`
6. `test_empty_criteria_returns_eligible`
7. `test_missing_field_when_another_fails_returns_not_eligible`
8. `test_none_profile_returns_possibly_eligible_with_all_criteria_fields`
9. `/api/health` returns 200
10. `/api/eligibility` with negative age returns 422 Unprocessable Entity
11. `/api/eligibility` returns structured verdicts for citizen profiles
12. Unknown scheme ID returns 404 Not Found
13. Chatbot with mocked Gemini answers in Kannada for Kannada queries
14. Chatbot with no matching records returns safe ungrounded fallback message

Run the backend test suite:
```bash
cd scheme-finder-api
python -m pytest -v
```

### Frontend Build Validation
Verify that the frontend builds with zero syntax, JSX, or bundling errors:
```bash
cd scheme-finder-web
npm run build
```

---

## 10. Data Verification Note
> [!WARNING]
> **Important Disclaimer on Thresholds & Criteria:**  
> All income limits, age brackets, and eligibility thresholds in `data/schemes.json` are **placeholders** marked with `"status": "draft_unverified"` and `"last_verified": null`.  
> Before relying on these rules or submitting real applications, citizens and evaluators must verify the latest official guidelines, gazette notifications, and income limits on the respective official portal URLs (`source_url`). Do not present placeholder thresholds as legal facts.

---

## 11. Disclaimer
**This tool gives guidance only. Verify eligibility and application details on official government portals.**  
The Government Scheme Finder Bot is an academic project built for informational and educational purposes. Neither the application nor its developer guarantees scheme sanctions or approvals.

---

## 12. Future Work
- **Bhashini Voice Input & Output:** Integrate Government of India's [AI4Bharat / Bhashini API](https://bhashini.gov.in/) for native Kannada voice prompts and audio responses for rural and non-literate citizens.
- **Pan-India Language Expansion:** Add Hindi, Tamil, Telugu, and Marathi localization.
- **Admin Portal & Scheme CMS:** Role-based portal for welfare officers to update scheme quotas and eligibility rules with automated audit trails.
- **WhatsApp & SMS Bot Access:** Twilio / Gupshup WhatsApp bot integration enabling citizens without smartphones to query schemes via simple text messages.

---

## 13. Author & Acknowledgements
- **Student Name:** Naveen
- **College:** New Horizon College of Engineering (NHCE), Bengaluru
- **Course:** Full Stack Technologies (AAT-1)
- **Academic Year:** 2026
