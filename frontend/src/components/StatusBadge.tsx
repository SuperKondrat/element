import { LOT_STATUS_LABELS, type LotStatus } from "../types";

const STYLES: Record<LotStatus, string> = {
  for_sale: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300",
  reserved: "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300",
  sold: "bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
};

export function StatusBadge({ status }: { status: LotStatus }) {
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${STYLES[status]}`}>
      {LOT_STATUS_LABELS[status]}
    </span>
  );
}
