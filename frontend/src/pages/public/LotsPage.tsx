import { useEffect, useState } from "react";
import { useApi } from "../../context/TransportContext";
import { LotCard } from "../../components/LotCard";
import type { LotFilter, LotListResponse, LotStatus, SortField } from "../../types";
import { LOT_STATUS_LABELS } from "../../types";

const PAGE_SIZE = 12;

const FIELD_CLASS =
  "rounded-md border border-slate-300 bg-white px-2 py-1.5 text-slate-900 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100";

const SORT_OPTIONS: { value: SortField; label: string }[] = [
  { value: "created_at", label: "по дате загрузки" },
  { value: "price", label: "по цене" },
  { value: "price_per_sqm", label: "по цене за м²" },
  { value: "area", label: "по площади" },
  { value: "floor", label: "по этажу" },
];

const EMPTY_LIST: LotListResponse = { items: [], total: 0, page: 1, page_size: PAGE_SIZE };

export function LotsPage() {
  const api = useApi();

  const [projectName, setProjectName] = useState("");
  const [rooms, setRooms] = useState<string>("");
  const [status, setStatus] = useState<LotStatus | "">("");
  const [priceMin, setPriceMin] = useState("");
  const [priceMax, setPriceMax] = useState("");
  const [sortBy, setSortBy] = useState<SortField>("created_at");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [page, setPage] = useState(1);

  const [data, setData] = useState<LotListResponse>(EMPTY_LIST);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const filter: LotFilter = {
      project_name: projectName || undefined,
      rooms: rooms === "" ? undefined : Number(rooms),
      status: status || undefined,
      price_per_sqm_min: priceMin === "" ? undefined : Number(priceMin),
      price_per_sqm_max: priceMax === "" ? undefined : Number(priceMax),
      sort_by: sortBy,
      sort_dir: sortDir,
      page,
      page_size: PAGE_SIZE,
    };

    let cancelled = false;
    setLoading(true);
    setError(null);

    api
      .listLots(filter)
      .then((result) => {
        if (!cancelled) setData(result);
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Не удалось загрузить лоты");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [api, projectName, rooms, status, priceMin, priceMax, sortBy, sortDir, page]);

  const totalPages = Math.max(1, Math.ceil(data.total / PAGE_SIZE));

  const resetToFirstPage = (setter: () => void) => {
    setter();
    setPage(1);
  };

  return (
    <div className="mx-auto max-w-6xl px-4 py-6">
      <h1 className="mb-4 text-2xl font-semibold text-slate-900 dark:text-slate-100">
        Каталог лотов
      </h1>

      <div className="mb-6 grid grid-cols-1 gap-3 rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900 sm:grid-cols-2 lg:grid-cols-4">
        <label className="flex flex-col text-sm text-slate-600 dark:text-slate-400">
          ЖК
          <input
            className={`mt-1 ${FIELD_CLASS}`}
            value={projectName}
            onChange={(e) => resetToFirstPage(() => setProjectName(e.target.value))}
            placeholder="Название ЖК"
          />
        </label>

        <label className="flex flex-col text-sm text-slate-600 dark:text-slate-400">
          Комнатность
          <select
            className={`mt-1 ${FIELD_CLASS}`}
            value={rooms}
            onChange={(e) => resetToFirstPage(() => setRooms(e.target.value))}
          >
            <option value="">любая</option>
            <option value="0">Студия</option>
            {[1, 2, 3, 4, 5].map((r) => (
              <option key={r} value={r}>
                {r}-комн.
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col text-sm text-slate-600 dark:text-slate-400">
          Статус
          <select
            className={`mt-1 ${FIELD_CLASS}`}
            value={status}
            onChange={(e) => resetToFirstPage(() => setStatus(e.target.value as LotStatus | ""))}
          >
            <option value="">любой</option>
            {Object.entries(LOT_STATUS_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>

        <div className="flex flex-col text-sm text-slate-600 dark:text-slate-400">
          Цена за м², ₽
          <div className="mt-1 flex gap-2">
            <input
              className={`w-1/2 ${FIELD_CLASS}`}
              type="number"
              placeholder="от"
              value={priceMin}
              onChange={(e) => resetToFirstPage(() => setPriceMin(e.target.value))}
            />
            <input
              className={`w-1/2 ${FIELD_CLASS}`}
              type="number"
              placeholder="до"
              value={priceMax}
              onChange={(e) => resetToFirstPage(() => setPriceMax(e.target.value))}
            />
          </div>
        </div>

        <label className="flex flex-col text-sm text-slate-600 dark:text-slate-400">
          Сортировка
          <select
            className={`mt-1 ${FIELD_CLASS}`}
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as SortField)}
          >
            {SORT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col text-sm text-slate-600 dark:text-slate-400">
          Направление
          <select
            className={`mt-1 ${FIELD_CLASS}`}
            value={sortDir}
            onChange={(e) => setSortDir(e.target.value as "asc" | "desc")}
          >
            <option value="asc">по возрастанию</option>
            <option value="desc">по убыванию</option>
          </select>
        </label>
      </div>

      {error && (
        <p className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950/40 dark:text-red-400">
          {error}
        </p>
      )}

      {loading ? (
        <p className="text-slate-500 dark:text-slate-400">Загрузка…</p>
      ) : data.items.length === 0 ? (
        <p className="text-slate-500 dark:text-slate-400">
          Лоты не найдены. Проверьте фильтры или активный набор в админке.
        </p>
      ) : (
        <>
          <p className="mb-3 text-sm text-slate-500 dark:text-slate-400">Найдено: {data.total}</p>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {data.items.map((lot) => (
              <LotCard key={lot.id} lot={lot} />
            ))}
          </div>

          {totalPages > 1 && (
            <div className="mt-6 flex items-center justify-center gap-2">
              <button
                type="button"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
                className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-900 disabled:opacity-40 dark:border-slate-700 dark:text-slate-100"
              >
                Назад
              </button>
              <span className="text-sm text-slate-600 dark:text-slate-400">
                стр. {page} из {totalPages}
              </span>
              <button
                type="button"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
                className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-900 disabled:opacity-40 dark:border-slate-700 dark:text-slate-100"
              >
                Вперёд
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
