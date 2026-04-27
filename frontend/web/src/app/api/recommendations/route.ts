import { NextResponse } from "next/server";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE?.trim() || "http://127.0.0.1:8000";

export async function POST(req: Request) {
  const body = await req.text();
  const resp = await fetch(`${API_BASE}/api/v1/recommendations/production`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
  });
  const text = await resp.text();
  return new NextResponse(text, {
    status: resp.status,
    headers: { "Content-Type": resp.headers.get("Content-Type") || "application/json" },
  });
}

