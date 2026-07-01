import { useTransport } from "../context/TransportContext";

export function TransportToggle() {
  const { transport, setTransport } = useTransport();

  return (
    <div className="inline-flex items-center rounded-full border border-slate-300 bg-white p-0.5 text-sm dark:border-slate-700 dark:bg-slate-800">
      {(["rest", "rpc"] as const).map((option) => (
        <button
          key={option}
          type="button"
          onClick={() => setTransport(option)}
          className={`rounded-full px-3 py-1 font-medium uppercase tracking-wide transition-colors ${
            transport === option
              ? "bg-indigo-600 text-white"
              : "text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
          }`}
        >
          {option}
        </button>
      ))}
    </div>
  );
}
