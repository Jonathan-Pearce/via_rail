/* ─────────────────────────────────────────────────────────────────────────
   API domain types — mirror the FastAPI response schemas exactly
   ───────────────────────────────────────────────────────────────────────── */

/** Rolling period option accepted by /api/performance and /api/summary */
export type Period = '7d' | '30d' | '365d'

/** Query filters shared across performance endpoints */
export interface PerformanceFilters {
  period: Period
  corridorOnly: boolean
  trainNumber: string | null
  stationCode: string | null
  origin: string | null
  destination: string | null
}

/** One day's aggregate from GET /api/performance */
export interface DailyPerformance {
  date: string          // 'YYYY-MM-DD' EST calendar date
  on_time_pct: number   // 0–100
  avg_delay_minutes: number
  late_15_pct: number   // 0–100
  late_60_pct: number   // 0–100
  total_stops: number
}

/** Aggregate summary from GET /api/summary */
export interface SummaryStats {
  period: Period
  total_stops: number
  on_time_pct:          number | null
  late_15_pct:          number | null
  late_60_pct:          number | null
  avg_delay_minutes:    number | null
}

/** One station record from GET /api/stations */
export interface StationRecord {
  station_code:      string
  station_name:      string
  is_corridor:       boolean
  avg_delay_minutes: number
  on_time_pct:       number
  total_stops:       number
}
