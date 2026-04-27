# Zomato First Project

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
- `tests/phase1/`: Phase 1 unit tests
- `tests/phase2/`: Phase 2 API tests

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

