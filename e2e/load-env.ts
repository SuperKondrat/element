import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

/** Простой .env-парсер (KEY=VALUE), без внешних зависимостей. */
function parseEnvFile(path: string): Record<string, string> {
  const result: Record<string, string> = {};
  let content: string;
  try {
    content = readFileSync(path, "utf-8");
  } catch {
    return result;
  }
  for (const line of content.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eq = trimmed.indexOf("=");
    if (eq === -1) continue;
    result[trimmed.slice(0, eq).trim()] = trimmed.slice(eq + 1).trim();
  }
  return result;
}

const root = fileURLToPath(new URL("..", import.meta.url));

/**
 * Читает те же файлы, что и `docker compose` (config/app.env + .env), чтобы
 * backend, поднятый Playwright'ом, подключался к той же локальной БД теми
 * же учётными данными, не дублируя секреты в этом репозитории.
 */
export function loadProjectEnv(): Record<string, string> {
  return {
    ...parseEnvFile(`${root}config/app.env`),
    ...parseEnvFile(`${root}.env`),
  };
}
