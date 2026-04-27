"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
} from "react";
import * as Collapsible from "@radix-ui/react-collapsible";
import { MapPin, Search } from "lucide-react";
import {
  fetchLocations,
  fetchRecommendations,
  type ProductionResponse,
} from "@/lib/api";
import { LocationCombobox } from "@/components/LocationCombobox";

function parseCSV(value: string): string[] {
  return value
    .split(",")
    .map((v) => v.trim())
    .filter(Boolean);
}

type SortMode = "ai_ranked" | "cost_low_to_high";

type SearchState = {
  locations: string[];
  location: string;
  query: string;
  minRating: string;
  budgetMin: string;
  budgetMax: string;
  topK: string;
  sortMode: SortMode;
  loading: boolean;
  error: string;
  result: ProductionResponse | null;
  locationsStatus: string;
  setLocation: (v: string) => void;
  setQuery: (v: string) => void;
  setMinRating: (v: string) => void;
  setBudgetMin: (v: string) => void;
  setBudgetMax: (v: string) => void;
  setTopK: (v: string) => void;
  setSortMode: (v: SortMode) => void;
  onSubmit: () => Promise<void>;
  clearResults: () => void;
};

const SearchCtx = createContext<SearchState | null>(null);

function useSearch() {
  const ctx = useContext(SearchCtx);
  if (!ctx) throw new Error("ZSearch components must be wrapped in <ZSearchProvider />");
  return ctx;
}

