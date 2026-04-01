import type { SummaryResponse } from '../api';

interface Props {
  data: SummaryResponse | null;
  loading: boolean;
}

interface CardDef {
  label: string;
  value: (d: SummaryResponse) => string;
  accent: string;
}

const CARDS: CardDef[] = [
  {
    label: 'On-Time %',
    value: (d) => d.on_time_pct != null ? `${d.on_time_pct.toFixed(1)}%` : '—',
    accent: '#22c55e',
  },
  {
    label: 'Avg Delay',
    value: (d) => d.avg_delay_minutes != null ? `${d.avg_delay_minutes.toFixed(1)} min` : '—',
    accent: '#3b82f6',
  },
  {
    label: 'Late 15+ min',
    value: (d) => d.late_15_pct != null ? `${d.late_15_pct.toFixed(1)}%` : '—',
    accent: '#f59e0b',
  },
  {
    label: 'Late 60+ min',
    value: (d) => d.late_60_pct != null ? `${d.late_60_pct.toFixed(1)}%` : '—',
    accent: '#ef4444',
  },
];

export function StatCard({ data, loading }: Props) {
  return (
    <div className="stat-cards">
      {CARDS.map((card) => (
        <div key={card.label} className="stat-card" style={{ borderTop: `4px solid ${card.accent}` }}>
          <div className="stat-label">{card.label}</div>
          <div className="stat-value">
            {loading || !data ? '—' : card.value(data)}
          </div>
          {!loading && data && (
            <div className="stat-sub">{data.total_stops.toLocaleString()} stops</div>
          )}
        </div>
      ))}
    </div>
  );
}
