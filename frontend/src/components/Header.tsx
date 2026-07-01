import { Link, NavLink } from "react-router-dom";
import { TransportToggle } from "./TransportToggle";
import { ThemeToggle } from "./ThemeToggle";
import { useAuth } from "../context/AuthContext";

export function Header() {
  const { isAuthenticated, logout } = useAuth();

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
      isActive
        ? "bg-indigo-600 text-white"
        : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
    }`;

  return (
    <header className="border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3">
        <Link to="/" className="text-lg font-semibold text-slate-900 dark:text-slate-100">
          Выборщик лотов
        </Link>

        <nav className="flex items-center gap-1">
          <NavLink to="/" end className={linkClass}>
            Витрина
          </NavLink>
          {isAuthenticated ? (
            <>
              <NavLink to="/admin/feeds" className={linkClass}>
                Фиды
              </NavLink>
              <NavLink to="/admin/bookings" className={linkClass}>
                Брони
              </NavLink>
              <NavLink to="/admin/applications" className={linkClass}>
                Заявки
              </NavLink>
              <button
                type="button"
                onClick={logout}
                className="rounded-md px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
              >
                Выйти
              </button>
            </>
          ) : (
            <NavLink to="/admin/login" className={linkClass}>
              Админка
            </NavLink>
          )}
        </nav>

        <div className="flex items-center gap-2">
          <TransportToggle />
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
