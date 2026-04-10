import { useCallback, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import type { FilterState } from '../api/types';

const PERIODS = ['7d', '30d', '365d'] as const;

const DEFAULT_FILTERS: FilterState = {
  period: '30d',
  corridorOnly: false,
  trainNumber: '',
  stationCode: '',
};

function isValidPeriod(v: string): v is FilterState['period'] {
  return (PERIODS as readonly string[]).includes(v);
}

export function useFilterState() {
  const [searchParams, setSearchParams] = useSearchParams();

  const filters: FilterState = useMemo(() => {
    const period = searchParams.get('period') ?? DEFAULT_FILTERS.period;
    return {
      period: isValidPeriod(period) ? period : DEFAULT_FILTERS.period,
      corridorOnly: searchParams.get('corridor') === 'true',
      trainNumber: searchParams.get('train') ?? '',
      stationCode: searchParams.get('station') ?? '',
    };
  }, [searchParams]);

  const setFilters = useCallback(
    (newFilters: FilterState) => {
      const params = new URLSearchParams();
      params.set('period', newFilters.period);
      if (newFilters.corridorOnly) params.set('corridor', 'true');
      if (newFilters.trainNumber) params.set('train', newFilters.trainNumber);
      if (newFilters.stationCode) params.set('station', newFilters.stationCode);
      setSearchParams(params, { replace: true });
    },
    [setSearchParams],
  );

  const resetFilters = useCallback(() => {
    setSearchParams(new URLSearchParams(), { replace: true });
  }, [setSearchParams]);

  return { filters, setFilters, resetFilters };
}
