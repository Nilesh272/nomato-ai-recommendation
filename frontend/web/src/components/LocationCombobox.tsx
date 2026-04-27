"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { ChevronDown } from "lucide-react";

type Props = {
  value: string;
  options: string[];
  placeholder?: string;
  disabled?: boolean;
  onChange: (value: string) => void;
};

export function LocationCombobox({
  value,
  options,
  placeholder,
  disabled,
  onChange,
}: Props) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const rootRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    function onDocClick(e: MouseEvent) {
      if (!rootRef.current) return;
      if (!rootRef.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return options.slice(0, 50);
    return options
      .filter((o) => o.toLowerCase().includes(q))
      .slice(0, 50);
  }, [options, query]);

  return (
    <div ref={rootRef} className="relative w-full">
      <div className="flex w-full items-center gap-2">
        <input
          value={open ? query : value}
          onFocus={() => {
            setOpen(true);
            setQuery("");
          }}
          onChange={(e) => {
            setOpen(true);
            setQuery(e.target.value);
            onChange(e.target.value); // allow free typing
          }}
          placeholder={placeholder}
          disabled={disabled}
          className="w-full bg-transparent text-sm outline-none"
        />
        <button
          type="button"
          disabled={disabled}
          onClick={() => setOpen((v) => !v)}
          className="rounded-md px-1 text-zinc-500 hover:bg-zinc-100 disabled:opacity-50"
          aria-label="Toggle locations"
        >
          <ChevronDown className="h-4 w-4" />
        </button>
      </div>

      {open ? (
        <div className="absolute left-0 right-0 top-[42px] z-50 max-h-64 overflow-auto rounded-xl border border-zinc-200 bg-white shadow-lg">
          {filtered.length ? (
            filtered.map((opt) => (
              <button
                key={opt}
                type="button"
                onClick={() => {
                  onChange(opt);
                  setOpen(false);
                }}
                className="block w-full px-3 py-2 text-left text-sm hover:bg-zinc-50"
              >
                {opt}
              </button>
            ))
          ) : (
            <div className="px-3 py-2 text-sm text-zinc-500">
              No matches.
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
}

