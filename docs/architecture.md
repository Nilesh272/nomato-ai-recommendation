# AI-Powered Restaurant Recommendation System  
Detailed Phase-Wise Architecture

## 1) System Vision and Non-Goals

### Vision
Build a recommendation platform that combines:
- structured restaurant data filtering, and
- LLM-based reasoning/explanation

to produce relevant, personalized, and explainable restaurant suggestions.

### Primary outcomes
- Fast shortlist generation from real dataset
- Personalized ranking and natural-language justifications
- Consistent output format for UI/API clients

### Non-goals for MVP
- Real-time restaurant booking integration
- User login/profile history
- Multi-city live inventory feeds from third-party vendors

---

## 2) End-to-End Logical Architecture

### Core services
- **Data Ingestion Service**: pulls and preprocesses dataset from Hugging Face
- **Restaurant Catalog DB**: stores cleaned and indexed restaurant records
- **Recommendation API Service**: orchestration layer for request -> response
- **Candidate Retrieval Engine**: deterministic filtering and pre-ranking
- **LLM Ranking Service**: model prompt construction, invocation, parsing
- **Response Formatter**: converts internal output to UI-safe contract
- **Observability Stack**: logs, metrics, traces, error tracking

### Data flow (high-level)
1. ETL ingests and standardizes dataset into DB.
2. User submits preferences via UI/API.
3. API validates and normalizes preferences.
4. Retrieval engine creates filtered candidate set.
5. LLM service ranks top candidates and explains reasoning.
6. Formatter returns top recommendations with fixed schema.

---

## 3) Phase-Wise Detailed Architecture

## Phase 1: Data Ingestion and Modeling

### Objective
Create a reliable, repeatable pipeline that turns raw dataset entries into query-efficient restaurant records.

### Components
- **Dataset Connector**
  - Source: `https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation`
  - Pull mode: batch download for MVP
  - Version pinning: store source dataset revision/hash in metadata table
- **Schema Mapper**
  - Maps raw fields to canonical model:
    - `restaurant_id` (generated)
    - `name`
    - `city`
    - `area/locality`
    - `cuisines` (array/string normalized)
    - `avg_cost_for_two` (numeric)
    - `rating` (float)
    - `votes` (int, optional)
    - `tags` (derived features like family_friendly, quick_service if available)
- **Data Cleaner**
  - Missing value strategy:
    - Drop record if `name` or `city` absent
    - Impute or null-mark optional columns
  - Normalization:
    - currency symbols removal
    - numeric conversion
    - cuisine token standardization (`North Indian`, `north indian`, etc.)
- **Quality Validator**
  - Valid rating range check (0-5)
  - Cost outlier checks (negative, unrealistic values)
  - Duplicate detection (`name + locality + city`)
- **Loader**
  - Upsert into `restaurants` table
  - Create indexes on `city`, `rating`, `avg_cost_for_two`, `cuisines`
- **Run Metadata Store**
  - `etl_runs` table for run id, source version, counts, failures

### Storage schema (MVP)
- `restaurants`
- `etl_runs`
- `restaurant_features` (optional denormalized tags/features)

### Deliverables
- Re-runnable ETL job
- Data dictionary and canonical schema
- Data quality report per ETL run

### Exit criteria
- At least 95% rows pass quality checks
- Query latency under target for basic city/rating filter on indexed columns

---

## Phase 2: User Input and API Contract

### Objective
Build a strict, stable preference intake layer.

### Components
- **Frontend Input Module**
  - Fields:
    - location (required)
    - budget (numeric INR for two: min and optional max)
    - cuisine (single or multi-select)
    - minimum rating
    - additional preferences (free text + predefined tags)
- **Recommendation API Endpoint**
  - `POST /api/v1/recommendations`
- **Request Validator**
  - Schema validation
  - Enum validation for budget
  - Range check for rating (0.0-5.0)
  - Input sanitization for free-text fields
- **Preference Normalizer**
  - Supports numeric budgets directly (`budget_min`, optional `budget_max`)
  - (Legacy) can still map budget tiers to numeric bounds if tier is provided
  - Normalizes cuisine spellings/synonyms
  - Expands additional preferences to tag candidates where possible

