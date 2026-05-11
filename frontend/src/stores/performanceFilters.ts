import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { PerformanceFilters, Period } from '@/api/types'

const VALID_PERIODS: Period[] = ['7d', '30d', '365d']

function parsePeriod(v: unknown): Period {
  return VALID_PERIODS.includes(v as Period) ? (v as Period) : '30d'
}

function parseNullableString(v: unknown): string | null {
  return typeof v === 'string' && v.trim() !== '' ? v.trim() : null
}

/**
 * Manages applied filter state and URL synchronisation.
 *
 * "Staged" filters are what the user has picked but not yet applied.
 * "Applied" filters are what charts/cards actually query against.
 *
 * On first mount we hydrate from URL query params so links are shareable.
 * Applied changes are reflected back into the URL.
 */
export const usePerformanceFilters = defineStore('performanceFilters', () => {
  const route  = useRoute()
  const router = useRouter()

  // ── Applied state (drives queries) ───────────────────────────────────
  const period      = ref<Period>('30d')
  const corridorOnly = ref(false)
  const trainNumber  = ref<string | null>(null)
  const stationCode  = ref<string | null>(null)
  const origin       = ref<string | null>(null)
  const destination  = ref<string | null>(null)

  // ── Staged state (sidebar pending changes) ────────────────────────────
  const staged = ref<PerformanceFilters>({
    period:      '30d',
    corridorOnly: false,
    trainNumber:  null,
    stationCode:  null,
    origin:       null,
    destination:  null,
  })

  // ── Derived applied bag ───────────────────────────────────────────────
  const applied = computed<PerformanceFilters>(() => ({
    period:      period.value,
    corridorOnly: corridorOnly.value,
    trainNumber:  trainNumber.value,
    stationCode:  stationCode.value,
    origin:       origin.value,
    destination:  destination.value,
  }))

  const isDirty = computed(() => {
    const a = applied.value
    const s = staged.value
    return (
      a.period       !== s.period       ||
      a.corridorOnly !== s.corridorOnly ||
      a.trainNumber  !== s.trainNumber  ||
      a.stationCode  !== s.stationCode  ||
      a.origin       !== s.origin       ||
      a.destination  !== s.destination
    )
  })

  // ── Hydrate from URL ──────────────────────────────────────────────────
  function hydrateFromQuery() {
    const q = route.query
    const p = parsePeriod(q.period)
    const co = q.corridor === 'true'
    const tn = parseNullableString(q.train)
    const sc = parseNullableString(q.station)
    const or = parseNullableString(q.origin)
    const de = parseNullableString(q.destination)

    period.value       = p
    corridorOnly.value = co
    trainNumber.value  = tn
    stationCode.value  = sc
    origin.value       = or
    destination.value  = de

    staged.value = { period: p, corridorOnly: co, trainNumber: tn, stationCode: sc, origin: or, destination: de }
  }

  hydrateFromQuery()

  // ── Push applied state to URL ─────────────────────────────────────────
  function pushToUrl() {
    const query: Record<string, string> = {
      period: period.value,
    }
    if (corridorOnly.value)     query.corridor    = 'true'
    if (trainNumber.value)      query.train       = trainNumber.value
    if (stationCode.value)      query.station     = stationCode.value
    if (origin.value)           query.origin      = origin.value
    if (destination.value)      query.destination = destination.value

    router.replace({ query })
  }

  // ── Actions ───────────────────────────────────────────────────────────
  function applyFilters() {
    period.value        = staged.value.period
    corridorOnly.value  = staged.value.corridorOnly
    trainNumber.value   = staged.value.trainNumber
    stationCode.value   = staged.value.stationCode
    origin.value        = staged.value.origin
    destination.value   = staged.value.destination
    pushToUrl()
  }

  function resetFilters() {
    const defaults: PerformanceFilters = {
      period:      '30d',
      corridorOnly: false,
      trainNumber:  null,
      stationCode:  null,
      origin:       null,
      destination:  null,
    }
    staged.value = { ...defaults }
    period.value        = defaults.period
    corridorOnly.value  = defaults.corridorOnly
    trainNumber.value   = defaults.trainNumber
    stationCode.value   = defaults.stationCode
    origin.value        = defaults.origin
    destination.value   = defaults.destination
    pushToUrl()
  }

  // Keep staged in sync with URL-driven changes (e.g. back/forward nav)
  watch(
    () => route.query,
    () => hydrateFromQuery(),
    { deep: true },
  )

  return {
    applied,
    staged,
    isDirty,
    applyFilters,
    resetFilters,
  }
})
