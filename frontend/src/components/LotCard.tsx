import { Link } from "react-router-dom";
import type { Lot } from "../types";
import { StatusBadge } from "./StatusBadge";
import { formatArea, formatPrice, formatRooms } from "../lib/format";

export function LotCard({ lot }: { lot: Lot }) {
  return (
    <Link
      to={`/lots/${lot.id}`}
      className="block rounded-lg border border-slate-200 bg-white p-4 transition-colors hover:shadow-md dark:border-slate-800 dark:bg-slate-900 dark:hover:border-slate-700"
    >
      <div className="mb-2 flex items-start justify-between gap-2">
        <h3 className="font-semibold text-slate-900 dark:text-slate-100">{lot.project_name}</h3>
        <StatusBadge status={lot.status} />
      </div>
      <p className="mb-3 text-sm text-slate-500 dark:text-slate-400">{lot.address}</p>
      <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-slate-700 dark:text-slate-300">
        <span>{formatRooms(lot.rooms)}</span>
        <span>{formatArea(lot.area)}</span>
        <span>этаж {lot.floor}</span>
      </div>
      <div className="mt-3 flex items-baseline justify-between">
        <span className="text-lg font-semibold text-slate-900 dark:text-slate-100">
          {formatPrice(lot.price)}
        </span>
        {lot.price_per_sqm ? (
          <span className="text-xs text-slate-500 dark:text-slate-400">
            {formatPrice(lot.price_per_sqm)} / м²
          </span>
        ) : null}
      </div>
    </Link>
  );
}
