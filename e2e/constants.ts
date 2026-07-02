import { loadProjectEnv } from "./load-env";

const projectEnv = loadProjectEnv();

export const BACKEND_PORT = projectEnv.BACKEND_PORT ?? "8000";
export const FRONTEND_PORT = projectEnv.FRONTEND_PORT ?? "5173";
// 127.0.0.1, а не localhost: на некоторых Windows-хостах localhost резолвится
// в ::1, и Playwright/uvicorn получают EACCES при подключении по IPv6-loopback.
export const BACKEND_URL = `http://127.0.0.1:${BACKEND_PORT}`;
export const FRONTEND_URL = `http://127.0.0.1:${FRONTEND_PORT}`;
export const ADMIN_USERNAME = projectEnv.ADMIN_USERNAME ?? "";
export const ADMIN_PASSWORD = projectEnv.ADMIN_PASSWORD ?? "";
