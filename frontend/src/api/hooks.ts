import { useQuery } from '@tanstack/react-query';
import type { FilterState, PerformanceDay, Station, Summary } from './types';

// In dev the Vite proxy forwards /api/* → http://localhost:8000
// In production set VITE_API_URL to the backend origin
const BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? '';

function buildParams(filters: FilterState): URLSearchParams {
  const p = new URLSearchParams();
  p.set('period', filters.period);
  if (filters.corridorOnly) p.set('corridor_only', 'true');
  if (filters.trainNumber) p.set('train_number', filters.trainNumber);
  if (filters.stationCode) p.set('station_code', filters.stationCode);
  return p;
}

async function fetchJson<T>(path: string, params?: URLSearchParams): Promise<T> {
  const url = params ? `${BASE}${path}?${params}` : `${BASE}${path}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`API error ${res.status}: ${res.statusText}`);
  return res.json() as Promise<T>;
}

export function usePerformance(filters: FilterState) {
  return useQuery<PerformanceDay[], Error>({
    queryKey: ['performance', filters],
    queryFn: () => fetchJson<PerformanceDay[]>('/api/performance', buildParams(filters)),
    staleTime: 5 * 60 * 1000,
  });
}

export function useSummary(filters: FilterState) {
  return useQuery<Summary, Error>({
    queryKey: ['summary', filters],
    queryFn: () => fetchJson<Summary>('/api/summary', buildParams(filters)),
    staleTime: 5 * 60 * 1000,
  });
}

export function useStations(corridorOnly = false) {
  const params = new URLSearchParams();
  if (corridorOnly) params.set('corridor_only', 'true');
  return useQuery<Station[], Error>({
    queryKey: ['stations', corridorOnly],
    queryFn: () => fetchJson<Station[]>('/api/stations', params),
    staleTime: 10 * 60 * 1000,
  });
}