export function ZSearchProvider({ children }: { children: React.ReactNode }) {
  const [locations, setLocations] = useState<string[]>([]);
  const [location, setLocation] = useState("");
  const [query, setQuery] = useState("");
  // Keep numeric inputs as strings to avoid "can't type" issues in controlled
  // <input type="number"> across browsers while user is editing.
  const [minRating, setMinRating] = useState("4.0");
  const [budgetMin, setBudgetMin] = useState("500");
  const [budgetMax, setBudgetMax] = useState("1500");
  const [topK, setTopK] = useState("5");
  const [sortMode, setSortMode] = useState<SortMode>("ai_ranked");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const [result, setResult] = useState<ProductionResponse | null>(null);
  const [locationsStatus, setLocationsStatus] = useState<string>("Loading locations…");

  useEffect(() => {
    fetchLocations()
      .then((locs) => {
        setLocations(locs);
        setLocation(locs[0] || "");
        setLocationsStatus(`Loaded ${locs.length} locations`);
      })
      .catch((e) => {
        setLocations([]);
        // Allow user to type location even if locations API fails.
        setError(e instanceof Error ? e.message : "Failed to load locations");
        setLocationsStatus("Failed to load locations (check backend)");
      });
  }, []);

  const cuisines = useMemo(() => {
    // lightweight parsing: treat some query tokens as cuisines
    return parseCSV(query);
  }, [query]);

  const onSubmit = useCallback(async () => {
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const parsedMinRating = Math.max(
        0,
        Math.min(5, Number.parseFloat(minRating || "0") || 0),
      );
      const parsedBudgetMin = Math.max(0, Number.parseInt(budgetMin || "0", 10) || 0);
      const parsedBudgetMaxRaw = budgetMax.trim();
      const parsedBudgetMax =
        parsedBudgetMaxRaw.length > 0 ? Math.max(0, Number.parseInt(parsedBudgetMaxRaw, 10) || 0) : null;
      const parsedTopK = Math.max(1, Math.min(10, Number.parseInt(topK || "5", 10) || 5));

      const data = await fetchRecommendations({
        client_id: "nextjs-ui",
        location,
        budget_min: parsedBudgetMin,
        budget_max: parsedBudgetMax,
        cuisines,
        min_rating: parsedMinRating,
        additional_preferences: [],
        max_results: 5,
        top_k: parsedTopK,
        sort_mode: sortMode,
      });
      setResult(data);

      // After results land, scroll the user to them for a "single flow" UX.
      // Delay to allow React to paint the results section.
      setTimeout(() => {
        document.getElementById("results")?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 50);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }, [budgetMax, budgetMin, cuisines, location, minRating, sortMode, topK]);

  const clearResults = useCallback(() => {
    setError("");
    setResult(null);
  }, []);

  const value: SearchState = {
    locations,
    location,
    query,
    minRating,
    budgetMin,
    budgetMax,
    topK,
    sortMode,
    loading,
    error,
    result,
    locationsStatus,
    setLocation,
    setQuery,
    setMinRating,
    setBudgetMin,
    setBudgetMax,
    setTopK,
    setSortMode,
    onSubmit,
    clearResults,
  };

  return <SearchCtx.Provider value={value}>{children}</SearchCtx.Provider>;
}

export function ZSearchBar() {
  const {
    locations,
    location,
    query,
    minRating,
    budgetMin,
    budgetMax,
    topK,
    sortMode,
    loading,
    error,
    result,
    locationsStatus,
    setLocation,
    setQuery,
    setMinRating,
    setBudgetMin,
    setBudgetMax,
    setTopK,
    setSortMode,
    onSubmit,
    clearResults,
  } = useSearch();

  const [showAdvanced, setShowAdvanced] = useState(false);
  const advancedId = useId();

  return (
    <div className="text-zinc-900">
      {/* Zomato-like single pill search bar (no extra buttons) */}
      <div className="mx-auto w-full max-w-4xl rounded-2xl bg-white shadow-lg ring-1 ring-black/10">
        <div className="flex w-full items-center">
          <div className="flex w-[44%] items-center gap-2 px-4 py-3">
            <span className="text-[#E23744]" aria-hidden="true">
              <MapPin className="h-5 w-5" />
            </span>
            <LocationCombobox
              value={location}
              options={locations}
              placeholder={locations.length ? "Select location" : "Type location…"}
              onChange={setLocation}
            />
          </div>
          <div className="h-6 w-px bg-zinc-200" />
          <div className="flex flex-1 items-center gap-2 px-4 py-3">
            <span className="text-zinc-400" aria-hidden="true">
              <Search className="h-5 w-5" />
            </span>
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") onSubmit();
              }}
              placeholder="Search for restaurant, cuisine or a dish"
              className="w-full bg-transparent text-sm outline-none placeholder:text-zinc-400"
            />
          </div>
        </div>
      </div>

      <div className="mx-auto mt-3 flex max-w-4xl flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2 text-xs">
          {error ? (
            <span className="rounded-full bg-red-50 px-3 py-1 font-medium text-red-700 ring-1 ring-red-200">
              {error}
            </span>
          ) : result ? (
            <span className="rounded-full bg-emerald-50 px-3 py-1 font-medium text-emerald-700 ring-1 ring-emerald-200">
              {result.message}
            </span>
          ) : (
            <span className="rounded-full bg-white/70 px-3 py-1 font-medium text-zinc-700 ring-1 ring-black/10">
              {locationsStatus} • Tip: enter cuisines as comma-separated values
            </span>
          )}
          {loading ? (
            <span className="rounded-full bg-white/70 px-3 py-1 font-medium text-zinc-700 ring-1 ring-black/10">
              Fetching recommendations…
            </span>
          ) : null}
        </div>

        <div className="flex items-center gap-2">
          <Collapsible.Root open={showAdvanced} onOpenChange={setShowAdvanced}>
            <Collapsible.Trigger asChild>
              <button
                type="button"
                aria-controls={advancedId}
                className="rounded-lg bg-white/70 px-3 py-2 text-sm font-semibold text-zinc-800 ring-1 ring-black/10 hover:bg-white"
              >
                {showAdvanced ? "Hide filters" : "Filters"}
              </button>
            </Collapsible.Trigger>
          </Collapsible.Root>

          {result ? (
            <button
              type="button"
              onClick={clearResults}
              className="rounded-lg bg-white/70 px-3 py-2 text-sm font-semibold text-zinc-800 ring-1 ring-black/10 hover:bg-white"
            >
              Clear
            </button>
          ) : null}
          <button
            onClick={onSubmit}
            disabled={loading || !location}
            className="rounded-lg bg-[#EF4F5F] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#E23744] disabled:opacity-60"
          >
            {loading ? "Searching…" : "Search"}
          </button>
        </div>
      </div>

      <Collapsible.Root open={showAdvanced} onOpenChange={setShowAdvanced}>
        <Collapsible.Content
          id={advancedId}
          className="mx-auto mt-3 max-w-4xl overflow-hidden rounded-2xl bg-white/90 p-3 ring-1 ring-black/5 backdrop-blur data-[state=closed]:animate-none data-[state=open]:animate-none"
        >
          <div className="grid grid-cols-2 gap-2 md:grid-cols-5">
            <div className="rounded-xl border border-zinc-200 bg-white px-3 py-2">
              <div className="text-[11px] font-medium text-zinc-500">Min rating</div>
              <input
                type="number"
                min={0}
                max={5}
                step={0.1}
                value={minRating}
                onChange={(e) => setMinRating(e.target.value)}
                className="w-full bg-transparent text-sm outline-none"
              />
            </div>
            <div className="rounded-xl border border-zinc-200 bg-white px-3 py-2">
              <div className="text-[11px] font-medium text-zinc-500">Budget min</div>
              <input
                type="number"
                min={0}
                value={budgetMin}
                onChange={(e) => setBudgetMin(e.target.value)}
                className="w-full bg-transparent text-sm outline-none"
              />
            </div>
            <div className="rounded-xl border border-zinc-200 bg-white px-3 py-2">
              <div className="text-[11px] font-medium text-zinc-500">Budget max</div>
              <input
                type="number"
                min={0}
                value={budgetMax}
                onChange={(e) => setBudgetMax(e.target.value)}
                className="w-full bg-transparent text-sm outline-none"
              />
            </div>
            <div className="rounded-xl border border-zinc-200 bg-white px-3 py-2">
              <div className="text-[11px] font-medium text-zinc-500">Top K</div>
              <input
                type="number"
                min={1}
                max={10}
                value={topK}
                onChange={(e) => setTopK(e.target.value)}
                className="w-full bg-transparent text-sm outline-none"
              />
            </div>
            <div className="rounded-xl border border-zinc-200 bg-white px-3 py-2">
              <div className="text-[11px] font-medium text-zinc-500">Sort</div>
              <select
                value={sortMode}
                onChange={(e) => setSortMode(e.target.value as SortMode)}
                className="w-full bg-transparent text-sm outline-none"
              >
                <option value="ai_ranked">AI ranked</option>
                <option value="cost_low_to_high">Cost: low to high</option>
              </select>
            </div>
          </div>
        </Collapsible.Content>
      </Collapsible.Root>
    </div>
  );
}

