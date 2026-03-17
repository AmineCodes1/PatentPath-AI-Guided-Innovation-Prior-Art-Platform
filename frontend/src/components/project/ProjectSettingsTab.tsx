/**
 * Project settings tab for editing metadata and archiving the project.
 */

import { useState } from "react";
import type { ReactElement } from "react";
import type { InnovationProject, ProjectUpdatePayload } from "../../types/project";

type ProjectSettingsTabProps = {
  project: InnovationProject;
  onSave: (payload: ProjectUpdatePayload) => Promise<void>;
  onArchive: () => Promise<void>;
};

export default function ProjectSettingsTab({
  project,
  onSave,
  onArchive,
}: Readonly<ProjectSettingsTabProps>): ReactElement {
  const [title, setTitle] = useState(project.title);
  const [problemStatement, setProblemStatement] = useState(project.problem_statement);
  const [domainIpcClass, setDomainIpcClass] = useState(project.domain_ipc_class ?? "");
  const [isSaving, setIsSaving] = useState(false);

  const saveChanges = async (): Promise<void> => {
    setIsSaving(true);
    await onSave({
      title: title.trim(),
      problem_statement: problemStatement.trim(),
      domain_ipc_class: domainIpcClass.trim() || undefined,
    });
    setIsSaving(false);
  };

  const handleArchive = async (): Promise<void> => {
    const confirmed = globalThis.confirm("Archive this project? You can still view it but it will be marked inactive.");
    if (!confirmed) {
      return;
    }
    await onArchive();
  };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5">
      <h3 className="text-base font-semibold text-text-primary">Project Settings</h3>

      <label className="mt-4 block text-sm text-text-secondary">
        <span>Title</span>
        <input
          type="text"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-text-primary outline-none focus:border-accent"
        />
      </label>

      <label className="mt-3 block text-sm text-text-secondary">
        <span>Problem Statement</span>
        <textarea
          value={problemStatement}
          onChange={(event) => setProblemStatement(event.target.value)}
          rows={6}
          className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-text-primary outline-none focus:border-accent"
        />
      </label>

      <label className="mt-3 block text-sm text-text-secondary">
        <span>Domain IPC Class</span>
        <input
          type="text"
          value={domainIpcClass}
          onChange={(event) => setDomainIpcClass(event.target.value.toUpperCase())}
          className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-text-primary outline-none focus:border-accent"
          placeholder="e.g. G06F"
        />
      </label>

      <div className="mt-5 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => void saveChanges()}
          disabled={isSaving}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-900 disabled:opacity-70"
        >
          {isSaving ? "Saving..." : "Save Changes"}
        </button>
        <button
          type="button"
          onClick={() => void handleArchive()}
          className="rounded-lg border border-risk-high px-4 py-2 text-sm font-semibold text-risk-high transition hover:bg-risk-high/10"
        >
          Archive Project
        </button>
      </div>
    </div>
  );
}
