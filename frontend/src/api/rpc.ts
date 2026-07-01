import { API_BASE_URL } from "./config";
import { ApiRequestError } from "./errors";
import type { ApiClient } from "./types";
import type {
  Application,
  ApplicationCreate,
  Booking,
  BookingCreate,
  Lot,
  LotListResponse,
  LotSet,
  LotSetUploadResult,
} from "../types";

interface RpcSuccess<T> {
  jsonrpc: "2.0";
  result: T;
  id: number;
}

interface RpcFailure {
  jsonrpc: "2.0";
  error: { code: number; message: string; data?: unknown };
  id: number | null;
}

let requestCounter = 0;

async function call<T>(method: string, params: Record<string, unknown> = {}, token?: string): Promise<T> {
  const headers = new Headers({ "Content-Type": "application/json" });
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}/rpc`, {
    method: "POST",
    headers,
    body: JSON.stringify({ jsonrpc: "2.0", method, params, id: ++requestCounter }),
  });

  if (!response.ok) {
    throw new ApiRequestError(response.status, null, response.statusText);
  }

  const body = (await response.json()) as RpcSuccess<T> | RpcFailure;
  if ("error" in body) {
    throw new ApiRequestError(null, body.error.code, body.error.message);
  }
  return body.result;
}

async function fileToBase64(file: File): Promise<string> {
  const buffer = await file.arrayBuffer();
  const bytes = new Uint8Array(buffer);
  let binary = "";
  const chunkSize = 0x8000;
  for (let i = 0; i < bytes.length; i += chunkSize) {
    binary += String.fromCharCode(...bytes.subarray(i, i + chunkSize));
  }
  return btoa(binary);
}

export const rpcApiClient: ApiClient = {
  login(username, password) {
    return call("auth.login", { username, password });
  },

  listLots(filter): Promise<LotListResponse> {
    return call("lots.list", { ...filter });
  },

  getLot(id): Promise<Lot> {
    return call("lots.get", { lot_id: id });
  },

  createBooking(data: BookingCreate): Promise<Booking> {
    return call("bookings.create", { ...data });
  },

  createApplication(data: ApplicationCreate): Promise<Application> {
    return call("applications.create", { ...data });
  },

  adminListBookings(token): Promise<Booking[]> {
    return call("admin.bookings.list", {}, token);
  },

  adminListApplications(token): Promise<Application[]> {
    return call("admin.applications.list", {}, token);
  },

  adminListLotSets(token): Promise<LotSet[]> {
    return call("admin.lot_sets.list", {}, token);
  },

  adminActivateLotSet(token, setId): Promise<LotSet> {
    return call("admin.lot_sets.activate", { set_id: setId }, token);
  },

  async adminUploadFeed(token, file): Promise<LotSetUploadResult> {
    const content_base64 = await fileToBase64(file);
    return call("admin.lot_sets.upload", { filename: file.name, content_base64 }, token);
  },
};
