import { describe, expect, it } from "vitest";
import { formatRussianPhone, isCompleteRussianPhone } from "./phone";

describe("formatRussianPhone", () => {
  it("returns empty string for empty input", () => {
    expect(formatRussianPhone("")).toBe("");
  });

  it("progressively formats digits as they are typed", () => {
    expect(formatRussianPhone("9")).toBe("+7 (9");
    expect(formatRussianPhone("999")).toBe("+7 (999)");
    expect(formatRussianPhone("999123")).toBe("+7 (999) 123");
    expect(formatRussianPhone("99912345")).toBe("+7 (999) 123-45");
    expect(formatRussianPhone("9991234567")).toBe("+7 (999) 123-45-67");
  });

  it("strips a leading country code digit (7 or 8)", () => {
    expect(formatRussianPhone("79991234567")).toBe("+7 (999) 123-45-67");
    expect(formatRussianPhone("89991234567")).toBe("+7 (999) 123-45-67");
  });

  it("ignores non-digit characters", () => {
    expect(formatRussianPhone("+7 (999) 123-45-67")).toBe("+7 (999) 123-45-67");
  });

  it("truncates input beyond 10 significant digits", () => {
    expect(formatRussianPhone("79991234567999")).toBe("+7 (999) 123-45-67");
  });
});

describe("isCompleteRussianPhone", () => {
  it("accepts a fully formatted phone", () => {
    expect(isCompleteRussianPhone("+7 (999) 123-45-67")).toBe(true);
  });

  it.each([
    "+7 (999) 123-45",
    "+79991234567",
    "89991234567",
    "не телефон",
    "",
  ])("rejects %s", (value) => {
    expect(isCompleteRussianPhone(value)).toBe(false);
  });
});