export function ZSearchResults() {
  const { result, loading } = useSearch();

  if (loading) {
    return (
      <section id="results" className="mx-auto mt-6 w-full max-w-6xl px-5 pb-10">
        <div className="mx-auto max-w-4xl">
          <div className="mb-3 h-6 w-56 animate-pulse rounded bg-zinc-200/70" />
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div
                // eslint-disable-next-line react/no-array-index-key
                key={i}
                className="rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm"
              >
                <div className="h-5 w-2/3 animate-pulse rounded bg-zinc-200/70" />
                <div className="mt-2 h-4 w-1/2 animate-pulse rounded bg-zinc-200/50" />
                <div className="mt-3 h-4 w-full animate-pulse rounded bg-zinc-200/50" />
              </div>
            ))}
          </div>
        </div>
      </section>
    );
  }

  if (!result?.recommendations?.length) return null;

  const total = result.recommendations.length;

  function chipsFromTags(tags: string | null | undefined): string[] {
    if (!tags) return [];
    return tags
      .split(/[,\|]/g)
      .map((t) => t.trim())
      .filter(Boolean)
      .slice(0, 4);
  }

  return (
    <section id="results" className="mx-auto mt-8 w-full max-w-6xl px-5 pb-10">
      <div className="mx-auto max-w-4xl">
        <div className="mb-3 flex items-end justify-between gap-3">
          <div>
            <div className="text-lg font-semibold tracking-tight text-zinc-900">
              AI recommendations
            </div>
            <div className="mt-0.5 text-sm text-zinc-600">
              Showing {total} result{total === 1 ? "" : "s"}
            </div>
          </div>
          <div className="text-xs text-zinc-500">Tip: adjust filters for variety</div>
        </div>

        <div className="space-y-3">
        {result.recommendations.map((r) => (
          <div
            key={`${r.rank}-${r.restaurant_name}`}
            className="rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm transition hover:shadow-md"
          >
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full bg-[#EF4F5F]/10 px-2.5 py-1 text-xs font-semibold text-[#C61F2B]">
                    #{r.rank}
                  </span>
                  <div className="truncate text-base font-semibold text-zinc-900">
                    {r.restaurant_name}
                  </div>
                </div>

                <div className="mt-1 text-sm text-zinc-600">
                  {r.city ? <span className="font-medium text-zinc-700">{r.city}</span> : null}
                  {r.locality ? (
                    <span className="text-zinc-600">
                      {r.city ? " • " : ""}
                      {r.locality}
                    </span>
                  ) : null}
                </div>

                <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
                  <span className="rounded-full bg-zinc-100 px-2.5 py-1 font-medium text-zinc-700">
                    {r.cuisine}
                  </span>
                  <span className="rounded-full bg-zinc-100 px-2.5 py-1 font-medium text-zinc-700">
                    Rating: {r.rating}
                  </span>
                  <span className="rounded-full bg-zinc-100 px-2.5 py-1 font-medium text-zinc-700">
                    {r.estimated_cost}
                  </span>
                </div>

                {chipsFromTags(r.tags).length ? (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {chipsFromTags(r.tags).map((t) => (
                      <span
                        key={t}
                        className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700 ring-1 ring-emerald-200"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                ) : null}
              </div>

              <div className="flex flex-wrap items-center gap-2 text-xs text-zinc-500">
                {typeof r.restaurant_id === "number" ? (
                  <span className="rounded-full bg-white px-2.5 py-1 ring-1 ring-zinc-200">
                    ID: {r.restaurant_id}
                  </span>
                ) : null}
                {typeof r.votes === "number" ? (
                  <span className="rounded-full bg-white px-2.5 py-1 ring-1 ring-zinc-200">
                    Votes: {r.votes}
                  </span>
                ) : null}
              </div>
            </div>

            <div className="mt-3 rounded-xl bg-zinc-50 px-3 py-2 text-sm text-zinc-800 ring-1 ring-black/5">
              {r.ai_generated_explanation}
            </div>
          </div>
        ))}
        </div>
      </div>
    </section>
  );
}

export function ZSearch() {
  return (
    <ZSearchProvider>
      <ZSearchBar />
      <ZSearchResults />
    </ZSearchProvider>
  );
}
