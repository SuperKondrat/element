#!/usr/bin/env node
// Единый раннер для всех тестов проекта: backend (pytest), frontend (vitest), e2e (playwright).
// Кроссплатформенный (Windows/macOS/Linux) — не зависит от bash/PowerShell-синтаксиса.
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("..", import.meta.url));

function loadEnvFile(path) {
  const result = {};
  let content;
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

const projectEnv = {
  ...loadEnvFile(`${root}config/app.env`),
  ...loadEnvFile(`${root}.env`),
};

function sleepSync(ms) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}

function step(title) {
  console.log(`\n\x1b[36m== ${title} ==\x1b[0m`);
}

function run(command, args, { cwd = root, env = {} } = {}) {
  const commandLine = [command, ...args].join(" ");
  console.log(`$ ${commandLine}`);
  const mergedEnv = { ...process.env, ...env };
  // Полная команда одной строкой (а не command+args с shell:true) — так, как
  // рекомендует Node, чтобы не ловить DEP0190. Все аргументы здесь заданы
  // нами самими (фиксированные литералы), а не пользовательским вводом.
  const result = spawnSync(commandLine, {
    stdio: "inherit",
    shell: true,
    cwd,
    env: mergedEnv,
  });
  if (result.status !== 0) {
    console.error(`\n\x1b[31mШаг завершился с ошибкой: ${command} ${args.join(" ")}\x1b[0m`);
    process.exit(result.status ?? 1);
  }
}

const backendDbEnv = {
  POSTGRES_HOST: "localhost",
  POSTGRES_PORT: projectEnv.POSTGRES_PORT ?? "5432",
  POSTGRES_DB: projectEnv.POSTGRES_DB ?? "element",
  POSTGRES_USER: projectEnv.POSTGRES_USER ?? "element",
  POSTGRES_PASSWORD: projectEnv.POSTGRES_PASSWORD ?? "",
};

function waitForDb() {
  step("Жду готовности postgres");
  for (let attempt = 1; attempt <= 30; attempt++) {
    const check = spawnSync("docker", ["compose", "exec", "-T", "db", "pg_isready"], {
      stdio: "ignore",
      shell: true,
      cwd: root,
    });
    if (check.status === 0) {
      console.log("БД готова.");
      return;
    }
    sleepSync(1000);
  }
  console.error("БД не поднялась за 30 секунд.");
  process.exit(1);
}

// Идемпотентно и безопасно: создаёт только отсутствующие таблицы, ничего не
// удаляет и не трогает существующие данные. Нужен для e2e (реальный uvicorn
// не создаёт схему сам), при этом backend-тесты управляют своей схемой сами
// (см. backend/tests/conftest.py).
function ensureSchema() {
  step("Проверяю схему БД (create_all, если чего-то не хватает)");
  run("uv", ["run", "python", "-m", "scripts.ensure_schema"], {
    cwd: `${root}backend`,
    env: {
      ...backendDbEnv,
      ADMIN_USERNAME: projectEnv.ADMIN_USERNAME ?? "admin",
      ADMIN_PASSWORD: projectEnv.ADMIN_PASSWORD ?? "admin123",
      JWT_SECRET_KEY: projectEnv.JWT_SECRET_KEY ?? "local-test-secret-key",
    },
  });
}

// pytest сам создаёт и удаляет свою схему за сессию (см. conftest.py), но
// требует, чтобы стартовать было не с чем — иначе чужие данные (например, от
// e2e-прогона) ломают тесты вида "витрина пустая по умолчанию". Дропаем те же
// таблицы, которые и так дропнул бы pytest в конце своей сессии.
function resetSchema() {
  step("Сбрасываю схему БД перед backend-тестами (drop_all)");
  run("uv", ["run", "python", "-m", "scripts.reset_schema"], {
    cwd: `${root}backend`,
    env: {
      ...backendDbEnv,
      ADMIN_USERNAME: projectEnv.ADMIN_USERNAME ?? "admin",
      ADMIN_PASSWORD: projectEnv.ADMIN_PASSWORD ?? "admin123",
      JWT_SECRET_KEY: projectEnv.JWT_SECRET_KEY ?? "local-test-secret-key",
    },
  });
}

function runBackend() {
  step("Backend: pytest (unit + integration)");
  run("uv", ["run", "pytest", "-q"], {
    cwd: `${root}backend`,
    env: backendDbEnv,
    // conftest.py сам жёстко проставляет тестовые ADMIN_*/JWT_SECRET_KEY
    // (admin123/test-secret-key), независимо от того, что уже есть в env —
    // значит, передавать их сюда или вычищать не нужно (см. tests/conftest.py).
  });
}

function runFrontend() {
  step("Frontend: vitest (unit)");
  run("npm", ["run", "test"], { cwd: `${root}frontend` });
}

function runE2e() {
  step("E2E: playwright (поднимет backend + frontend сам)");
  run("npx", ["playwright", "test"], { cwd: `${root}e2e` });
}

const suite = process.argv[2] ?? "all";

if (suite === "backend") {
  run("docker", ["compose", "up", "-d", "db"]);
  waitForDb();
  resetSchema();
  runBackend();
} else if (suite === "frontend") {
  runFrontend();
} else if (suite === "e2e") {
  run("docker", ["compose", "up", "-d", "db"]);
  waitForDb();
  ensureSchema();
  runE2e();
} else if (suite === "all") {
  run("docker", ["compose", "up", "-d", "db"]);
  waitForDb();
  resetSchema();
  runBackend();
  runFrontend();
  ensureSchema(); // backend pytest роняет свою схему в конце сессии — досоздаём перед e2e
  runE2e();
} else {
  console.error(`Неизвестный набор тестов: ${suite}. Используйте: all | backend | frontend | e2e`);
  process.exit(1);
}

console.log("\n\x1b[32mВсе тесты пройдены.\x1b[0m");
