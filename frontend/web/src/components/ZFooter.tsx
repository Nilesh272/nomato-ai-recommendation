export function ZFooter() {
  return (
    <footer className="border-t border-zinc-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-5 pt-10">
        <div className="text-xl font-semibold tracking-tight text-[#E23744]">nomato</div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            className="rounded-lg bg-white px-3 py-2 text-xs font-medium text-zinc-700 ring-1 ring-zinc-200 hover:bg-zinc-50"
          >
            India
          </button>
          <button
            type="button"
            className="rounded-lg bg-white px-3 py-2 text-xs font-medium text-zinc-700 ring-1 ring-zinc-200 hover:bg-zinc-50"
          >
            English
          </button>
        </div>
      </div>

      <div className="mx-auto grid max-w-6xl gap-6 px-5 py-8 md:grid-cols-4">
        <div>
          <div className="mt-2 text-sm text-zinc-600">
            Basic clone UI for testing the AI recommendation flow.
          </div>
        </div>
        <div>
          <div className="inline-flex flex-col gap-2">
            <div className="text-sm font-extrabold tracking-tight text-zinc-950">ABOUT NOMATO</div>
            <div className="h-1 w-10 rounded-full bg-[#EF4F5F]" />
          </div>
          <ul className="mt-2 space-y-2 text-sm text-zinc-600">
            <li>Who We Are</li>
            <li>Blog</li>
            <li>Work With Us</li>
            <li>Report Fraud</li>
          </ul>
        </div>
        <div>
          <div className="inline-flex flex-col gap-2">
            <div className="text-sm font-extrabold tracking-tight text-zinc-950">FOR RESTAURANTS</div>
            <div className="h-1 w-10 rounded-full bg-[#EF4F5F]" />
          </div>
          <ul className="mt-2 space-y-2 text-sm text-zinc-600">
            <li>Partner With Us</li>
            <li>Apps For You</li>
          </ul>
        </div>
        <div>
          <div className="inline-flex flex-col gap-2">
            <div className="text-sm font-extrabold tracking-tight text-zinc-950">LEARN MORE</div>
            <div className="h-1 w-10 rounded-full bg-[#EF4F5F]" />
          </div>
          <ul className="mt-2 space-y-2 text-sm text-zinc-600">
            <li>Privacy</li>
            <li>Security</li>
            <li>Terms</li>
          </ul>
        </div>
      </div>
      <div className="mx-auto max-w-6xl px-5 pb-8 text-xs text-zinc-500">
        <div>
          By continuing past this page, you agree to our Terms of Service, Cookie Policy,
          Privacy Policy and Content Policies.
        </div>
        <div className="mt-2 font-medium text-zinc-600">
          Made by <span className="font-semibold text-[#E23744]">Nilesh Thakare</span> — Product Manager
        </div>
      </div>
    </footer>
  );
}

