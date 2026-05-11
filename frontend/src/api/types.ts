// ---- API response types ----

export interface PerformanceDay {
  date: string;
  on_time_pct: number;
  avg_delay_minutes: number;
  late_15_pct: number;
  late_60_pct: number;
  total_stops: number;
}

export interface Summary {
  period: string;
  total_stops: number;
  on_time_pct: number | null;
  late_15_pct: number | null;
  late_60_pct: number | null;
  avg_delay_minutes: number | null;
}

export interface Station {
  station_code: string;
  station_name: string;
  is_corridor: boolean;
  avg_delay_minutes: number;
  on_time_pct: number;
  total_stops: number;
}

// ---- Filter state ----

export interface FilterState {
  period: '7d' | '30d' | '365d';
  corridorOnly: boolean;
  trainNumber: string;
  stationCode: string;
}