### API request contract (example)
- `location: string`
- `budget_tier: string`
- `cuisines: string[]`
- `min_rating: number`
- `additional_preferences: string[]`
- `max_results: number` (default 5, cap 10)

### Deliverables
- Documented OpenAPI spec
- Backend validation + normalized preference object
- Frontend form with validation messages

### Exit criteria
- Invalid inputs receive clear `4xx` errors
- Valid inputs transformed into normalized query object consistently

---

## Phase 3: Candidate Retrieval and Deterministic Ranking

### Objective
Reduce search space to high-quality candidates before LLM call.

### Components
- **Filter Builder**
  - Hard filters:
    - `city == location`
    - `rating >= min_rating`
    - cost range from budget tier
  - Optional hard filter:
    - cuisine must intersect selected cuisines (configurable strictness)
- **Feature Match Engine**
  - Scores additional preference matches:
    - `family_friendly`, `quick_service`, etc.
  - Uses text tags and heuristic keyword matching for MVP
- **Pre-Ranker**
  - Weighted score example:
    - rating score (40%)
    - cuisine match score (30%)
    - budget fit score (20%)
    - preference tag score (10%)
- **Candidate Limiter**
  - Select top N (fixed internal limit) for LLM context
  - Ensures diversity (optional): avoid over-clustering by same locality/cuisine
- **Phase 3 LLM integration decision**
  - LLM provider for this project: **Groq LLM**
  - API key will be stored in a local `.env` file and loaded via environment variables

### Internal output contract
- `candidate_id`
- `name`
- `city`
- `cuisines`
- `rating`
- `avg_cost_for_two`
- `matched_signals` (e.g., "within budget", "cuisine match")
- `pre_rank_score`

### Deliverables
- Retrieval module with unit tests
- Deterministic shortlist endpoint output
- Explainable match signals attached to each candidate

### Exit criteria
- Candidate generation under 300ms on target dataset size
- 0 uncaught errors for missing/partial records

---

## Phase 4: LLM Ranking and Explanation Layer

### Objective
Use LLM to reorder shortlisted candidates and generate high-quality explanations.

### Components
- **Prompt Composer**
  - Sections:
    - system constraints (use only provided data)
    - user preference summary
    - shortlisted candidates in structured JSON
    - strict output schema requirement
- **LLM Invocation Adapter**
  - Provider abstraction (OpenAI/Anthropic/local model gateway)
  - Timeout, retry, and fallback behavior
  - Token usage accounting
- **Output Schema Enforcer**
  - Parse model output as JSON
  - Validate required fields per recommendation:
    - rank
    - restaurant_name
    - explanation
    - confidence or fit score (optional)
- **Safety and Hallucination Guard**
  - Reject outputs referencing non-existent restaurants/attributes
  - If invalid, trigger retry with stricter prompt or fallback to deterministic ranking

### Prompt constraints (must include)
- "Do not invent data."
- "Use only attributes in candidate list."
- "Return top K recommendations."
- "Each explanation: max 2-3 sentences."

### Deliverables
- Prompt templates and versioning strategy
- LLM service with robust parsing and fallback
- Structured output guaranteed for downstream UI

### Exit criteria
- >= 99% valid structured response rate after retry/fallback
- Average LLM latency within acceptable SLO for MVP

---

## Phase 5: Response Presentation and UX

### Objective
Render recommendation output clearly and consistently for end users.

### Current implementation plan
- Backend-first delivery for Phase 5 is prioritized now.
- Frontend website updates will be implemented in a later iteration after backend response formatting is stabilized.
  - Frontend stack: **Next.js (App Router) + Tailwind CSS**
  - UI direction: Zomato-style landing page aligned to provided reference screenshot:
    - Sticky **white header** with red Zomato logo + nav links
    - **Hero** with food background + centered logo + tagline
    - Single **pill search bar** (location + search) to keep UX clean; advanced filters behind a “Filters” toggle
    - Below-hero sections: category cards, popular localities, “Explore options near me” accordions, and a multi-column footer
  - Backend integration:
    - Next.js **BFF proxy routes** (recommended for local dev to avoid CORS):
      - `GET /api/locations` → Phase 6 `GET /api/v1/locations`
      - `POST /api/recommendations` → Phase 6 `POST /api/v1/recommendations/production`

