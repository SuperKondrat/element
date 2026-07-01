import { API_BASE_URL } from "./config";
import { ApiRequestError } from "./errors";
import type { ApiClient } from "./types";
import type {
  Application,
  ApplicationCreate,
  Booking,
  BookingCreate,
  Lot,
  LotFilter,
  LotListResponse,
  LotSet,
  LotSetUploadResult,
} from "../types";

async function request<T>(path: string, init: RequestInit = {}, token?: string): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body !== undefined && !(init.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = (await response.json()) as { detail?: string };
      detail = body.detail ?? detail;
    } catch {
      // тело не JSON — оставляем statusText
    }
    throw new ApiRequestError(response.status, null, detail);
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

function buildQuery(filter: LotFilter): string {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filter)) {
    if (value !== undefined && value !== null && value !== "") {
      params.set(key, String(value));
    }
  }
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

export const restApiClient: ApiClient = {
  login(username, password) {
    return request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
  },

  listLots(filter): Promise<LotListResponse> {
    return request(`/api/lots${buildQuery(filter)}`);
  },

  getLot(id): Promise<Lot> {
    return request(`/api/lots/${id}`);
  },

  createBooking(data: BookingCreate): Promise<Booking> {
    return request("/api/bookings", { method: "POST", body: JSON.stringify(data) });
  },

  createApplication(data: ApplicationCreate): Promise<Application> {
    return request("/api/applications", { method: "POST", body: JSON.stringify(data) });
  },

  adminListBookings(token): Promise<Booking[]> {
    return request("/api/admin/bookings", {}, token);
  },

  adminListApplications(token): Promise<Application[]> {
    return request("/api/admin/applications", {}, token);
  },

  adminListLotSets(token): Promise<LotSet[]> {
    return request("/api/admin/lot-sets", {}, token);
  },

  adminActivateLotSet(token, setId): Promise<LotSet> {
    return request(`/api/admin/lot-sets/${setId}/activate`, { method: "POST" }, token);
  },

  adminUploadFeed(token, file): Promise<LotSetUploadResult> {
    const formData = new FormData();
    formData.append("file", file);
    return request("/api/admin/lot-sets/upload", { method: "POST", body: formData }, token);
  },
};
