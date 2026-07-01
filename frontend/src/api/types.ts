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

/** Общий интерфейс транспорта — REST- и RPC-клиенты реализуют его одинаково,
 * страницы/компоненты работают только с этим интерфейсом через useApi(),
 * не зная, какой протокол активен (см. п.8.2 PLAN.md). */
export interface ApiClient {
  login(username: string, password: string): Promise<{ access_token: string }>;

  listLots(filter: LotFilter): Promise<LotListResponse>;
  getLot(id: number): Promise<Lot>;

  createBooking(data: BookingCreate): Promise<Booking>;
  createApplication(data: ApplicationCreate): Promise<Application>;

  adminListBookings(token: string): Promise<Booking[]>;
  adminListApplications(token: string): Promise<Application[]>;
  adminListLotSets(token: string): Promise<LotSet[]>;
  adminActivateLotSet(token: string, setId: number): Promise<LotSet>;
  adminUploadFeed(token: string, file: File): Promise<LotSetUploadResult>;
}
