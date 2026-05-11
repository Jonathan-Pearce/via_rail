import { apiFetch } from './client'
import type {
  PerformanceFilters,
  DailyPerformance,
  SummaryStats,
} from './types'

function filtersToParams(f: PerformanceFilters) {
  return {
    period: f.period,
    corridor_only: f.corridorOnly ? 'true' : undefined,
    train_number:  f.trainNumber  ?? undefined,
    station_code:  f.stationCode  ?? undefined,
    origin:        f.origin       ?? undefined,
    destination:   f.destination  ?? undefined,
  }
}

export function fetchPerformance(
  filters: PerformanceFilters,
): Promise<DailyPerformance[]> {
  return apiFetch<DailyPerformance[]>('/api/performance', filtersToParams(filters))
}

export function fetchSummary(
  filters: PerformanceFilters,
): Promise<SummaryStats> {
  return apiFetch<SummaryStats>('/api/summary', filtersToParams(filters))
}
