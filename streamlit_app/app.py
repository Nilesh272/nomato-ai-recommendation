"""Streamlit entrypoint for the production recommendation backend (Streamlit Cloud / self-hosted)."""

from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

import streamlit as st

# Repository root (Streamlit Cloud cwd is usually the repo root; this keeps imports stable if not).
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
os.chdir(_REPO_ROOT)

from phases.phase2_user_input_api.backend.schemas.recommendation import BudgetTier  # noqa: E402
from phases.phase6_production_readiness.backend.schemas.production import ProductionRequest  # noqa: E402
from phases.phase6_production_readiness.backend.services.production_pipeline import (  # noqa: E402
    DB_PATH,
    ProductionPipelineError,
    ProductionRateLimitError,
    run_production_recommendation,
)


def _apply_streamlit_secrets_to_environ() -> None:
    """Expose Streamlit Cloud / local secrets as env vars for Groq and optional config."""
    try:
        sec = st.secrets
    except Exception:
        return
    keys = ("GROQ_API_KEY", "GROQ_BASE_URL", "GROQ_MODEL", "GROQ_TRUST_ENV")
    for key in keys:
        if key in sec:
            os.environ[key] = str(sec[key])


def _load_locations() -> list[str]:
    if not DB_PATH.is_file():
        return []
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT city, COUNT(*) as cnt FROM restaurants GROUP BY city ORDER BY cnt DESC LIMIT 200"
        ).fetchall()
    finally:
        conn.close()
    return [r[0] for r in rows if r[0]]


def _parse_list(raw: str) -> list[str]:
    parts = [p.strip() for p in raw.replace("\n", ",").split(",")]
    return [p for p in parts if p]


def main() -> None:
    st.set_page_config(page_title="Zomato recommendations", layout="wide")
    _apply_streamlit_secrets_to_environ()

    st.title("Restaurant recommendations")
    st.caption("Production pipeline (Phase 6) — same logic as the FastAPI `/api/v1/recommendations/production` route.")

    if not DB_PATH.is_file():
        st.error(
            f"SQLite database not found at `{DB_PATH}`. "
            "Run Phase 1 ETL locally and commit or upload `zomato.db` for deployment."
        )
        st.stop()

    locations = _load_locations()

    with st.sidebar:
        st.subheader("Client")
        client_id = st.text_input("Client ID (rate limit key)", value="streamlit-user")

    with st.form("prefs"):
        c1, c2 = st.columns(2)
        with c1:
            if locations:
                loc_idx = locations.index("Bangalore") if "Bangalore" in locations else 0
                location = st.selectbox("Location", options=locations, index=loc_idx)
            else:
                location = st.text_input("Location", value="Bangalore")
            min_rating = st.slider("Minimum rating", 0.0, 5.0, 3.5, 0.1)
            top_k = st.number_input("Top K (ranked)", min_value=1, max_value=10, value=5)
            max_results = st.number_input("Max results (shortlist)", min_value=1, max_value=10, value=5)
        with c2:
            budget_tier_raw = st.selectbox("Budget tier (optional)", options=["(none)", "low", "medium", "high"])
            budget_min = st.number_input("Budget min (INR for two, optional)", min_value=0, value=0)
            budget_max = st.number_input("Budget max (INR for two, 0 = omit)", min_value=0, value=0)
            sort_mode = st.selectbox("Sort mode", options=["ai_ranked", "cost"], index=0)

        cuisines_raw = st.text_input("Cuisines (comma-separated)", value="North Indian")
        prefs_raw = st.text_input("Additional preferences (comma-separated)", value="")

        submitted = st.form_submit_button("Get recommendations")

    if not submitted:
        return

    budget_tier: BudgetTier | None = None
    if budget_tier_raw != "(none)":
        budget_tier = BudgetTier(budget_tier_raw)

    payload = ProductionRequest(
        client_id=client_id.strip() or "anonymous",
        location=location.strip(),
        budget_min=int(budget_min) if budget_min > 0 else None,
        budget_max=int(budget_max) if budget_max > 0 else None,
        budget_tier=budget_tier,
        cuisines=_parse_list(cuisines_raw),
        min_rating=float(min_rating),
        additional_preferences=_parse_list(prefs_raw),
        max_results=int(max_results),
        top_k=int(top_k),
        sort_mode=sort_mode,
    )

    with st.spinner("Ranking restaurants…"):
        try:
            result = run_production_recommendation(payload)
        except ProductionRateLimitError:
            st.error("Rate limit exceeded. Wait a minute and try again.")
            return
        except ProductionPipelineError as exc:
            st.error(str(exc))
            return

    st.subheader("Results")
    meta = f"request_id={result.request_id} · cached={result.cached} · fallback_used={result.fallback_used}"
    st.caption(meta)
    if result.message:
        st.info(result.message)

    if not result.recommendations:
        st.warning("No recommendations returned.")
        for item in result.empty_state_suggestions:
            st.write(f"- {item.suggestion}")
        return

    for rec in result.recommendations:
        with st.expander(f"#{rec.sort_key_ai_rank} · {rec.restaurant_name} · {rec.rating} · {rec.estimated_cost}"):
            st.markdown(f"**{rec.cuisine}** · {rec.locality or rec.city or ''}")
            st.write(rec.ai_generated_explanation)


main()
