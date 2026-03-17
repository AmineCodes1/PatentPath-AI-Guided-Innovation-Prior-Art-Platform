/**
 * Protected project workspace placeholder page.
 */

import { useParams } from "react-router-dom";
import type { ReactElement } from "react";
import TopNav from "../components/layout/TopNav";

export default function ProjectPage(): ReactElement {
  const { id } = useParams<{ id: string }>();

  return (
    <div className="min-h-screen bg-surface">
      <TopNav />
      <main className="mx-auto max-w-7xl px-6 py-8">
        <h1 className="text-2xl font-bold text-text-primary">Project Workspace</h1>
        <p className="mt-2 text-text-secondary">Project ID: {id}</p>
      </main>
    </div>
  );
}
