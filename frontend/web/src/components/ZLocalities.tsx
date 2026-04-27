"use client";

import { useEffect, useMemo, useState } from "react";
import { fetchLocations } from "@/lib/api";

export function ZLocalities() {
  const [locations, setLocations] = useState<string[]>([]);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    fetchLocations()
      .then((locs) => setLocations(locs))
      .catch(() => setLocations([]));
  }, []);

  const shown = useMemo(() => {
    return expanded ? locations.slice(0, 24) : locations.slice(0, 6);
  }, [expanded, locations]);

  return (
    <section className="mx-auto mt-8 w-full max-w-6xl px-5">
      <div className="inline-flex flex-col gap-2">
        <div className="text-2xl font-extrabold tracking-tight text-zinc-950">
          Popular localities in and around Bengaluru
        </div>
        <div className="h-1 w-14 rounded-full bg-[#EF4F5F]" />
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-3">
        {shown.map((l) => (
          <div
            key={l}
            className="flex items-center justify-between rounded-xl bg-white px-4 py-4 shadow-sm ring-1 ring-black/5 transition hover:shadow-md"
          >
            <div>
              <div className="font-medium text-zinc-900">{l}</div>
              <div className="mt-0.5 text-xs text-zinc-500">
                {Math.floor(200 + (l.length * 37) % 1200)} places
              </div>
            </div>
            <div className="text-zinc-400">›</div>
          </div>
        ))}
        {locations.length > 6 ? (
          <button
            type="button"
            onClick={() => setExpanded((v) => !v)}
            className="rounded-xl bg-white px-4 py-4 text-left shadow-sm ring-1 ring-black/5 transition hover:shadow-md"
          >
            <div className="flex items-center justify-between">
              <div className="font-medium">{expanded ? "See less" : "See more"}</div>
              <div className="text-zinc-400">⌄</div>
            </div>
          </button>
        ) : null}
      </div>
    </section>
  );
}

