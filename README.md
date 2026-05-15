# Zomato First Project

![Nomato AI Restaurant Recommendation System](https://res.cloudinary.com/dc1wq21mk/image/upload/q_auto/f_auto/v1778840723/Screenshot_2026-05-15_at_3.50.47_PM_enclkx.png)

Implemented phases:
- Phase 1: data ingestion and modeling
- Phase 2: user input API contract, validation, and normalization
- Phase 3: candidate retrieval and deterministic pre-ranking
- Phase 4: Groq LLM ranking, explanations, and fallback handling
- Phase 5: backend presentation formatter for UI-ready response cards
- Phase 6: production readiness (metrics, cache, rate limiting, resilience)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Project structure

- `phases/phase1_data_ingestion/`: dataset ETL, cleaning, validation, SQLite loading
- `phases/phase2_user_input_api/`: FastAPI service for preference intake and normalization
- `streamlit_app/`: Streamlit deployment for the Phase 6 production pipeline (same logic as FastAPI)
- `tests/phase1/`: Phase 1 unit tests
- `tests/phase2/`: Phase 2 API tests

## Architecture

### Deployment

- **Backend:** [Streamlit](https://streamlit.io) (for example [Streamlit Community Cloud](https://streamlit.io/cloud) or self-hosted), where the Python-side recommendation and serving logic runs.
- **Frontend:** [Vercel](https://vercel.com), deploying the Next.js app under `frontend/web`.

On [Streamlit Community Cloud](https://streamlit.io/cloud), set the app’s main file to `streamlit_app/app.py`, install dependencies from `requirements.txt`, and add **Secrets** for `GROQ_API_KEY` (optional: `GROQ_MODEL`, `GROQ_BASE_URL`). The app reads `phases/phase1_data_ingestion/data_pipeline/zomato.db`; build it with Phase 1 ETL or supply the file in the deployment environment.

The Next.js app’s `NEXT_PUBLIC_API_BASE` targets a **REST** service (`POST /api/v1/recommendations/production`). Use the Phase 6 FastAPI app for that, or another HTTP host; Streamlit serves the Python stack through the Streamlit UI, not as that JSON endpoint.

## Run Phase 1 ETL

```bash
HF_HOME="./.hf_cache" python -m phases.phase1_data_ingestion.data_pipeline.run_etl
```

Optional flags:

```bash
HF_HOME="./.hf_cache" python -m phases.phase1_data_ingestion.data_pipeline.run_etl \
  --dataset-name ManikaSaini/zomato-restaurant-recommendation \
  --split train \
  --db-path phases/phase1_data_ingestion/data_pipeline/zomato.db
```

## Run Phase 2 API

```bash
uvicorn phases.phase2_user_input_api.backend.main:app --reload
```

OpenAPI docs will be available at:
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`

## Run Phase 3 API

```bash
uvicorn phases.phase3_candidate_retrieval.backend.main:app --reload
```

Phase 3 endpoint:
- `POST /api/v1/recommendations/shortlist`

## Run Phase 4 API

```bash
uvicorn phases.phase4_llm_ranking.backend.main:app --reload
```

Phase 4 endpoint:
- `POST /api/v1/recommendations/final`

## Run Phase 5 API

```bash
uvicorn phases.phase5_response_presentation.backend.main:app --reload
```

Phase 5 endpoint:
- `POST /api/v1/recommendations/present`

## Run Phase 6 API

```bash
uvicorn phases.phase6_production_readiness.backend.main:app --reload
```

Phase 6 endpoints:
- `POST /api/v1/recommendations/production`
- `GET /api/v1/metrics`

## Run Streamlit (production backend)

Uses the same production pipeline as Phase 6 (`run_production_recommendation`). For local secrets, use a root `.env` with `GROQ_API_KEY` (as used by the Groq client) or configure [Streamlit secrets](https://docs.streamlit.io/develop/concepts/connections/secrets-management).

```bash
streamlit run streamlit_app/app.py
```

## Run Basic End-to-End UI

```bash
uvicorn frontend.basic_ui.app:app --reload
```

Open:
- `http://127.0.0.1:8000/`

This basic UI calls:
- `POST /api/v1/recommendations/production`

## Run Next.js Frontend (Zomato-like)

```bash
cd frontend/web
cp .env.local.example .env.local
npm run dev
```

Open:
- `http://localhost:3000`

## Run tests

```bash
pytest -q
```

