import { defineConfig } from "@playwright/test";
import { loadProjectEnv } from "./load-env";
import { BACKEND_PORT, BACKEND_URL, FRONTEND_PORT, FRONTEND_URL } from "./constants";

const projectEnv = loadProjectEnv();

const backendEnv = {
  ...process.env,
  POSTGRES_HOST: "localhost",
  POSTGRES_PORT: projectEnv.POSTGRES_PORT ?? "5432",
  POSTGRES_DB: projectEnv.POSTGRES_DB ?? "element",
  POSTGRES_USER: projectEnv.POSTGRES_USER ?? "element",
  POSTGRES_PASSWORD: projectEnv.POSTGRES_PASSWORD ?? "",
  ADMIN_USERNAME: projectEnv.ADMIN_USERNAME ?? "",
  ADMIN_PASSWORD: projectEnv.ADMIN_PASSWORD ?? "",
  JWT_SECRET_KEY: projectEnv.JWT_SECRET_KEY ?? "",
  JWT_ALGORITHM: projectEnv.JWT_ALGORITHM ?? "HS256",
  JWT_EXPIRE_MINUTES: projectEnv.JWT_EXPIRE_MINUTES ?? "60",
  CORS_ORIGINS: FRONTEND_URL,
  LOG_LEVEL: projectEnv.LOG_LEVEL ?? "warning",
  MAX_FEED_SIZE_MB: projectEnv.MAX_FEED_SIZE_MB ?? "64",
};

export default defineConfig({
  testDir: "./tests",
  fullyParallel: false,
  workers: 1,
  reporter: [["list"]],
  use: {
    baseURL: FRONTEND_URL,
    trace: "retain-on-failure",
  },
  webServer: [
    {
      command: `uv run uvicorn app.main:app --host 0.0.0.0 --port ${BACKEND_PORT}`,
      cwd: "../backend",
      env: backendEnv,
      url: `${BACKEND_URL}/api/lots`,
      reuseExistingServer: !process.env.CI,
      timeout: 30_000,
    },
    {
      command: `npm run dev -- --port ${FRONTEND_PORT}`,
      cwd: "../frontend",
      env: { ...process.env, VITE_API_BASE_URL: BACKEND_URL },
      url: FRONTEND_URL,
      reuseExistingServer: !process.env.CI,
      timeout: 30_000,
    },
  ],
});
