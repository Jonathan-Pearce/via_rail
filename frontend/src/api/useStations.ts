import { useState, useEffect } from 'react';
import type { StationItem } from './types';

export function useStations(corridorOnly: boolean = false) {
  const [data, setData] = useState<StationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    const params = corridorOnly ? '?corridor_only=true' : '';
    fetch(`/api/stations${params}`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json() as Promise<StationItem[]>;
      })
      .then(setData)
      .catch((e: unknown) => setError(String(e)))
      .finally(() => setLoading(false));
  }, [corridorOnly]);

  return { data, loading, error };
}
