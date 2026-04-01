// Shared API types for Via Rail Performance Dashboard

export interface PerformanceFilters {
  period?: '7d' | '30d' | '365d';
  corridor_only?: boolean;
  train_number?: string;
  station_code?: string;
}

export interface PerformanceDataPoint {
  date: string;
  on_time_pct: number;
  avg_delay_minutes: number;
  late_15_pct: number;
  late_60_pct: number;
  total_stops: number;
}

export interface PerformanceResponse {
  data: PerformanceDataPoint[];
  filters: PerformanceFilters;
}

export interface SummaryResponse {
  period: string;
  on_time_pct: number | null;
  avg_delay_minutes: number | null;
  late_15_pct: number | null;
  late_60_pct: number | null;
  total_stops: number;
  corridor_only?: boolean;
}

export interface StationItem {
  station_code: string;
  station_name: string;
  is_corridor: boolean;
  avg_delay_minutes: number;
  on_time_pct: number;
  total_stops: number;
}
