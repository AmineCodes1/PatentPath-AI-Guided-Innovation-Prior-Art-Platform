/**
 * Login page for existing PatentPath users.
 */

import { FormEvent, useState } from "react";
import type { ReactElement } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getMe, login } from "../api/auth";
import { useAuthStore } from "../store/authStore";

export default function LoginPage(): ReactElement {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const storeLogin = useAuthStore((state) => state.login);
  const navigate = useNavigate();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault();
    setErrorMessage(null);
    setIsSubmitting(true);

    try {
      const tokenPayload = await login({ email, password });
      const user = await getMe();
      storeLogin(tokenPayload.access_token, user);
      navigate("/dashboard", { replace: true });
    } catch {
      setErrorMessage("Login failed. Please verify your credentials and try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-10">
      <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-panel">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-primary text-2xl font-bold text-white">
            P
          </div>
          <h1 className="text-2xl font-bold text-text-primary">PatentPath</h1>
          <p className="mt-1 text-sm text-text-secondary">Sign in to continue your innovation search.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <label className="block">
            <span className="mb-1 block text-sm font-medium text-text-primary">Email</span>
            <input
              type="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none transition focus:border-accent"
            />
          </label>

          <label className="block">
            <span className="mb-1 block text-sm font-medium text-text-primary">Password</span>
            <input
              type="password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none transition focus:border-accent"
            />
          </label>

          {errorMessage ? <p className="text-sm text-risk-high">{errorMessage}</p> : null}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-900 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {isSubmitting ? "Signing in..." : "Login"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-text-secondary">
          New to PatentPath?{" "}
          <Link to="/register" className="font-semibold text-primary hover:text-accent">
            Create an account
          </Link>
        </p>
      </div>
    </main>
  );
}
