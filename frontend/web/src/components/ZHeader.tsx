 "use client";

import * as Dialog from "@radix-ui/react-dialog";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import * as NavigationMenu from "@radix-ui/react-navigation-menu";
import * as Separator from "@radix-ui/react-separator";
import { Menu, ShoppingCart } from "lucide-react";

const red = {
  brand: "text-[#E23744]",
  primaryBg: "bg-[#EF4F5F]",
  primaryHover: "hover:bg-[#E23744]",
  ring: "ring-[#EF4F5F]/30",
};

function NavLink(props: { href: string; children: React.ReactNode }) {
  return (
    <NavigationMenu.Link asChild>
      <a
        href={props.href}
        className="rounded-xl px-3 py-2 text-sm font-semibold text-zinc-700 transition hover:bg-zinc-50 hover:text-zinc-900"
      >
        {props.children}
      </a>
    </NavigationMenu.Link>
  );
}

export function ZHeader() {
  return (
    <header className="sticky top-0 z-40 border-b border-zinc-200 bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-5">
        <div className="flex items-center gap-3">
          <div className="grid h-9 w-9 place-items-center rounded-xl bg-[#EF4F5F]/10 ring-1 ring-[#EF4F5F]/20">
            <span className={["text-base font-black", red.brand].join(" ")}>n</span>
          </div>
          <div className="leading-none">
            <div className={["text-[17px] font-extrabold tracking-tight", red.brand].join(" ")}>
              nomato
            </div>
            <div className="mt-0.5 hidden text-[11px] font-medium text-zinc-500 sm:block">
              AI Restaurant Recommendation System
            </div>
          </div>
        </div>

        <NavigationMenu.Root className="hidden md:block">
          <NavigationMenu.List className="flex items-center gap-2">
            <NavigationMenu.Item>
              <NavLink href="#">Log in</NavLink>
            </NavigationMenu.Item>

            <NavigationMenu.Item>
              <NavigationMenu.Link asChild>
                <a
                  href="#"
                  className={[
                    "rounded-xl px-3 py-2 text-sm font-semibold text-white shadow-sm ring-1 transition",
                    red.primaryBg,
                    red.ring,
                    red.primaryHover,
                  ].join(" ")}
                >
                  Sign up
                </a>
              </NavigationMenu.Link>
            </NavigationMenu.Item>

            <NavigationMenu.Item>
              <DropdownMenu.Root>
                <DropdownMenu.Trigger asChild>
                  <button
                    type="button"
                    className="ml-1 inline-flex items-center justify-center rounded-xl px-3 py-2 text-sm font-semibold text-zinc-700 transition hover:bg-zinc-50 hover:text-zinc-900"
                    aria-label="Open actions"
                  >
                    <ShoppingCart className="h-4 w-4" />
                  </button>
                </DropdownMenu.Trigger>
                <DropdownMenu.Portal>
                  <DropdownMenu.Content
                    sideOffset={8}
                    className="min-w-44 rounded-2xl bg-white p-1 shadow-lg ring-1 ring-black/10"
                  >
                    <DropdownMenu.Item className="cursor-pointer rounded-xl px-3 py-2 text-sm font-semibold text-zinc-800 outline-none hover:bg-zinc-50">
                      View cart
                    </DropdownMenu.Item>
                    <DropdownMenu.Item className="cursor-pointer rounded-xl px-3 py-2 text-sm font-semibold text-zinc-800 outline-none hover:bg-zinc-50">
                      Orders
                    </DropdownMenu.Item>
                    <DropdownMenu.Separator className="my-1 h-px bg-zinc-200" />
                    <DropdownMenu.Item className="cursor-pointer rounded-xl px-3 py-2 text-sm font-semibold text-[#E23744] outline-none hover:bg-[#EF4F5F]/10">
                      Help & support
                    </DropdownMenu.Item>
                  </DropdownMenu.Content>
                </DropdownMenu.Portal>
              </DropdownMenu.Root>
            </NavigationMenu.Item>
          </NavigationMenu.List>
        </NavigationMenu.Root>

        <Dialog.Root>
          <Dialog.Trigger asChild>
            <button
              type="button"
              className="inline-flex items-center justify-center rounded-xl bg-white px-3 py-2 text-sm font-semibold text-zinc-700 ring-1 ring-zinc-200 transition hover:bg-zinc-50 md:hidden"
              aria-label="Open menu"
            >
              <Menu className="h-4 w-4 text-zinc-900" />
            </button>
          </Dialog.Trigger>
          <Dialog.Portal>
            <Dialog.Overlay className="fixed inset-0 z-50 bg-black/35 backdrop-blur-sm" />
            <Dialog.Content className="fixed inset-x-3 top-4 z-50 rounded-3xl bg-white p-4 shadow-2xl ring-1 ring-black/10 md:hidden">
              <div className="flex items-center justify-between">
                <div className="text-sm font-extrabold text-zinc-900">Menu</div>
                <Dialog.Close asChild>
                  <button
                    type="button"
                    className="rounded-xl px-3 py-2 text-sm font-semibold text-zinc-700 hover:bg-zinc-50"
                  >
                    Close
                  </button>
                </Dialog.Close>
              </div>

              <div className="mt-3 space-y-1">
                {[
                  "Investor Relations",
                  "Add restaurant",
                  "Log in",
                  "Sign up",
                ].map((label) => (
                  <a
                    key={label}
                    href="#"
                    className={[
                      "block rounded-2xl px-3 py-3 text-sm font-semibold transition",
                      label === "Sign up"
                        ? `${red.primaryBg} ${red.primaryHover} text-white`
                        : "text-zinc-800 hover:bg-zinc-50",
                    ].join(" ")}
                  >
                    {label}
                  </a>
                ))}
              </div>
            </Dialog.Content>
          </Dialog.Portal>
        </Dialog.Root>
      </div>
    </header>
  );
}

