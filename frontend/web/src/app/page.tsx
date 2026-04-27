import { ZHeader } from "@/components/ZHeader";
import { ZHero } from "@/components/ZHero";
import { ZCategoryCards } from "@/components/ZCategoryCards";
import { ZLocalities } from "@/components/ZLocalities";
import { ZExplore } from "@/components/ZExplore";
import { ZFooter } from "@/components/ZFooter";
import { ZSearchProvider, ZSearchResults } from "@/components/ZSearch";

export default function Home() {
  return (
    <ZSearchProvider>
      <div className="min-h-screen bg-white">
        <ZHeader />
        <ZHero />
        <ZSearchResults />
        <ZCategoryCards />
        <ZLocalities />
        <ZExplore />
        <ZFooter />
      </div>
    </ZSearchProvider>
  );
}
