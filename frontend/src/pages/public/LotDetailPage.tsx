import { useEffect, useState, type FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import { useApi } from "../../context/TransportContext";
import { ApiRequestError } from "../../api/errors";
import type { Lot } from "../../types";
import { StatusBadge } from "../../components/StatusBadge";
import { formatArea, formatPrice, formatRooms } from "../../lib/format";
import { formatRussianPhone, isCompleteRussianPhone } from "../../lib/phone";
import { isValidEmail } from "../../lib/validation";

/** Хотя бы один способ связи указан и оба заполненных поля корректны. */
function isContactValid(name: string, phone: string, email: string): boolean {
  if (!name.trim()) return false;
  if (!phone && !email) return false;
  if (phone && !isCompleteRussianPhone(phone)) return false;
  if (email && !isValidEmail(email)) return false;
  return true;
}

export function LotDetailPage() {
  const { id } = useParams<{ id: string }>();
  const api = useApi();
  const lotId = Number(id);

  const [lot, setLot] = useState<Lot | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    setLot(null);
    setLoadError(null);
    api
      .getLot(lotId)
      .then(setLot)
      .catch((err: unknown) =>
        setLoadError(err instanceof Error ? err.message : "Лот не найден"),
      );
  }, [api, lotId]);

  if (loadError) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-6">
        <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950/40 dark:text-red-400">
          {loadError}
        </p>
        <Link
          to="/"
          className="mt-4 inline-block text-sm text-slate-600 underline dark:text-slate-400"
        >
          ← к списку лотов
        </Link>
      </div>
    );
  }

  if (!lot) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-6 text-slate-500 dark:text-slate-400">
        Загрузка…
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-6">
      <Link
        to="/"
        className="mb-4 inline-block text-sm text-slate-600 underline dark:text-slate-400"
      >
        ← к списку лотов
      </Link>

      <div className="mb-6 rounded-lg border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
        <div className="mb-2 flex items-start justify-between gap-2">
          <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">
            {lot.project_name}
          </h1>
          <StatusBadge status={lot.status} />
        </div>
        <p className="mb-4 text-sm text-slate-500 dark:text-slate-400">{lot.address}</p>

        <dl className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-3">
          <Field label="Комнатность" value={formatRooms(lot.rooms)} />
          <Field label="Площадь" value={formatArea(lot.area)} />
          <Field label="Этаж" value={String(lot.floor)} />
          <Field label="Цена" value={formatPrice(lot.price)} />
          <Field label="Базовая цена" value={formatPrice(lot.price_base)} />
          {lot.price_per_sqm ? (
            <Field label="Цена за м²" value={formatPrice(lot.price_per_sqm)} />
          ) : null}
        </dl>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <BookingForm lot={lot} onBooked={(updated) => setLot(updated)} />
        <ApplicationForm lotId={lot.id} />
      </div>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-slate-400 dark:text-slate-500">{label}</dt>
      <dd className="font-medium text-slate-900 dark:text-slate-100">{value}</dd>
    </div>
  );
}

function BookingForm({ lot, onBooked }: { lot: Lot; onBooked: (lot: Lot) => void }) {
  const api = useApi();
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const canBook = lot.status === "for_sale";

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await api.createBooking({
        lot_id: lot.id,
        contact_name: name,
        contact_phone: phone || undefined,
        contact_email: email || undefined,
      });
      setSuccess(true);
      onBooked({ ...lot, status: "reserved" });
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "Не удалось забронировать лот");
    } finally {
      setSubmitting(false);
    }
  };

  if (success) {
    return (
      <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800 dark:border-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-300">
        Бронь оформлена. С вами свяжутся для подтверждения.
      </div>
    );
  }

  return (
    <form
      onSubmit={submit}
      className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900"
    >
      <h2 className="mb-3 font-semibold text-slate-900 dark:text-slate-100">Забронировать лот</h2>
      {!canBook && (
        <p className="mb-3 text-sm text-amber-700 dark:text-amber-400">
          Лот сейчас недоступен для брони.
        </p>
      )}
      <ContactFields
        name={name}
        setName={setName}
        phone={phone}
        setPhone={setPhone}
        email={email}
        setEmail={setEmail}
      />
      {error && <p className="mb-2 text-sm text-red-700 dark:text-red-400">{error}</p>}
      <button
        type="submit"
        disabled={!canBook || submitting || !isContactValid(name, phone, email)}
        className="w-full rounded-md bg-indigo-600 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-500 disabled:opacity-40"
      >
        {submitting ? "Отправка…" : "Забронировать"}
      </button>
    </form>
  );
}

