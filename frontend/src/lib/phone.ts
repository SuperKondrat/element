const DIGITS_AFTER_CODE = 10;

/** Прогрессивно форматирует ввод в маску +7 (XXX) XXX-XX-XX по мере набора цифр. */
export function formatRussianPhone(rawValue: string): string {
  let digits = rawValue.replace(/\D/g, "");
  if (digits.startsWith("7") || digits.startsWith("8")) {
    digits = digits.slice(1);
  }
  digits = digits.slice(0, DIGITS_AFTER_CODE);

  if (digits.length === 0) return "";

  let result = `+7 (${digits.slice(0, 3)}`;
  if (digits.length >= 3) result += ")";
  if (digits.length > 3) result += ` ${digits.slice(3, 6)}`;
  if (digits.length > 6) result += `-${digits.slice(6, 8)}`;
  if (digits.length > 8) result += `-${digits.slice(8, 10)}`;
  return result;
}

const COMPLETE_PHONE_PATTERN = /^\+7 \(\d{3}\) \d{3}-\d{2}-\d{2}$/;

export function isCompleteRussianPhone(value: string): boolean {
  return COMPLETE_PHONE_PATTERN.test(value);
}
