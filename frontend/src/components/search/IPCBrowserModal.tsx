/**
 * IPC browser modal with browse and fuzzy-search tabs for filter selection.
 */

import { useEffect, useMemo, useState } from "react";
import type { ReactElement } from "react";
import { getIPCTree, searchIPC } from "../../api/classifications";
import type { IPCClass, IPCSection } from "../../api/classifications";

type IPCBrowserModalProps = {
  isOpen: boolean;
  initialSelected: string[];
  onApply: (codes: string[]) => void;
  onClose: () => void;
};

type TabKey = "browse" | "search";

function uniqueCodes(codes: string[]): string[] {
  const normalized = codes.map((item) => item.trim().toUpperCase()).filter(Boolean);
  return Array.from(new Set(normalized));
}

export default function IPCBrowserModal({
  isOpen,
  initialSelected,
  onApply,
  onClose,
}: Readonly<IPCBrowserModalProps>): ReactElement | null {
  const [activeTab, setActiveTab] = useState<TabKey>("browse");
  const [sections, setSections] = useState<IPCSection[]>([]);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});
  const [selectedCodes, setSelectedCodes] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<IPCClass[]>([]);
  const [isLoadingTree, setIsLoadingTree] = useState(false);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    setSelectedCodes(uniqueCodes(initialSelected));
    if (sections.length > 0) {
      return;
    }

    setIsLoadingTree(true);
    void getIPCTree()
      .then((payload) => {
        setSections(payload.sections);
        setExpandedSections(
          payload.sections.reduce<Record<string, boolean>>((accumulator, section) => {
            accumulator[section.section] = section.section === "G";
            return accumulator;
          }, {}),
        );
      })
      .finally(() => {
        setIsLoadingTree(false);
      });
  }, [initialSelected, isOpen, sections.length]);

  useEffect(() => {
    if (!isOpen || activeTab !== "search") {
      return;
    }

    const normalized = searchQuery.trim();
    if (normalized.length < 2) {
      setSearchResults([]);
      return;
    }

    const timerId = globalThis.setTimeout(() => {
      void searchIPC(normalized).then((items) => {
        setSearchResults(items);
      });
    }, 250);

    return () => {
      globalThis.clearTimeout(timerId);
    };
  }, [activeTab, isOpen, searchQuery]);

  const selectedSet = useMemo(() => new Set(selectedCodes), [selectedCodes]);

  if (!isOpen) {
    return null;
  }

  const toggleSelectCode = (code: string): void => {
    const normalized = code.toUpperCase();
    setSelectedCodes((current) => (
      current.includes(normalized)
        ? current.filter((item) => item !== normalized)
        : [...current, normalized]
    ));
  };

  const removeCode = (code: string): void => {
    const normalized = code.toUpperCase();
    setSelectedCodes((current) => current.filter((item) => item !== normalized));
  };

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-4xl rounded-2xl border border-slate-200 bg-white shadow-panel">
        <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4">
          <h3 className="text-lg font-semibold text-text-primary">IPC/CPC Browser</h3>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md border border-slate-300 px-3 py-1 text-xs font-semibold text-text-secondary hover:bg-surface"
          >
            Close
          </button>
        </div>

        <div className="px-5 pt-4">
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setActiveTab("browse")}
              className={`rounded-lg px-3 py-2 text-sm font-semibold ${
                activeTab === "browse" ? "bg-primary text-white" : "bg-surface text-text-secondary"
              }`}
            >
              Browse
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("search")}
              className={`rounded-lg px-3 py-2 text-sm font-semibold ${
                activeTab === "search" ? "bg-primary text-white" : "bg-surface text-text-secondary"
              }`}
            >
              Search
            </button>
          </div>

          <div className="mt-3 flex flex-wrap gap-2">
            {selectedCodes.length === 0 ? (
              <p className="text-xs text-text-secondary">No IPC classes selected yet.</p>
            ) : (
              selectedCodes.map((code) => (
                <button
                  type="button"
                  key={code}
                  onClick={() => removeCode(code)}
                  className="rounded-full bg-accent/20 px-3 py-1 text-xs font-semibold text-primary"
                  title="Remove class"
                >
                  {code} ×
                </button>
              ))
            )}
          </div>
        </div>

        <div className="max-h-[55vh] overflow-auto px-5 py-4">
          {activeTab === "browse" ? (
            <div className="space-y-3">
              {isLoadingTree ? (
                <p className="text-sm text-text-secondary">Loading IPC sections...</p>
              ) : (
                sections.map((section) => {
                  const expanded = expandedSections[section.section] ?? false;
                  return (
                    <div key={section.section} className="rounded-xl border border-slate-200">
                      <button
                        type="button"
                        onClick={() => {
                          setExpandedSections((current) => ({
                            ...current,
                            [section.section]: !expanded,
                          }));
                        }}
                        className="flex w-full items-center justify-between px-4 py-3 text-left"
                      >
                        <span className="font-semibold text-text-primary">
                          {section.section} — {section.title}
                        </span>
                        <span className="text-xs text-text-secondary">{expanded ? "Hide" : "Show"}</span>
                      </button>

                      {expanded ? (
                        <div className="border-t border-slate-200 px-3 py-3">
                          <div className="grid gap-2 md:grid-cols-2">
                            {section.classes.map((item) => {
                              const selected = selectedSet.has(item.code.toUpperCase());
                              return (
                                <button
                                  type="button"
                                  key={item.code}
                                  onClick={() => toggleSelectCode(item.code)}
                                  className={`rounded-lg border px-3 py-2 text-left transition ${
                                    selected
                                      ? "border-primary bg-primary/10"
                                      : "border-slate-200 bg-white hover:bg-surface"
                                  }`}
                                >
                                  <p className="text-sm font-semibold text-text-primary">{item.code}</p>
                                  <p className="mt-1 text-xs text-text-secondary">{item.title}</p>
                                </button>
                              );
                            })}
                          </div>
                        </div>
                      ) : null}
                    </div>
                  );
                })
              )}
            </div>
          ) : (
            <div>
              <input
                type="text"
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                placeholder="Search IPC classes by code, title, or keyword"
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-text-primary outline-none focus:border-accent"
              />

              <div className="mt-3 space-y-2">
                {searchResults.length === 0 ? (
                  <p className="text-sm text-text-secondary">Type at least 2 characters to search.</p>
                ) : (
                  searchResults.map((item) => {
                    const selected = selectedSet.has(item.code.toUpperCase());
                    return (
                      <button
                        type="button"
                        key={item.code}
                        onClick={() => toggleSelectCode(item.code)}
                        className={`w-full rounded-lg border px-3 py-2 text-left transition ${
                          selected ? "border-primary bg-primary/10" : "border-slate-200 hover:bg-surface"
                        }`}
                      >
                        <p className="text-sm font-semibold text-text-primary">{item.code} — {item.title}</p>
                        <p className="mt-1 text-xs text-text-secondary">{item.description}</p>
                      </button>
                    );
                  })
                )}
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center justify-end gap-2 border-t border-slate-200 px-5 py-4">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-text-secondary hover:bg-surface"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={() => {
              onApply(uniqueCodes(selectedCodes));
              onClose();
            }}
            className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white hover:bg-blue-900"
          >
            Apply Filters
          </button>
        </div>
      </div>
    </div>
  );
}
