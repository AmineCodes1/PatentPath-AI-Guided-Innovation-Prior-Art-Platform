/**
 * Primary navigation bar for authenticated PatentPath pages.
 */

import { useMemo, useState } from "react";
import type { ReactElement } from "react";
import { Link, useNavigate } from "react-router-dom";
import SearchHistoryPanel from "../search/SearchHistoryPanel";
import { useAuthStore } from "../../store/authStore";

export default function TopNav(): ReactElement {
  const [open, setOpen] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const navigate = useNavigate();

  const initials = useMemo(() => {
    if (!user?.display_name) {
      return "PP";
    }
    return user.display_name
      .split(" ")
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase() ?? "")
      .join("");
  }, [user?.display_name]);

  const handleLogout = (): void => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <header className="border-b border-blue-900 bg-primary text-white">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link to="/dashboard" className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-md bg-white/20 text-center text-lg font-bold leading-9">P</div>
          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-white/70">PatentPath</p>
            <p className="text-sm font-semibold">Innovation Workspace</p>
          </div>
        </Link>

        <div className="relative">
          <div className="flex items-center gap-2">
            <Link
              to="/app-docs"
              className="rounded-full border border-white/25 bg-white/10 px-3 py-1.5 text-sm font-semibold"
            >
              Docs
            </Link>

            <button
              type="button"
              onClick={() => setHistoryOpen(true)}
              className="rounded-full border border-white/25 bg-white/10 px-3 py-1.5 text-sm font-semibold"
            >
              History
            </button>

            <button
              type="button"
              onClick={() => setOpen((value) => !value)}
              className="flex items-center gap-3 rounded-full border border-white/25 bg-white/10 px-3 py-1.5"
            >
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-white text-sm font-bold text-primary">
                {initials}
              </span>
              <span className="text-sm font-medium">{user?.display_name ?? "Account"}</span>
            </button>
          </div>

          {open ? (
            <div className="absolute right-0 z-10 mt-2 w-44 rounded-xl border border-slate-200 bg-white py-2 text-sm text-text-primary shadow-panel">
              <button type="button" className="block w-full px-4 py-2 text-left hover:bg-surface">
                Profile
              </button>
              <button type="button" className="block w-full px-4 py-2 text-left hover:bg-surface">
                Settings
              </button>
              <button
                type="button"
                onClick={handleLogout}
                className="block w-full px-4 py-2 text-left text-risk-high hover:bg-surface"
              >
                Logout
              </button>
            </div>
          ) : null}
        </div>
      </div>

      <SearchHistoryPanel open={historyOpen} onClose={() => setHistoryOpen(false)} />
    </header>
  );
}
