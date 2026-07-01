import { useCallback, useEffect, useState, type ChangeEvent } from "react";
import { useApi } from "../../context/TransportContext";
import { useAuth } from "../../context/AuthContext";
import { ApiRequestError } from "../../api/errors";
import type { LotSet } from "../../types";
import { formatDate } from "../../lib/format";
import { useAdminGuard } from "./useAdminGuard";

export function FeedsPage() {
  const api = useApi();
  const { token } = useAuth();
  const handleUnauthorized = useAdminGuard();

  const [sets, setSets] = useState<LotSet[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [activatingId, setActivatingId] = useState<number | null>(null);

  const load = useCallback(() => {
    if (!token) return;
    setLoading(true);
    api
      .adminListLotSets(token)
      .then(setSets)
      .catch((err: unknown) => {
        if (err instanceof ApiRequestError && handleUnauthorized(err)) return;
        setError(err instanceof Error ? err.message : "Не удалось загрузить наборы");
      })
      .finally(() => setLoading(false));
  }, [api, token, handleUnauthorized]);

  useEffect(() => {
    load();
  }, [load]);

  const onFileChange = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file || !token) return;

    setUploading(true);
    setUploadMessage(null);
    setError(null);
    try {
      const result = await api.adminUploadFeed(token, file);
      setUploadMessage(
        `Загружено ${result.lots_count} лотов` +
          (result.skipped_count ? `, пропущено ${result.skipped_count}` : ""),
      );
      load();
    } catch (err) {
      if (err instanceof ApiRequestError && handleUnauthorized(err)) return;
      setError(err instanceof Error ? err.message : "Не удалось загрузить фид");
    } finally {
      setUploading(false);
    }
  };

  const activate = async (setId: number) => {
    if (!token) return;
    setActivatingId(setId);
    try {
      await api.adminActivateLotSet(token, setId);
      load();
    } catch (err) {
      if (err instanceof ApiRequestError && handleUnauthorized(err)) return;
      setError(err instanceof Error ? err.message : "Не удалось активировать набор");
    } finally {
      setActivatingId(null);
    }
  };

  return (
    <div>
      <h1 className="mb-4 text-xl font-semibold text-slate-900 dark:text-slate-100">
        Наборы лотов
      </h1>

      <div className="mb-6 rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
        <label className="inline-block cursor-pointer rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-500">
          {uploading ? "Загрузка…" : "Загрузить фид (.xml)"}
          <input type="file" accept=".xml" className="hidden" onChange={onFileChange} disabled={uploading} />
        </label>
        {uploadMessage && (
          <p className="mt-2 text-sm text-emerald-700 dark:text-emerald-400">{uploadMessage}</p>
        )}
      </div>

      {error && (
        <p className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950/40 dark:text-red-400">
          {error}
        </p>
      )}

      {loading ? (
        <p className="text-slate-500 dark:text-slate-400">Загрузка…</p>
      ) : sets.length === 0 ? (
        <p className="text-slate-500 dark:text-slate-400">
          Пока нет ни одного набора — загрузите фид.
        </p>
      ) : (
        <table className="w-full border-collapse overflow-hidden rounded-lg border border-slate-200 bg-white text-sm dark:border-slate-800 dark:bg-slate-900">
          <thead className="bg-slate-50 text-left text-slate-500 dark:bg-slate-800/60 dark:text-slate-400">
            <tr>
              <th className="px-3 py-2">Файл</th>
              <th className="px-3 py-2">Загружен</th>
              <th className="px-3 py-2">Лотов</th>
              <th className="px-3 py-2">Статус</th>
              <th className="px-3 py-2" />
            </tr>
          </thead>
          <tbody>
            {sets.map((set) => (
              <tr
                key={set.id}
                className="border-t border-slate-100 text-slate-900 dark:border-slate-800 dark:text-slate-100"
              >
                <td className="px-3 py-2">{set.name}</td>
                <td className="px-3 py-2 text-slate-500 dark:text-slate-400">
                  {formatDate(set.uploaded_at)}
                </td>
                <td className="px-3 py-2">{set.lots_count}</td>
                <td className="px-3 py-2">
                  {set.is_active ? (
                    <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300">
                      активен
                    </span>
                  ) : (
                    <span className="text-slate-400 dark:text-slate-600">—</span>
                  )}
                </td>
                <td className="px-3 py-2 text-right">
                  {!set.is_active && (
                    <button
                      type="button"
                      onClick={() => activate(set.id)}
                      disabled={activatingId === set.id}
                      className="rounded-md border border-slate-300 px-3 py-1 text-xs font-medium hover:bg-slate-50 disabled:opacity-40 dark:border-slate-700 dark:hover:bg-slate-800"
                    >
                      {activatingId === set.id ? "…" : "Сделать активным"}
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
