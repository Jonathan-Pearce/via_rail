import { useQuery } from '@tanstack/vue-query'
import { computed, type MaybeRefOrGetter, toValue } from 'vue'
import { fetchPerformance, fetchSummary } from '@/api/performance'
import type { PerformanceFilters } from '@/api/types'

function filtersKey(f: PerformanceFilters) {
  return [
    'performance',
    f.period,
    f.corridorOnly,
    f.trainNumber,
    f.stationCode,
    f.origin,
    f.destination,
  ] as const
}

export function usePerformanceQuery(
  filters: MaybeRefOrGetter<PerformanceFilters>,
) {
  const key = computed(() => filtersKey(toValue(filters)))

  return useQuery({
    queryKey: key,
    queryFn: () => fetchPerformance(toValue(filters)),
  })
}

export function useSummaryQuery(
  filters: MaybeRefOrGetter<PerformanceFilters>,
) {
  const key = computed(() => ['summary', ...filtersKey(toValue(filters)).slice(1)])

  return useQuery({
    queryKey: key,
    queryFn: () => fetchSummary(toValue(filters)),
  })
}
