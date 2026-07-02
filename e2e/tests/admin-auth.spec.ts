import { expect, test } from "@playwright/test";
import { ADMIN_PASSWORD, ADMIN_USERNAME } from "../constants";

test("unauthenticated visitor is redirected from admin pages to login", async ({ page }) => {
  await page.goto("/admin/feeds");
  await expect(page).toHaveURL(/\/admin\/login$/);
});

test("wrong password shows an error and does not log in", async ({ page }) => {
  await page.goto("/admin/login");
  await page.getByPlaceholder("Логин").fill(ADMIN_USERNAME);
  await page.getByPlaceholder("Пароль").fill("definitely-wrong-password");
  await page.getByRole("button", { name: "Войти" }).click();

  await expect(page.getByText("Неверный логин или пароль")).toBeVisible();
  await expect(page).toHaveURL(/\/admin\/login$/);
});

test("correct credentials log the admin in and unlock the admin nav", async ({ page }) => {
  await page.goto("/admin/login");
  await page.getByPlaceholder("Логин").fill(ADMIN_USERNAME);
  await page.getByPlaceholder("Пароль").fill(ADMIN_PASSWORD);
  await page.getByRole("button", { name: "Войти" }).click();

  await expect(page).toHaveURL(/\/admin\/feeds$/);
  await expect(page.getByRole("heading", { name: "Наборы лотов" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Брони" })).toBeVisible();
});
