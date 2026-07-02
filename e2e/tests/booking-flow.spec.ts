import { expect, test, type Page } from "@playwright/test";
import { ADMIN_PASSWORD, ADMIN_USERNAME } from "../constants";
import { buildFeedXml } from "../fixtures/feed";

async function loginAsAdmin(page: Page): Promise<void> {
  await page.goto("/admin/login");
  await page.getByPlaceholder("Логин").fill(ADMIN_USERNAME);
  await page.getByPlaceholder("Пароль").fill(ADMIN_PASSWORD);
  await page.getByRole("button", { name: "Войти" }).click();
  await expect(page).toHaveURL(/\/admin\/feeds$/);
}

test("admin uploads and activates a feed, visitor books the lot from the public showcase", async ({
  page,
}) => {
  const runId = Date.now();
  const projectName = `E2E ЖК ${runId}`;
  const feedFileName = `e2e-feed-${runId}.xml`;
  const contactName = `E2E Покупатель ${runId}`;

  await loginAsAdmin(page);

  await page
    .getByLabel("Загрузить фид (.xml)")
    .setInputFiles({ name: feedFileName, mimeType: "application/xml", buffer: Buffer.from(buildFeedXml(projectName)) });
  await expect(page.getByText("Загружено 1 лотов")).toBeVisible();

  const feedRow = page.getByRole("row", { name: new RegExp(feedFileName) });
  await expect(feedRow).toBeVisible();
  await feedRow.getByRole("button", { name: "Сделать активным" }).click();
  await expect(feedRow.getByText("активен")).toBeVisible();

  await page.goto("/");
  await page.getByPlaceholder("Название ЖК").fill(projectName);
  await expect(page.getByText("Найдено: 1")).toBeVisible();
  await page.getByRole("heading", { name: projectName }).click();

  await expect(page).toHaveURL(/\/lots\/\d+$/);
  await expect(page.getByText("в продаже")).toBeVisible();

  const bookingForm = page.locator("form", { hasText: "Забронировать лот" });
  await bookingForm.getByPlaceholder("Имя").fill(contactName);
  await bookingForm.getByPlaceholder("+7 (___) ___-__-__").fill("9991234567");
  await bookingForm.getByRole("button", { name: "Забронировать" }).click();

  await expect(page.getByText("Бронь оформлена. С вами свяжутся для подтверждения.")).toBeVisible();
  await expect(page.getByText("забронирован")).toBeVisible();

  await page.goto("/admin/bookings");
  await expect(page.getByRole("row", { name: new RegExp(contactName) })).toBeVisible();
});

test("a lot that is not for sale cannot be booked", async ({ page }) => {
  const runId = Date.now();
  const projectName = `E2E Sold Lot ${runId}`;
  const feedFileName = `e2e-feed-sold-${runId}.xml`;

  const soldFeedXml = buildFeedXml(projectName).replace("<status>FREE</status>", "<status>SOLD</status>");

  await loginAsAdmin(page);
  await page
    .getByLabel("Загрузить фид (.xml)")
    .setInputFiles({ name: feedFileName, mimeType: "application/xml", buffer: Buffer.from(soldFeedXml) });
  await expect(page.getByText("Загружено 1 лотов")).toBeVisible();

  const feedRow = page.getByRole("row", { name: new RegExp(feedFileName) });
  await feedRow.getByRole("button", { name: "Сделать активным" }).click();
  await expect(feedRow.getByText("активен")).toBeVisible();

  await page.goto("/");
  await page.getByPlaceholder("Название ЖК").fill(projectName);
  await page.getByRole("heading", { name: projectName }).click();

  const detailHeading = page.getByRole("heading", { level: 1, name: projectName });
  await expect(detailHeading).toBeVisible();
  await expect(detailHeading.locator("..").getByText("продано")).toBeVisible();
  await expect(page.getByText("Лот сейчас недоступен для брони.")).toBeVisible();
  await expect(page.locator("form", { hasText: "Забронировать лот" }).getByRole("button", { name: "Забронировать" })).toBeDisabled();
});
