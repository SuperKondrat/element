import { useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import type { ApiRequestError } from "../../api/errors";

/** Если токен истёк/недействителен — разлогинивает и уводит на /admin/login.
 * Возвращает true, если ошибка была обработана (вызывающий код должен
 * прекратить дальнейшую обработку).
 *
 * Обёрнуто в useCallback: без этого каждый рендер отдавал бы новую ссылку
 * на функцию, ломая useCallback/useEffect на страницах-потребителях
 * (FeedsPage и т.п.) и вызывая бесконечный цикл повторных запросов. */
export function useAdminGuard() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  return useCallback(
    (error: ApiRequestError): boolean => {
      if (!error.isUnauthorized) return false;
      logout();
      navigate("/admin/login", { replace: true });
      return true;
    },
    [logout, navigate],
  );
}
