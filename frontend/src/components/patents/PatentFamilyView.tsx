/**
 * Accordion widget showing INPADOC patent family members for a publication.
 */

import { useEffect, useMemo, useState } from "react";
import type { ReactElement } from "react";
import apiClient from "../../api/client";

type FamilyMember = {
  publication_number: string;
  title?: string | null;
  publication_date?: string | null;
};

type FamilyResponse = {
  publication_number: string;
  family_members: FamilyMember[];
};

type PatentFamilyViewProps = {
  publicationNumber: string;
};

function countryFlagFromPublication(publicationNumber: string): string {
  const code = publicationNumber.slice(0, 2).toUpperCase();
  if (!/^[A-Z]{2}$/.test(code)) {
    return "🏳";
  }

  const codePoints = Array.from(code).map((char) => 127397 + (char.codePointAt(0) ?? 65));
  return String.fromCodePoint(...codePoints);
}

function espacenetLink(publicationNumber: string): string {
  return `https://worldwide.espacenet.com/patent/search/family/${publicationNumber}`;
}

export default function PatentFamilyView({ publicationNumber }: Readonly<PatentFamilyViewProps>): ReactElement {
  const [open, setOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [members, setMembers] = useState<FamilyMember[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open || members.length > 0 || isLoading) {
      return;
    }

    let cancelled = false;

    const loadFamily = async (): Promise<void> => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await apiClient.get<FamilyResponse>(`/patents/${publicationNumber}/family`);
        if (!cancelled) {
          setMembers(response.data.family_members ?? []);
        }
      } catch {
        if (!cancelled) {
          setError("Unable to load patent family members right now.");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    void loadFamily();

    return () => {
      cancelled = true;
    };
  }, [isLoading, members.length, open, publicationNumber]);

  const headerLabel = useMemo(() => {
    if (members.length === 0) {
      return "Patent Family Members";
    }
    return `Patent Family Members (${members.length})`;
  }, [members.length]);

  return (
    <section className="rounded-xl border border-slate-200 bg-white">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="flex w-full items-center justify-between px-4 py-3 text-left"
      >
        <span className="text-sm font-semibold text-text-primary">{headerLabel}</span>
        <span className="text-xs font-semibold text-accent">{open ? "Hide" : "Show"}</span>
      </button>

      {open ? (
        <div className="border-t border-slate-100 px-4 py-3">
          {isLoading ? (
            <div className="space-y-2" aria-live="polite">
              <p className="text-xs font-semibold uppercase tracking-widest text-primary">Loading family...</p>
              <div className="h-10 animate-pulse rounded-lg bg-slate-100" />
              <div className="h-10 animate-pulse rounded-lg bg-slate-100" />
            </div>
          ) : null}

          {!isLoading && error ? <p className="text-sm text-risk-high">{error}</p> : null}

          {!isLoading && !error && members.length === 0 ? (
            <p className="text-sm text-text-secondary">No family members were returned for this publication.</p>
          ) : null}

          {!isLoading && !error && members.length > 0 ? (
            <ul className="space-y-2">
              {members.map((member) => (
                <li key={member.publication_number} className="rounded-lg border border-slate-200 bg-surface px-3 py-2">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-text-primary">
                        <span className="mr-2" aria-hidden="true">{countryFlagFromPublication(member.publication_number)}</span>
                        {member.publication_number}
                      </p>
                      <p className="text-xs text-text-secondary">
                        {member.title || "Title unavailable"}
                      </p>
                    </div>
                    <a
                      href={espacenetLink(member.publication_number)}
                      target="_blank"
                      rel="noreferrer"
                      className="rounded-md border border-primary/40 px-2 py-1 text-xs font-semibold text-primary hover:bg-primary hover:text-white"
                    >
                      Espacenet
                    </a>
                  </div>
                </li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
