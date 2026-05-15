import { ZHeader } from "@/components/ZHeader";
import { ZHero } from "@/components/ZHero";
import { ZFooter } from "@/components/ZFooter";
import { ZSearchProvider, ZSearchResults } from "@/components/ZSearch";

export default function Home() {
  return (
    <ZSearchProvider>
      <div className="min-h-screen bg-white">
        <ZHeader />
        <ZHero />
        <ZSearchResults />
        <ZFooter />
      </div>
    </ZSearchProvider>
  );
}
