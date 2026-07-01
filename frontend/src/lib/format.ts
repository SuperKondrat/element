const currencyFormatter = new Intl.NumberFormat("ru-RU", {
  style: "currency",
  currency: "RUB",
  maximumFractionDigits: 0,
});

export function formatPrice(value: number): string {
  return currencyFormatter.format(value);
}

export function formatArea(value: number): string {
  return `${value.toLocaleString("ru-RU")} м²`;
}

export function formatRooms(rooms: number): string {
  return rooms === 0 ? "Студия" : `${rooms}-комн.`;
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleString("ru-RU", { dateStyle: "medium", timeStyle: "short" });
}
