export class ApiRequestError extends Error {
  status: number | null;
  code: number | null;

  constructor(status: number | null, code: number | null, message: string) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
    this.code = code;
  }

  /** true, если сервер ответил 401 / RPC-код "недействительный токен". */
  get isUnauthorized(): boolean {
    return this.status === 401 || this.code === -32004;
  }
}
