"use client";

import { ZHeader } from "@/components/ZHeader";
import { ZHero } from "@/components/ZHero";
import { ZFooter } from "@/components/ZFooter";
import { ZSearchProvider, ZSearchResults } from "@/components/ZSearch";

export function ZHomeClient() {
  return (
    <ZSearchProvider>
      <div className="min-h-screen bg-zinc-50">
        <ZHeader />
        <ZHero />
        <ZSearchResults />
        <ZFooter />
      </div>
    </ZSearchProvider>
  );
}

