import { useEffect, useState } from "react";
import { useApi } from "../../context/TransportContext";
import { useAuth } from "../../context/AuthContext";
import { ApiRequestError } from "../../api/errors";
import type { Booking } from "../../types";
import { BOOKING_STATUS_LABELS } from "../../types";
import { formatDate } from "../../lib/format";
import { useAdminGuard } from "./useAdminGuard";

export function BookingsPage() {
  const api = useApi();
  const { token } = useAuth();
  const handleUnauthorized = useAdminGuard();

  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    api
      .adminListBookings(token)
      .then(setBookings)
      .catch((err: unknown) => {
        if (err instanceof ApiRequestError && handleUnauthorized(err)) return;
        setError(err instanceof Error ? err.message : "Не удалось загрузить брони");
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
      <h1 className="mb-4 text-xl font-semibold text-slate-900 dark:text-slate-100">Брони</h1>
      {bookings.length === 0 ? (
        <p className="text-slate-500 dark:text-slate-400">Броней пока нет.</p>
      ) : (
        <table className="w-full border-collapse overflow-hidden rounded-lg border border-slate-200 bg-white text-sm dark:border-slate-800 dark:bg-slate-900">
          <thead className="bg-slate-50 text-left text-slate-500 dark:bg-slate-800/60 dark:text-slate-400">
            <tr>
              <th className="px-3 py-2">Лот</th>
              <th className="px-3 py-2">Контакт</th>
              <th className="px-3 py-2">Статус</th>
              <th className="px-3 py-2">Дата</th>
            </tr>
          </thead>
          <tbody>
            {bookings.map((b) => (
              <tr
                key={b.id}
                className="border-t border-slate-100 text-slate-900 dark:border-slate-800 dark:text-slate-100"
              >
                <td className="px-3 py-2">#{b.lot_id}</td>
                <td className="px-3 py-2">
                  {b.contact_name}
                  <div className="text-xs text-slate-400 dark:text-slate-500">
                    {b.contact_phone ?? b.contact_email}
                  </div>
                </td>
                <td className="px-3 py-2">{BOOKING_STATUS_LABELS[b.status]}</td>
                <td className="px-3 py-2 text-slate-500 dark:text-slate-400">
                  {formatDate(b.created_at)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
