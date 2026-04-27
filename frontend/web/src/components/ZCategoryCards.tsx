const items = [
  {
    title: "Order Online",
    subtitle: "Stay home and order to your doorstep",
    image:
      "https://images.unsplash.com/photo-1604908554027-027dd8b0a4a3?auto=format&fit=crop&w=1200&q=60",
  },
  {
    title: "Dining",
    subtitle: "View the city's favourite dining venues",
    image:
      "https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=1200&q=60",
  },
  {
    title: "Live Events",
    subtitle: "Discover India's best festivals & events",
    image:
      "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=1200&q=60",
  },
];

export function ZCategoryCards() {
  return (
    <section className="mx-auto mt-6 w-full max-w-6xl px-5">
      <div className="grid gap-4 md:grid-cols-3">
        {items.map((it) => (
          <div
            key={it.title}
            className="group overflow-hidden rounded-xl bg-white shadow-sm ring-1 ring-black/5 transition hover:shadow-md"
          >
            <div
              className="h-36 w-full bg-cover bg-center transition-transform duration-300 group-hover:scale-[1.02]"
              style={{ backgroundImage: `url('${it.image}')` }}
            />
            <div className="p-4">
              <div className="text-lg font-semibold">{it.title}</div>
              <div className="mt-1 text-sm text-zinc-600">{it.subtitle}</div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

