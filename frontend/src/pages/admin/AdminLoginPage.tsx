import { useState, type FormEvent } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useApi } from "../../context/TransportContext";
import { useAuth } from "../../context/AuthContext";
import { ApiRequestError } from "../../api/errors";

export function AdminLoginPage() {
  const api = useApi();
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (isAuthenticated) {
    return <Navigate to="/admin/feeds" replace />;
  }

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const { access_token } = await api.login(username, password);
      login(access_token);
      navigate("/admin/feeds", { replace: true });
    } catch (err) {
      setError(err instanceof ApiRequestError ? "Неверный логин или пароль" : "Ошибка входа");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-sm px-4 py-12">
      <h1 className="mb-4 text-xl font-semibold text-slate-900 dark:text-slate-100">
        Вход в админку
      </h1>
      <form
        onSubmit={submit}
        className="space-y-3 rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900"
      >
        <input
          className="w-full rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm text-slate-900 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          placeholder="Логин"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoFocus
        />
        <input
          className="w-full rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm text-slate-900 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          placeholder="Пароль"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        {error && <p className="text-sm text-red-700 dark:text-red-400">{error}</p>}
        <button
          type="submit"
          disabled={submitting || !username || !password}
          className="w-full rounded-md bg-indigo-600 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-500 disabled:opacity-40"
        >
          {submitting ? "Вход…" : "Войти"}
        </button>
      </form>
    </div>
  );
}
