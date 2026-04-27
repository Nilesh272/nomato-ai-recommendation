import { ZSearchBar } from "./ZSearch";

export function ZHero() {
  return (
    <section className="relative h-[440px] overflow-hidden md:h-[480px]">
      <div
        className="absolute inset-0 w-full bg-cover bg-center"
        style={{
          backgroundImage:
            "linear-gradient(rgba(0,0,0,.50), rgba(0,0,0,.35)), url('https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=2400&q=60')",
        }}
      />
      <div className="absolute inset-0 z-10 flex items-center">
        <div className="mx-auto w-full max-w-6xl px-5">
          <div className="text-center text-white">
            <div className="text-5xl font-semibold tracking-tight md:text-6xl">
              nomato
            </div>
            <div className="mx-auto mt-3 max-w-3xl text-base font-medium opacity-95 md:text-lg">
              Find the best restaurants, cafés and bars in your city
            </div>
            <div className="mx-auto mt-6 max-w-4xl">
              <ZSearchBar />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

