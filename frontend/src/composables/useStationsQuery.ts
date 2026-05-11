import { useQuery } from '@tanstack/vue-query'
import { computed, type MaybeRefOrGetter, toValue } from 'vue'
import { fetchStations } from '@/api/stations'

export function useStationsQuery(corridorOnly: MaybeRefOrGetter<boolean> = false) {
  const key = computed(() => ['stations', toValue(corridorOnly)])

  return useQuery({
    queryKey: key,
    queryFn: () => fetchStations(toValue(corridorOnly)),
    staleTime: 5 * 60_000, // stations change rarely — cache 5 min
  })
}
