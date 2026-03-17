/**
 * Notes tab with masonry-like grid and create-note modal interaction.
 */

import { useMemo, useState } from "react";
import type { ReactElement } from "react";
import type { ProjectNote, ProjectSessionSummary } from "../../types/project";

type NotesTabProps = {
  notes: ProjectNote[];
  sessions: ProjectSessionSummary[];
  onCreateNote: (payload: { title: string; content: string; linked_session_id?: string }) => Promise<void>;
  onDeleteNote: (noteId: string) => Promise<void>;
};

export default function NotesTab({
  notes,
  sessions,
  onCreateNote,
  onDeleteNote,
}: Readonly<NotesTabProps>): ReactElement {
  const [openModal, setOpenModal] = useState(false);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [linkedSessionId, setLinkedSessionId] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const sessionNameById = useMemo(() => {
    const map = new Map<string, string>();
    sessions.forEach((session) => {
      map.set(session.id, `${new Date(session.executed_at).toLocaleDateString()} - ${session.query_text.slice(0, 40)}`);
    });
    return map;
  }, [sessions]);

  const submitNote = async (): Promise<void> => {
    if (!title.trim() || !content.trim()) {
      return;
    }
    setIsSubmitting(true);
    await onCreateNote({
      title: title.trim(),
      content: content.trim(),
      linked_session_id: linkedSessionId || undefined,
    });
    setIsSubmitting(false);
    setTitle("");
    setContent("");
    setLinkedSessionId("");
    setOpenModal(false);
  };

  return (
    <div className="relative">
      {notes.length === 0 ? (
        <p className="rounded-xl bg-surface p-4 text-sm text-text-secondary">No notes yet. Capture insights and ideas from your analysis here.</p>
      ) : (
        <div className="columns-1 gap-4 md:columns-2 xl:columns-3">
          {notes.map((note) => (
            <article key={note.id} className="mb-4 break-inside-avoid rounded-xl border border-slate-200 bg-white p-4">
              <div className="flex items-start justify-between gap-2">
                <h3 className="text-sm font-semibold text-text-primary">{note.title}</h3>
                <button
                  type="button"
                  onClick={() => void onDeleteNote(note.id)}
                  className="text-xs font-semibold text-risk-high hover:underline"
                >
                  Delete
                </button>
              </div>
              <p className="mt-2 whitespace-pre-line text-sm text-text-secondary">{note.content}</p>
              <p className="mt-3 text-xs text-text-secondary">
                {note.linked_session_id && sessionNameById.has(note.linked_session_id)
                  ? `Linked session: ${sessionNameById.get(note.linked_session_id)}`
                  : "Linked session: None"}
              </p>
              <p className="mt-1 text-xs text-text-secondary">
                {new Date(note.created_at).toLocaleString()}
              </p>
            </article>
          ))}
        </div>
      )}

      <button
        type="button"
        onClick={() => setOpenModal(true)}
        className="fixed bottom-8 right-8 rounded-full bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel transition hover:bg-blue-900"
      >
        Add Note
      </button>

      {openModal ? (
        <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/40 px-4">
          <div className="w-full max-w-lg rounded-2xl bg-white p-5 shadow-panel">
            <h3 className="text-lg font-semibold text-text-primary">Add Project Note</h3>
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
              <span>Content</span>
              <textarea
                value={content}
                onChange={(event) => setContent(event.target.value)}
                rows={5}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-text-primary outline-none focus:border-accent"
              />
            </label>
            <label className="mt-3 block text-sm text-text-secondary">
              <span>Linked Session (optional)</span>
              <select
                value={linkedSessionId}
                onChange={(event) => setLinkedSessionId(event.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-text-primary outline-none focus:border-accent"
              >
                <option value="">None</option>
                {sessions.map((session) => (
                  <option key={session.id} value={session.id}>
                    {new Date(session.executed_at).toLocaleDateString()} - {session.query_text.slice(0, 40)}
                  </option>
                ))}
              </select>
            </label>

            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setOpenModal(false)}
                className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-text-primary"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => void submitNote()}
                disabled={isSubmitting}
                className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-900 disabled:opacity-70"
              >
                {isSubmitting ? "Saving..." : "Save Note"}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
