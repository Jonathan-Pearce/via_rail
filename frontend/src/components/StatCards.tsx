import React from 'react';
import type { Summary } from '../api/types';
import './StatCards.css';

interface StatCardsProps {
  summary: Summary | undefined;
  loading: boolean;
}

interface CardDef {
  key: keyof Summary;
  label: string;
  format: (val: number) => string;
  icon: React.ReactNode;
  colorClass: string;
  description: string;
}

const CheckIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <circle cx="12" cy="12" r="10" fill="currentColor" opacity="0.15" />
    <path d="M7 12l4 4 6-7" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const ClockIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <circle cx="12" cy="12" r="10" fill="currentColor" opacity="0.15" />
    <path d="M12 7v5l3 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const AlertIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path d="M12 3L2 20h20L12 3z" fill="currentColor" opacity="0.15" />
    <path d="M12 9v5M12 17v.5" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
  </svg>
);

const TrainDelayIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <rect x="4" y="4" width="12" height="10" rx="2" fill="currentColor" opacity="0.15" />
    <path d="M4 4h12a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z" stroke="currentColor" strokeWidth="1.8" />
    <path d="M2 14l-1 3h18l-1-3" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
    <circle cx="6" cy="18.5" r="1.2" fill="currentColor" />
    <circle cx="12" cy="18.5" r="1.2" fill="currentColor" />
  </svg>
);

const CARDS: CardDef[] = [
  {
    key: 'on_time_pct',
    label: 'On-Time Rate',
    format: v => `${v.toFixed(1)}%`,
    icon: <CheckIcon />,
    colorClass: 'stat-card--green',
    description: 'Stops arriving ≤ 5 min late',
  },
  {
    key: 'avg_delay_minutes',
    label: 'Avg. Delay',
    format: v => `${v.toFixed(1)} min`,
    icon: <ClockIcon />,
    colorClass: 'stat-card--blue',
    description: 'Mean delay across all stops',
  },
  {
    key: 'late_15_pct',
    label: 'Late 15+ min',
    format: v => `${v.toFixed(1)}%`,
    icon: <AlertIcon />,
    colorClass: 'stat-card--yellow',
    description: 'Stops arriving ≥ 15 min late',
  },
  {
    key: 'late_60_pct',
    label: 'Late 60+ min',
    format: v => `${v.toFixed(1)}%`,
    icon: <TrainDelayIcon />,
    colorClass: 'stat-card--red',
    description: 'Stops arriving ≥ 60 min late',
  },
];

const SkeletonCard: React.FC = () => (
  <div className="stat-card stat-card--skeleton" aria-busy="true" aria-label="Loading…">
    <div className="skeleton-line skeleton-line--short" />
    <div className="skeleton-line skeleton-line--long" />
    <div className="skeleton-line skeleton-line--medium" />
  </div>
);

const StatCards: React.FC<StatCardsProps> = ({ summary, loading }) => {
  if (loading) {
    return (
      <div className="stat-cards" aria-label="Loading statistics">
        {CARDS.map(c => <SkeletonCard key={c.key} />)}
      </div>
    );
  }

  return (
    <div className="stat-cards animate-fade-in">
      {CARDS.map(({ key, label, format, icon, colorClass, description }) => {
        const rawVal = summary?.[key];
        const val = typeof rawVal === 'number' ? rawVal : null;
        return (
          <div key={key} className={`stat-card ${colorClass}`}>
            <div className="stat-card__header">
              <span className="stat-card__icon">{icon}</span>
              <span className="stat-card__label">{label}</span>
            </div>
            <div className="stat-card__value">
              {val !== null ? format(val) : '—'}
            </div>
            <div className="stat-card__desc">{description}</div>
            {summary && (
              <div className="stat-card__total">
                {summary.total_stops.toLocaleString()} stops · {summary.period}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default StatCards;
