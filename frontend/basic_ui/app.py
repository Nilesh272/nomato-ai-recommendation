from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from phases.phase6_production_readiness.backend.api.routes import router as production_router

app = FastAPI(title="Zomato E2E UI", version="0.1.0")
app.include_router(production_router)


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Zomato AI Recommender - Basic UI</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 0; background: #f7f7f8; color: #202124; }
      .container { max-width: 1000px; margin: 24px auto; padding: 0 16px; }
      .card { background: #fff; border-radius: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); padding: 16px; margin-bottom: 16px; }
      h1 { margin: 0 0 8px; }
      .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
      label { display: block; font-size: 13px; margin-bottom: 6px; color: #444; }
      input, select { width: 100%; padding: 10px; border: 1px solid #d0d0d0; border-radius: 8px; }
      /* Use input + datalist for location to avoid blank multi-row select issues */
      #location { background: #fff; }
      button { background: #ef4f5f; color: white; border: 0; padding: 11px 16px; border-radius: 8px; cursor: pointer; font-weight: 600; }
      button:disabled { opacity: .6; cursor: not-allowed; }
      .row { display: flex; gap: 10px; align-items: center; }
      .meta { font-size: 13px; color: #666; }
      .pill { display:inline-block; background:#f2f2f2; border-radius: 999px; padding:4px 8px; font-size: 12px; }
      .error { color: #b00020; font-size: 14px; }
      .ok { color: #0b8043; font-size: 14px; }
      .rec h3 { margin: 0 0 6px; }
      .rec p { margin: 6px 0; }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="card">
        <h1>Zomato AI Recommender</h1>
        <p class="meta">Basic end-to-end UI (Phase 1-6 backend integration)</p>
      </div>

      <div class="card">
        <form id="recommendation-form">
          <div class="grid">
            <div>
              <label>Location</label>
              <input id="location" list="locations-list" placeholder="Start typing to search…" required />
              <datalist id="locations-list"></datalist>
              <div class="meta" id="location-status"></div>
            </div>
            <div>
              <label>Budget (INR for two)</label>
              <div class="row">
                <input id="budget_min" type="number" min="0" placeholder="min" value="500" />
                <input id="budget_max" type="number" min="0" placeholder="max (optional)" value="1500" />
              </div>
            </div>
            <div>
              <label>Cuisines (comma separated)</label>
              <input id="cuisines" value="North Indian, Chinese" />
            </div>
            <div>
              <label>Additional Preferences (comma separated)</label>
              <input id="additional_preferences" value="quick service, family friendly" />
            </div>
            <div>
              <label>Minimum Rating</label>
              <input id="min_rating" type="number" min="0" max="5" step="0.1" value="4.0" />
            </div>
            <div>
              <label>Sort Mode</label>
              <select id="sort_mode">
                <option value="ai_ranked" selected>ai_ranked</option>
                <option value="cost_low_to_high">cost_low_to_high</option>
              </select>
            </div>
            <div>
              <label>Top K</label>
              <input id="top_k" type="number" min="1" max="10" value="5" />
            </div>
            <div>
              <label>Candidate limit</label>
              <input disabled value="Fixed internally" />
            </div>
          </div>
          <div style="margin-top:14px" class="row">
            <button id="submit-btn" type="submit">Get Recommendations</button>
            <span id="status" class="meta"></span>
          </div>
          <p id="error" class="error"></p>
        </form>
      </div>

      <div id="summary" class="card" style="display:none;"></div>
      <div id="results"></div>
    </div>

    <script>
      const form = document.getElementById("recommendation-form");
      const statusEl = document.getElementById("status");
      const errorEl = document.getElementById("error");
      const resultsEl = document.getElementById("results");
      const summaryEl = document.getElementById("summary");
      const submitBtn = document.getElementById("submit-btn");
      // Point UI requests to the Phase 6 backend when backend and UI run on different ports.
      const API_BASE = "http://127.0.0.1:8000";
      const locationStatusEl = document.getElementById("location-status");
      const locationListEl = document.getElementById("locations-list");

      async function loadLocations() {
        const input = document.getElementById("location");
        locationListEl.innerHTML = "";
        locationStatusEl.textContent = "Loading locations…";
        try {
          const resp = await fetch(`${API_BASE}/api/v1/locations`);
          if (!resp.ok) {
            const text = await resp.text();
            throw new Error(`locations API failed (${resp.status}): ${text.slice(0, 200)}`);
          }
          const data = await resp.json();
          const locations = data.locations || [];
          if (!locations.length) {
            locationStatusEl.textContent = "No locations returned from backend.";
            return;
          }
          locationListEl.innerHTML = locations.map(l => `<option value="${l}"></option>`).join("");
          if (locations.includes("Banashankari")) input.value = "Banashankari";
          else input.value = locations[0];
          locationStatusEl.textContent = `Loaded ${locations.length} locations.`;
        } catch (e) {
          locationStatusEl.textContent = `Failed to load locations: ${e.message}`;
          console.error(e);
        }
      }

      loadLocations();

      function parseCSV(value) {
        return value.split(",").map(v => v.trim()).filter(Boolean);
      }

      function render(data) {
        summaryEl.style.display = "block";
        summaryEl.innerHTML = `
          <div class="row" style="justify-content:space-between;">
            <div>
              <div class="ok">${data.message}</div>
              <div class="meta">request_id: ${data.request_id} | cached: ${data.cached} | fallback: ${data.fallback_used}</div>
            </div>
            <div class="pill">count: ${data.recommendations.length}</div>
          </div>
        `;
        resultsEl.innerHTML = "";

        if (!data.recommendations.length) {
          const emptyCard = document.createElement("div");
          emptyCard.className = "card";
          emptyCard.innerHTML = "<h3>No recommendations found</h3>";
          if (data.empty_state_suggestions?.length) {
            emptyCard.innerHTML += "<ul>" + data.empty_state_suggestions.map(x => `<li>${x.suggestion}</li>`).join("") + "</ul>";
          }
          resultsEl.appendChild(emptyCard);
          return;
        }

        data.recommendations.forEach((item) => {
          const card = document.createElement("div");
          card.className = "card rec";
          card.innerHTML = `
            <h3>#${item.rank} ${item.restaurant_name}</h3>
            <p><strong>Cuisine:</strong> ${item.cuisine}</p>
            <p><strong>Rating:</strong> ${item.rating}</p>
            <p><strong>Estimated Cost:</strong> ${item.estimated_cost}</p>
            <p><strong>AI Explanation:</strong> ${item.ai_generated_explanation}</p>
          `;
          resultsEl.appendChild(card);
        });
      }

      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        errorEl.textContent = "";
        summaryEl.style.display = "none";
        resultsEl.innerHTML = "";
        submitBtn.disabled = true;
        statusEl.textContent = "Loading...";

        const payload = {
          client_id: "ui-user",
          location: document.getElementById("location").value,
          budget_min: parseInt(document.getElementById("budget_min").value || "0", 10),
          budget_max: document.getElementById("budget_max").value ? parseInt(document.getElementById("budget_max").value, 10) : null,
          cuisines: parseCSV(document.getElementById("cuisines").value),
          min_rating: parseFloat(document.getElementById("min_rating").value || "0"),
          additional_preferences: parseCSV(document.getElementById("additional_preferences").value),
          max_results: 5,
          top_k: parseInt(document.getElementById("top_k").value || "5", 10),
          sort_mode: document.getElementById("sort_mode").value
        };

        try {
          const resp = await fetch(`${API_BASE}/api/v1/recommendations/production`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          });
          const data = await resp.json();
          if (!resp.ok) {
            throw new Error(data.detail || "Request failed");
          }
          render(data);
          statusEl.textContent = "Done";
        } catch (err) {
          errorEl.textContent = err.message;
          statusEl.textContent = "Failed";
        } finally {
          submitBtn.disabled = false;
        }
      });
    </script>
  </body>
</html>
"""

