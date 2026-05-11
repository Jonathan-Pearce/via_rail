import type { StationItem, PerformanceFilters } from '../api';

interface Props {
  filters: PerformanceFilters;
  onFiltersChange: (f: PerformanceFilters) => void;
  stations: StationItem[];
  /** Unique train numbers derived from station data or other source */
  trainNumbers: string[];
}

const PERIODS: { label: string; value: PerformanceFilters['period'] }[] = [
  { label: '7 days', value: '7d' },
  { label: '30 days', value: '30d' },
  { label: '1 year', value: '365d' },
];

export function Sidebar({ filters, onFiltersChange, stations, trainNumbers }: Props) {
  function set<K extends keyof PerformanceFilters>(key: K, value: PerformanceFilters[K]) {
    onFiltersChange({ ...filters, [key]: value });
  }

  return (
    <aside className="sidebar">
      <h2 className="sidebar-title">Filters</h2>

      {/* Period selector */}
      <fieldset className="filter-group">
        <legend>Period</legend>
        <div className="period-buttons">
          {PERIODS.map((p) => (
            <button
              key={p.value}
              className={`period-btn${filters.period === p.value ? ' active' : ''}`}
              onClick={() => set('period', p.value)}
            >
              {p.label}
            </button>
          ))}
        </div>
      </fieldset>

      {/* Corridor toggle */}
      <fieldset className="filter-group">
        <legend>Route</legend>
        <label className="toggle-label">
          <input
            type="checkbox"
            checked={!!filters.corridor_only}
            onChange={(e) => set('corridor_only', e.target.checked)}
          />
          <span>Corridor only</span>
        </label>
      </fieldset>

      {/* Train number */}
      <fieldset className="filter-group">
        <legend>Train number</legend>
        <select
          value={filters.train_number ?? ''}
          onChange={(e) => set('train_number', e.target.value || undefined)}
          className="filter-select"
        >
          <option value="">All trains</option>
          {trainNumbers.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
      </fieldset>

      {/* Station */}
      <fieldset className="filter-group">
        <legend>Station</legend>
        <select
          value={filters.station_code ?? ''}
          onChange={(e) => set('station_code', e.target.value || undefined)}
          className="filter-select"
        >
          <option value="">All stations</option>
          {stations.map((s) => (
            <option key={s.station_code} value={s.station_code}>
              {s.station_name}
            </option>
          ))}
        </select>
      </fieldset>
    </aside>
  );
}
