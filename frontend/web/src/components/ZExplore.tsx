const sections = [
  "Popular cuisines near me",
  "Popular restaurant types near me",
  "Top Restaurant Chains",
  "Cities We Deliver To",
];

import { ChevronDown } from "lucide-react";

export function ZExplore() {
  return (
    <section className="mx-auto mt-10 w-full max-w-6xl px-5 pb-10">
      <div className="inline-flex flex-col gap-2">
        <div className="text-2xl font-extrabold tracking-tight text-zinc-950">
          Explore options near me
        </div>
        <div className="h-1 w-14 rounded-full bg-[#EF4F5F]" />
      </div>
      <div className="mt-4 space-y-3">
        {sections.map((s) => (
          <details
            key={s}
            className="group rounded-xl bg-white px-4 py-4 shadow-sm ring-1 ring-black/5 transition hover:shadow-md"
          >
            <summary className="cursor-pointer list-none font-medium text-zinc-900">
              <div className="flex items-center justify-between">
                <span>{s}</span>
                <span className="text-zinc-400 transition group-open:rotate-180" aria-hidden="true">
                  <ChevronDown className="h-4 w-4" />
                </span>
              </div>
            </summary>
            <div className="mt-2 text-sm text-zinc-600">
              Placeholder content. We’ll enhance this with real data later.
            </div>
          </details>
        ))}
      </div>
    </section>
  );
}