### Components
- **Presentation Formatter**
  - Merges deterministic and LLM signals
  - Normalizes display formats:
    - cost as currency range
    - rating to fixed decimal
- **Frontend Results Module**
  - Card/list UI for top recommendations
  - Each card includes:
    - Restaurant Name
    - Cuisine
    - Rating
    - Estimated Cost
    - AI-generated explanation
  - Optional sort toggle: "AI ranked" vs "Cost low to high"
- **Empty/Edge State Handler**
  - No matches for strict filters
  - Offer relaxed-filter suggestions (lower min rating, wider budget)

### Deliverables
- Consistent response schema from API to UI
- Backend presentation formatter and API-ready card payload (current scope)
- Polished recommendation result screen (planned next, frontend iteration)
- Graceful no-result and error states

### Exit criteria
- No schema mismatches between backend and UI
- End-to-end request-to-render flow works for core scenarios

---

## Phase 6: Production Readiness, Monitoring, and Iteration

### Objective
Improve reliability, quality, and operational control.

### Components
- **Observability**
  - Structured logs:
    - request id
    - filters applied
    - candidate count
    - LLM latency/tokens
  - Metrics:
    - request success rate
    - p95 latency
    - fallback rate
    - no-result rate
- **Evaluation Framework**
  - Offline eval set with known good recommendations
  - Human evaluation rubric:
    - relevance
    - explanation quality
    - diversity
- **Caching**
  - Cache frequent query signatures:
    - `city + budget + cuisine + min_rating`
  - TTL-based invalidation
- **Resilience**
  - Circuit breaker for LLM provider outage
  - Deterministic ranking fallback path always available
- **Security and Governance**
  - API key management via env/secret manager
  - Basic request rate limiting
  - PII-safe logging policy

### Deliverables
- SLO dashboard
- Automated regression evaluation runs
- Runbook for outages and degraded mode

### Exit criteria
- Stable operation under expected traffic
- Measurable quality improvements iteration-over-iteration

---

## 4) Suggested Tech Stack (MVP)

### Backend
- Python + FastAPI
- Pandas for ETL
- SQLAlchemy + PostgreSQL/SQLite

### LLM layer
- Groq LLM via provider SDK adapter interface
- JSON schema-based output validation
- API key source: `.env` file (for example, `GROQ_API_KEY=...`)

### Frontend
- React (or simple template-based UI) with form + result cards

### Infra
- Dockerized services
- Optional Redis for cache
- Basic CI pipeline with tests and lint checks

---

## 5) Suggested Repository Structure

- `docs/`
  - `problemStatement.md`
  - `architecture.md`
- `data_pipeline/`
  - `ingest.py`
  - `clean.py`
  - `validate.py`
- `backend/`
  - `api/`
  - `services/retrieval/`
  - `services/llm/`
  - `schemas/`
- `frontend/`
  - `components/`
  - `pages/`
- `tests/`
  - `unit/`
  - `integration/`

---

## 6) Build Plan (Execution Sequence)

1. Implement ETL + canonical DB schema  
2. Build `POST /recommendations` with deterministic filtering only  
3. Add LLM ranking service and strict output parser  
4. Integrate frontend form + result display  
5. Add observability, fallback, and cache  
6. Run evaluation loop and tune scoring/prompt versions

---

## 7) Risks and Mitigations

- **Sparse or noisy dataset fields**
  - Mitigation: quality checks + null-safe retrieval logic
- **LLM hallucination**
  - Mitigation: strict prompt + output validation + hard fallback
- **Latency spikes**
  - Mitigation: shortlist before LLM + caching + timeout/retry caps
- **Inconsistent UX output**
  - Mitigation: versioned response schema and formatter

---

## 8) Definition of Done (MVP)

- User can submit all required preferences.
- System returns top recommendations with:
  - restaurant name
  - cuisine
  - rating
  - estimated cost
  - AI explanation
- Deterministic fallback works when LLM fails.
- Basic logs and latency metrics are available.
- Documentation includes API contract and architecture details.
