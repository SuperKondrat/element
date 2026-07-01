export type LotStatus = "for_sale" | "reserved" | "sold";

export interface Lot {
  id: number;
  external_id: string;
  set_id: number;
  project_name: string;
  address: string;
  rooms: number;
  area: number;
  floor: number;
  price: number;
  price_base: number;
  price_per_sqm: number | null;
  status: LotStatus;
  created_at: string;
  updated_at: string;
}

export type SortField = "price" | "price_per_sqm" | "area" | "floor" | "created_at";
export type SortDirection = "asc" | "desc";

export interface LotFilter {
  project_name?: string;
  rooms?: number;
  status?: LotStatus;
  price_per_sqm_min?: number;
  price_per_sqm_max?: number;
  sort_by?: SortField;
  sort_dir?: SortDirection;
  page?: number;
  page_size?: number;
}

export interface LotListResponse {
  items: Lot[];
  total: number;
  page: number;
  page_size: number;
}

export interface LotSet {
  id: number;
  name: string;
  uploaded_at: string;
  lots_count: number;
  is_active: boolean;
}

export interface LotSetUploadResult extends LotSet {
  skipped_count: number;
}

export type BookingStatus = "active" | "cancelled";

export interface Booking {
  id: number;
  lot_id: number;
  contact_name: string;
  contact_phone: string | null;
  contact_email: string | null;
  status: BookingStatus;
  created_at: string;
}

export interface BookingCreate {
  lot_id: number;
  contact_name: string;
  contact_phone?: string;
  contact_email?: string;
}

export type ApplicationStatus = "new" | "in_progress" | "closed";

export interface Application {
  id: number;
  lot_id: number | null;
  contact_name: string;
  contact_phone: string | null;
  contact_email: string | null;
  comment: string | null;
  status: ApplicationStatus;
  created_at: string;
}

export interface ApplicationCreate {
  lot_id?: number;
  contact_name: string;
  contact_phone?: string;
  contact_email?: string;
  comment?: string;
}

export const LOT_STATUS_LABELS: Record<LotStatus, string> = {
  for_sale: "в продаже",
  reserved: "забронирован",
  sold: "продано",
};

export const APPLICATION_STATUS_LABELS: Record<ApplicationStatus, string> = {
  new: "новая",
  in_progress: "в работе",
  closed: "закрыта",
};

export const BOOKING_STATUS_LABELS: Record<BookingStatus, string> = {
  active: "активна",
  cancelled: "отменена",
};
