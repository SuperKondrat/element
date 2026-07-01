import { useEffect, useState } from "react";
import { useApi } from "../../context/TransportContext";
import { useAuth } from "../../context/AuthContext";
import { ApiRequestError } from "../../api/errors";
import type { Application } from "../../types";
import { APPLICATION_STATUS_LABELS } from "../../types";
import { formatDate } from "../../lib/format";
import { useAdminGuard } from "./useAdminGuard";

export function ApplicationsPage() {
  const api = useApi();
  const { token } = useAuth();
  const handleUnauthorized = useAdminGuard();

  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    api
      .adminListApplications(token)
      .then(setApplications)
      .catch((err: unknown) => {
        if (err instanceof ApiRequestError && handleUnauthorized(err)) return;
        setError(err instanceof Error ? err.message : "Не удалось загрузить заявки");
      })
      .finally(() => setLoading(false));
  }, [api, token, handleUnauthorized]);

  if (loading) return <p className="text-slate-500 dark:text-slate-400">Загрузка…</p>;
  if (error)
    return (
      <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950/40 dark:text-red-400">
        {error}
      </p>
    );

  return (
    <div>
      <h1 className="mb-4 text-xl font-semibold text-slate-900 dark:text-slate-100">Заявки</h1>
      {applications.length === 0 ? (
        <p className="text-slate-500 dark:text-slate-400">Заявок пока нет.</p>
      ) : (
        <table className="w-full border-collapse overflow-hidden rounded-lg border border-slate-200 bg-white text-sm dark:border-slate-800 dark:bg-slate-900">
          <thead className="bg-slate-50 text-left text-slate-500 dark:bg-slate-800/60 dark:text-slate-400">
            <tr>
              <th className="px-3 py-2">Лот</th>
              <th className="px-3 py-2">Контакт</th>
              <th className="px-3 py-2">Комментарий</th>
              <th className="px-3 py-2">Статус</th>
              <th className="px-3 py-2">Дата</th>
            </tr>
          </thead>
          <tbody>
            {applications.map((a) => (
              <tr
                key={a.id}
                className="border-t border-slate-100 align-top text-slate-900 dark:border-slate-800 dark:text-slate-100"
              >
                <td className="px-3 py-2">{a.lot_id ? `#${a.lot_id}` : "—"}</td>
                <td className="px-3 py-2">
                  {a.contact_name}
                  <div className="text-xs text-slate-400 dark:text-slate-500">
                    {a.contact_phone ?? a.contact_email}
                  </div>
                </td>
                <td className="max-w-xs px-3 py-2 text-slate-600 dark:text-slate-300">
                  {a.comment ?? "—"}
                </td>
                <td className="px-3 py-2">{APPLICATION_STATUS_LABELS[a.status]}</td>
                <td className="px-3 py-2 text-slate-500 dark:text-slate-400">
                  {formatDate(a.created_at)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