function ApplicationForm({ lotId }: { lotId: number }) {
  const api = useApi();
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await api.createApplication({
        lot_id: lotId,
        contact_name: name,
        contact_phone: phone || undefined,
        contact_email: email || undefined,
        comment: comment || undefined,
      });
      setSuccess(true);
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "Не удалось отправить заявку");
    } finally {
      setSubmitting(false);
    }
  };

  if (success) {
    return (
      <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800 dark:border-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-300">
        Заявка отправлена. Мы свяжемся с вами в ближайшее время.
      </div>
    );
  }

  return (
    <form
      onSubmit={submit}
      className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900"
    >
      <h2 className="mb-3 font-semibold text-slate-900 dark:text-slate-100">Оставить заявку</h2>
      <ContactFields
        name={name}
        setName={setName}
        phone={phone}
        setPhone={setPhone}
        email={email}
        setEmail={setEmail}
      />
      <textarea
        className="mb-3 w-full rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm text-slate-900 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
        placeholder="Комментарий (необязательно)"
        rows={3}
        value={comment}
        onChange={(e) => setComment(e.target.value)}
      />
      {error && <p className="mb-2 text-sm text-red-700 dark:text-red-400">{error}</p>}
      <button
        type="submit"
        disabled={submitting || !isContactValid(name, phone, email)}
        className="w-full rounded-md border border-indigo-600 py-2 text-sm font-medium text-indigo-600 transition-colors hover:bg-indigo-50 disabled:opacity-40 dark:text-indigo-400 dark:hover:bg-indigo-950/40"
      >
        {submitting ? "Отправка…" : "Отправить заявку"}
      </button>
    </form>
  );
}

function ContactFields(props: {
  name: string;
  setName: (v: string) => void;
  phone: string;
  setPhone: (v: string) => void;
  email: string;
  setEmail: (v: string) => void;
}) {
  const phoneError = props.phone.length > 0 && !isCompleteRussianPhone(props.phone);
  const emailError = props.email.length > 0 && !isValidEmail(props.email);

  return (
    <div className="mb-3 space-y-2">
      <input
        className="w-full rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm text-slate-900 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
        placeholder="Имя"
        value={props.name}
        onChange={(e) => props.setName(e.target.value)}
        required
      />
      <div>
        <input
          className={`w-full rounded-md border bg-white px-2 py-1.5 text-sm text-slate-900 dark:bg-slate-800 dark:text-slate-100 ${
            phoneError ? "border-red-400 dark:border-red-500" : "border-slate-300 dark:border-slate-700"
          }`}
          placeholder="+7 (___) ___-__-__"
          type="tel"
          inputMode="tel"
          value={props.phone}
          onChange={(e) => props.setPhone(formatRussianPhone(e.target.value))}
        />
        {phoneError && (
          <p className="mt-0.5 text-xs text-red-600 dark:text-red-400">Введите номер полностью</p>
        )}
      </div>
      <div>
        <input
          className={`w-full rounded-md border bg-white px-2 py-1.5 text-sm text-slate-900 dark:bg-slate-800 dark:text-slate-100 ${
            emailError ? "border-red-400 dark:border-red-500" : "border-slate-300 dark:border-slate-700"
          }`}
          placeholder="Почта"
          type="email"
          value={props.email}
          onChange={(e) => props.setEmail(e.target.value)}
        />
        {emailError && (
          <p className="mt-0.5 text-xs text-red-600 dark:text-red-400">Некорректный адрес почты</p>
        )}
      </div>
      <p className="text-xs text-slate-400 dark:text-slate-500">Укажите телефон или почту для связи</p>
    </div>
  );
}
