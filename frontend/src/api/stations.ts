import { apiFetch } from './client'
import type { StationRecord } from './types'

export function fetchStations(corridorOnly = false): Promise<StationRecord[]> {
  return apiFetch<StationRecord[]>('/api/stations', {
    corridor_only: corridorOnly ? 'true' : undefined,
  })
}
