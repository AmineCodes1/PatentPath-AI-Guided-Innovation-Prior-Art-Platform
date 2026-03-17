/**
 * Protected search session placeholder page.
 */

import { useParams } from "react-router-dom";
import TopNav from "../components/layout/TopNav";

export default function SearchPage(): JSX.Element {
  const { sessionId } = useParams<{ sessionId: string }>();

  return (
    <div className="min-h-screen bg-surface">
      <TopNav />
      <main className="mx-auto max-w-7xl px-6 py-8">
        <h1 className="text-2xl font-bold text-text-primary">Search Session</h1>
        <p className="mt-2 text-text-secondary">Session ID: {sessionId}</p>
      </main>
    </div>
  );
}
