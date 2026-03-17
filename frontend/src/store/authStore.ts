/**
 * Zustand authentication store with localStorage token persistence.
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User } from "../types/auth";

type AuthState = {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  setUser: (user: User | null) => void;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      login: (token, user) =>
        set({
          token,
          user,
          isAuthenticated: true,
        }),
      logout: () =>
        set({
          token: null,
          user: null,
          isAuthenticated: false,
        }),
      setUser: (user) =>
        set((state) => ({
          user,
          isAuthenticated: Boolean(state.token && user),
        })),
    }),
    {
      name: "patentpath-auth",
      partialize: (state) => ({ token: state.token, user: state.user }),
      onRehydrateStorage: () => (state) => {
        if (!state) {
          return;
        }
        state.isAuthenticated = Boolean(state.token && state.user);
      },
    },
  ),
);
