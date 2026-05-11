import { useState, useEffect, useCallback } from 'react';
import type { PerformanceResponse, PerformanceFilters } from './types';

function buildQuery(filters: PerformanceFilters): string {
  const params = new URLSearchParams();
  if (filters.period) params.set('period', filters.period);
  if (filters.corridor_only) params.set('corridor_only', 'true');
  if (filters.train_number) params.set('train_number', filters.train_number);
  if (filters.station_code) params.set('station_code', filters.station_code);
  const qs = params.toString();
  return qs ? `?${qs}` : '';
}

export function usePerformance(filters: PerformanceFilters) {
  const [data, setData] = useState<PerformanceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch_ = useCallback(() => {
    setLoading(true);
    setError(null);
    fetch(`/api/performance${buildQuery(filters)}`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json() as Promise<PerformanceResponse>;
      })
      .then(setData)
      .catch((e: unknown) => setError(String(e)))
      .finally(() => setLoading(false));
  }, [filters.period, filters.corridor_only, filters.train_number, filters.station_code]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    fetch_();
  }, [fetch_]);

  return { data, loading, error, refetch: fetch_ };
}
