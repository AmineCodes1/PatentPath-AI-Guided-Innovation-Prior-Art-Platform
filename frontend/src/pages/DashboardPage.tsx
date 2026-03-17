/**
 * Placeholder dashboard page after successful authentication.
 */

import TopNav from "../components/layout/TopNav";
import type { ReactElement } from "react";

export default function DashboardPage(): ReactElement {
  return (
    <div className="min-h-screen bg-surface">
      <TopNav />
      <main className="mx-auto max-w-7xl px-6 py-8">
        <h1 className="text-2xl font-bold text-text-primary">Dashboard</h1>
        <p className="mt-2 text-text-secondary">Your innovation projects and recent searches will appear here.</p>
      </main>
    </div>
  );
}
