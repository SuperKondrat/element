import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import { restApiClient } from "../api/rest";
import { rpcApiClient } from "../api/rpc";
import type { ApiClient } from "../api/types";

export type Transport = "rest" | "rpc";

const STORAGE_KEY = "element:transport";

interface TransportContextValue {
  transport: Transport;
  setTransport: (transport: Transport) => void;
  api: ApiClient;
}

const TransportContext = createContext<TransportContextValue | null>(null);

function readInitialTransport(): Transport {
  const stored = window.localStorage.getItem(STORAGE_KEY);
  return stored === "rpc" ? "rpc" : "rest";
}

export function TransportProvider({ children }: { children: ReactNode }) {
  const [transport, setTransportState] = useState<Transport>(readInitialTransport);

  const setTransport = (next: Transport) => {
    setTransportState(next);
    window.localStorage.setItem(STORAGE_KEY, next);
  };

  const api = useMemo<ApiClient>(
    () => (transport === "rest" ? restApiClient : rpcApiClient),
    [transport],
  );

  const value = useMemo(() => ({ transport, setTransport, api }), [transport, api]);

  return <TransportContext.Provider value={value}>{children}</TransportContext.Provider>;
}

export function useTransport(): TransportContextValue {
  const ctx = useContext(TransportContext);
  if (!ctx) throw new Error("useTransport должен использоваться внутри TransportProvider");
  return ctx;
}

export function useApi(): ApiClient {
  return useTransport().api;
}
