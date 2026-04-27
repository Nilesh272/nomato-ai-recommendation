export type LocationsResponse = { locations: string[] };

export type ProductionRequest = {
  client_id: string;
  location: string;
  budget_min: number;
  budget_max: number | null;
  cuisines: string[];
  min_rating: number;
  additional_preferences: string[];
  max_results: number;
  top_k: number;
  sort_mode: "ai_ranked" | "cost_low_to_high";
};

export type ProductionResponse = {
  request_id: string;
  cached: boolean;
  message: string;
  fallback_used: boolean;
  recommendations: Array<{
    rank: number;
    restaurant_id?: number | null;
    restaurant_name: string;
    city?: string | null;
    locality?: string | null;
    cuisine: string;
    rating: string;
    estimated_cost: string;
    votes?: number | null;
    tags?: string | null;
    ai_generated_explanation: string;
  }>;
  empty_state_suggestions: Array<{ suggestion: string }>;
};

export async function fetchLocations(): Promise<string[]> {
  const resp = await fetch(`/api/locations`, { cache: "no-store" });
  if (!resp.ok) throw new Error(`locations: ${resp.status}`);
  const data = (await resp.json()) as LocationsResponse;
  return data.locations || [];
}

export async function fetchRecommendations(
  payload: ProductionRequest,
): Promise<ProductionResponse> {
  const resp = await fetch(`/api/recommendations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = (await resp.json()) as ProductionResponse & { detail?: string };
  if (!resp.ok) throw new Error(data.detail || `request failed: ${resp.status}`);
  return data;
}

