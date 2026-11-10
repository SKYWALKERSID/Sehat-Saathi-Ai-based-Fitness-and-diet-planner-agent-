# Sehat Saathi — AI-Based Fitness & Diet Planner Agent

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML%20Ensemble-F7931E?logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-Plan%20Scoring-189AB4)](https://xgboost.readthedocs.io/)
[![FAISS](https://img.shields.io/badge/FAISS-Vector%20RAG-008080)](https://github.com/facebookresearch/faiss)
[![SQLite](https://img.shields.io/badge/SQLite-SQLAlchemy%20ORM-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)

**Sehat Saathi** is a full-stack AI Health, Fitness, and Clinical Nutrition Planner built with **Flask**, a **6-Model Machine Learning Ensemble**, **7 Domain-Specific Model Context Protocol (MCP) Servers**, and a **FAISS Vector Retrieval-Augmented Generation (RAG) Coach**.

It synthesizes user biometrics, clinical conditions, joint injuries, allergies, and real-time weather/hydration telemetry to generate personalized 4-meal daily nutrition plans, injury-safe 7-day workout schedules, 7/30/90-day weight trajectories, and interactive clinical coaching.

---

## Key Capabilities

### 1. Multi-Model Machine Learning Pipeline (`backend/ml_models/`)
Sehat Saathi trains and serves six specialized ML models serialized with `joblib`:
- **Model 1 — Fitness Goal Classifier (`goal_predictor.pkl`)**: `RandomForestClassifier` predicting optimal goal alignment (`Weight Loss`, `Muscle Gain`, `Fat Loss`, `Maintenance`, `Strength Training`) with probability confidence.
- **Model 2 — Calorie Requirement Regressor (`calorie_predictor.pkl`)**: `LinearRegression` blended with Mifflin-St Jeor BMR/TDEE equations for accurate daily caloric targets.
- **Model 3 — Collaborative Diet Recommender (`diet_knn.pkl`)**: `NearestNeighbors` (KNN) clustering user biometrics and activity profiles to suggest high-adherence dietary templates.
- **Model 4 — Multi-Horizon Progress Forecaster (`progress_predictors.pkl`)**: 7-day, 30-day, and 90-day weight trajectory regressors driven by caloric delta and weekly training frequency.
- **Model 5 — Plan Compatibility Scorer (`plan_scorer.pkl`)**: `XGBRegressor` scoring overall plan safety and adherence (`0–100`) across sleep, hydration, calorie delta, and injury/allergy constraints.
- **Model 6 — Clinical Health Risk Classifier (`health_risk_predictors.pkl`)**: Multi-target `DecisionTreeClassifier` flagging **Obesity Risk**, **Sedentary Risk**, and **Metabolic Risk**.

### 2. Seven Domain-Specific MCP Servers (`backend/mcp/`)
Every recommendation and telemetry action is powered by modular MCP tools and logged to the database audit trail (`MCPLogs`):
1. **Nutrition MCP (`backend/mcp/nutrition.py`)**: 24+ Indian and global whole foods with macro/micronutrient profiles, dietary tags (`Vegetarian`, `Vegan`, `Eggetarian`, `Jain`, `Keto`, `Low Carb`, `High Protein`, `Non-Vegetarian`), allergen flags (`dairy`, `gluten`, `peanuts`, `nuts`, `root-vegetable`), and smart food substitutions.
2. **Exercise MCP (`backend/mcp/exercise.py`)**: 20+ structured exercises with MET values, primary/secondary muscle targets, form instructions, common mistakes, AI coaching tips, and equipment alternatives.
3. **Weather MCP (`backend/mcp/weather.py`)**: Evaluates ambient temperature, humidity, and air quality to automatically swap outdoor high-heat sessions (`Running`, `HIIT`) for indoor alternatives (`Swimming`, `Rowing Machine`) or extend cold-weather warmups.
4. **Hydration MCP (`backend/mcp/hydration.py`)**: Computes dynamic daily water intake targets (`L/day`) from body weight, activity level, and weather heat index.
5. **Progress MCP (`backend/mcp/progress.py`)**: Audits historical biometric logs to compute weekly weight velocity (`kg/week`), hydration/sleep compliance percentages, and plateau/safety alerts.
6. **Health Standards MCP (`backend/mcp/health_knowledge.py`)**: Provides WHO/ACSM/ICMR clinical reference ranges for BMI, resting heart rate, blood pressure, fasting glucose, and macronutrient splits.
7. **FAISS Clinical RAG MCP (`backend/mcp/rag.py`)**: Indexes clinical sports-medicine and nutrition literature using `TfidfVectorizer` + `faiss.IndexFlatL2` (`rag/faiss/index.bin`) for semantic retrieval in the AI Health Coach.

### 3. Safety-First Injury & Medical Override Engine
- **Joint & Spine Protection (`backend/workouts/generator.py`)**:
  - *Knee Injury*: Automatically substitutes `Squats`, `Leg Press`, and `Running` with `Bird-Dog & Glute Bridge` and `Swimming`.
  - *Back / Spine Injury*: Replaces `Deadlift` and axial-load movements with `Dumbbell Rows` and supported `Leg Press`.
  - *Shoulder Injury*: Replaces `Overhead Press`, `Bench Press`, and `Pull-ups` with `Plank` and neutral-grip rows.
  - *Hypertension / Asthma*: Caps intensity, removes Valsalva-heavy `HIIT Circuit` spikes, and adds pacing advisories.
- **Strict Dietary & Allergen Filtering (`backend/diets/generator.py`)**:
  - Enforces strict boundaries for `Jain` (no root vegetables, eggs, or meat), `Vegan` (no dairy, eggs, or meat), `Vegetarian` (no eggs or meat), `Eggetarian`, `Keto`, `Low Carb`, and `High Protein` plans while stripping user-reported allergens (`Peanuts`, `Gluten`, `Dairy`, `Nuts`).

### 4. Interactive SaaS Dashboard & Deep Analytics Hub
- **Main Dashboard (`/dashboard`)**:
  - **3-Step Profile Wizard** for creating and switching between multiple profiles per account.
  - **Diet Plan Tab** with per-meal Nutrition Scores, macro progress bars, fiber estimates, and per-item food substitutions.
  - **Workout Plan Tab** with Monday–Sunday schedule switching, interactive **Mark Complete / Completed** persistence (`POST /api/workout/toggle`), dynamic training volume (`kg`), and form guides.
  - **Progress & Reports Tab** with 7/30/365-day filtering, Chart.js weight & goal projections, SVG sparklines, and Progress MCP insights.
  - **AI Health Coach Tab** connected to `/api/chatbot` (FAISS RAG + Gemini 2.5 Flash / OpenAI / Clinical Offline Engine) and ML Risk Badges.
- **ML & MCP Analytics Hub (`/analytics`)**:
  - 7-Day, 30-Day, and 90-Day ML Weight Forecast horizon chart.
  - Dual-axis **Hydration & Sleep Compliance** chart (`#lifestyleChart`).
  - Interactive **Nutrition MCP Food Logger** (`/api/nutrition-logs`) with automatic macro calculation per gram.
  - Interactive **Clinical Health Vitals Logger** (`/api/health-metrics`) for Blood Pressure, Heart Rate, and Blood Sugar.
  - Live **MCP Server Execution Audit Trail** (`/api/mcp-logs/<id>`).

---

## Project Architecture

```text
SEHAT SAATHI/
├── backend/
│   ├── __init__.py              # Flask Application Factory, SQLAlchemy & FAISS init
│   ├── routes.py                # Core web routes (/, /dashboard, /analytics, legal pages)
│   ├── auth/routes.py           # Authentication blueprint (/auth/login, /auth/signup, /auth/logout)
│   ├── profiles/routes.py       # Profile CRUD, ML+MCP orchestration, workout completion toggle
│   ├── analytics/routes.py      # Progress logs, ML forecast, Nutrition/Vitals/MCP log APIs
│   ├── chatbot/routes.py        # AI Health Coach API (FAISS RAG + Gemini/OpenAI/Offline synthesis)
│   ├── diets/generator.py       # Macro-partitioned, allergen-safe 4-meal diet generator
│   ├── workouts/generator.py    # Injury- & weather-aware 7-day workout generator
│   ├── mcp/                     # 7 Domain-Specific MCP Servers
│   │   ├── nutrition.py         # Nutrition lookup & food database
│   │   ├── exercise.py          # Exercise database & MET calculator
│   │   ├── weather.py           # Weather & outdoor/indoor override MCP
│   │   ├── hydration.py         # Dynamic hydration target calculator
│   │   ├── progress.py          # Biometric velocity & compliance analyzer
│   │   ├── health_knowledge.py  # Clinical reference standards
│   │   └── rag.py               # FAISS vector index builder & semantic retriever
│   └── ml_models/
│       ├── train.py             # Training pipeline for all 6 ML models
│       ├── predictor.py         # Model inference & fallback wrappers
│       └── *.pkl                # Serialized Scikit-Learn & XGBoost models
├── database/
│   ├── __init__.py              # DB init & programmatic seeding helpers
│   ├── db.py                    # SQLAlchemy instance
│   └── models/__init__.py       # 12 SQLAlchemy ORM models (User, Profile, FitnessGoals, etc.)
├── rag/faiss/                   # Persisted FAISS vector index, chunks.json & TF-IDF vectorizer
├── static/
│   ├── css/style.css            # Clean SaaS stylesheet
│   └── js/dashboard.js          # Frontend state, Chart.js, Workout Toggle & AI Coach logic
├── templates/
│   ├── base.html                # Master layout & navigation
│   ├── index.html               # Landing page
│   ├── dashboard.html           # 5-tab interactive dashboard & 3-step setup wizard
│   ├── analytics.html           # Deep ML & MCP telemetry hub
│   └── auth/                    # Login & Signup templates
├── populate_test_cases.py       # Populates 10 diverse test profiles & generates verification report
├── recommender.py               # Unified facade for programmatic ML + MCP plan generation
├── config.py                    # Environment & SQLite configuration
├── run.py                       # Application entry point
├── start.bat                    # One-click Windows setup & launcher
└── requirements.txt             # Python dependencies
```

---

## Quick Start

### Option A: One-Click Windows Launch
Run `start.bat` from the project root:
```powershell
.\start.bat
```
`start.bat` automatically creates `.venv`, installs dependencies, trains the ML models if needed, seeds the database and FAISS vector index, and launches the server at `http://127.0.0.1:5000`.

### Option B: Manual Terminal Setup
1. **Create and activate a virtual environment**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
2. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
3. **Train the 6 Machine Learning models**:
   ```powershell
   python backend/ml_models/train.py
   ```
4. **Build the FAISS index & seed the 10 verification profiles**:
   ```powershell
   python populate_test_cases.py
   ```
5. **Start the Flask server**:
   ```powershell
   python run.py
   ```
6. Open **`http://127.0.0.1:5000`** in your browser.

---

## Demo Account & Pre-Loaded Profiles

Running `python populate_test_cases.py` creates a ready-to-use demo account with **10 diverse profiles** spanning different goals, dietary rules, injuries, and medical conditions:

- **Email**: `demo@sehatsaathi.ai`
- **Password**: `demo1234`

| # | Profile Name | Goal | Diet Preference | Constraints / Medical / Injury |
| :- | :--- | :--- | :--- | :--- |
| 1 | **Alice Cooper** | Weight Loss | Non-Vegetarian | None |
| 2 | **Bob Marley** | Weight Gain | Non-Vegetarian | None |
| 3 | **Charlie Puth** | Muscle Building | High Protein | None |
| 4 | **Daisy Ridley** | General Fitness | Vegetarian | Knee injury, Peanuts allergy |
| 5 | **Ethan Hunt** | Weight Loss | Vegan | Asthma |
| 6 | **Fiona Gallagher** | General Fitness | Low Carb | Senior (68 yrs), Hypertension |
| 7 | **George Costanza** | Fat Loss | Non-Vegetarian | Lower back pain |
| 8 | **Hannah Baker** | Endurance | Jain | Strict Jain (no root vegetables/eggs/meat) |
| 9 | **Ian Somerhalder** | Muscle Building | High Protein | Shoulder injury, Gluten allergy |
| 10 | **Jack Reacher** | Strength Training | Keto | Ultra-low-carb ketogenic macro split |

---

## REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/profile` | Creates a profile, runs all 6 ML models + MCP generators, and persists plans. |
| `GET` | `/api/profiles` | Lists all profiles belonging to the authenticated user. |
| `GET` | `/api/profile/<id>` | Returns profile biometrics, ML goals/risks, weather/hydration MCP context, 4-meal diet, and 7-day workout plan. |
| `POST` | `/api/workout/toggle` | Toggles and persists exercise completion (`completed: true/false`) for a specific day and exercise index. |
| `POST` | `/api/progress` | Logs daily weight, water intake, sleep hours, calories consumed/burned, and syncs `HydrationRecords`. |
| `GET` | `/api/progress/<id>` | Returns chronological biometric progress history. |
| `GET` | `/api/progress/analyze/<id>` | Executes Progress MCP audit (weekly weight velocity, water/sleep compliance, alerts). |
| `GET` | `/api/progress/predict/<id>` | Executes ML Model 4 to forecast 7-day, 30-day, and 90-day weight trajectories. |
| `GET` | `/api/nutrition-logs/<id>` | Lists granular food logs recorded via the Nutrition MCP server. |
| `POST` | `/api/nutrition-logs` | Looks up a food item in Nutrition MCP, scales macros by serving grams, and logs the entry. |
| `GET` | `/api/health-metrics/<id>` | Lists clinical vitals (Blood Pressure, Heart Rate, Blood Sugar). |
| `POST` | `/api/health-metrics` | Logs a new clinical vitals entry for the active profile. |
| `GET` | `/api/mcp-logs/<id>` | Returns the audit trail of MCP tool invocations (`Nutrition`, `Weather`, `Progress`, `RAG`). |
| `POST` | `/api/chatbot` | Queries the FAISS RAG knowledge base + Health Standards MCP and synthesizes a coaching response. |
| `GET/POST` | `/api/feedback` | Saves and retrieves 1–5 star user plan ratings and review comments. |

---

## Optional Environment Variables (`.env`)

Sehat Saathi works 100% offline out of the box using its local FAISS vector index and clinical synthesis engine. To optionally enable cloud LLM completion in `/api/chatbot`, configure a `.env` file in the root directory:

```ini
SECRET_KEY=your-production-secret-key
GEMINI_API_KEY=your-optional-gemini-api-key
OPENAI_API_KEY=your-optional-openai-api-key
```

---

## Contact & License

- **Author / Maintainer**: Siddhesh (`siddhesh.jabalpur49697@gmail.com`)
- **Reports & Documentation**: See [`reports/`](reports/) for detailed system architecture and verification summaries ([`reports/test_results.md`](reports/test_results.md)).
