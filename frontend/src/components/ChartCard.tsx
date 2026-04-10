import React from 'react';
import './ChartCard.css';

interface ChartCardProps {
  title: string;
  subtitle?: string;
  loading?: boolean;
  error?: Error | null;
  empty?: boolean;
  onRetry?: () => void;
  children: React.ReactNode;
}

const ErrorIcon: React.FC = () => (
  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <circle cx="12" cy="12" r="10" stroke="var(--via-yellow)" strokeWidth="2" />
    <path d="M12 8v5M12 15.5v.5" stroke="var(--via-yellow-dark)" strokeWidth="2.2" strokeLinecap="round" />
  </svg>
);

const EmptyIcon: React.FC = () => (
  <svg width="56" height="56" viewBox="0 0 56 56" fill="none" aria-hidden="true">
    <rect x="8" y="18" width="40" height="26" rx="4" fill="var(--via-gray-200)" />
    <rect x="14" y="10" width="28" height="8" rx="2" fill="var(--via-gray-300)" />
    <path d="M20 32l4 4 12-12" stroke="var(--via-gray-400)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const ChartCard: React.FC<ChartCardProps> = ({
  title,
  subtitle,
  loading,
  error,
  empty,
  onRetry,
  children,
}) => (
  <div className={`chart-card${loading ? ' chart-card--loading' : ''}`}>
    <div className="chart-card__header">
      <div>
        <h3 className="chart-card__title">{title}</h3>
        {subtitle && <p className="chart-card__subtitle">{subtitle}</p>}
      </div>
    </div>

    <div className="chart-card__body">
      {loading && (
        <div className="chart-card__skeleton" aria-busy="true" aria-label="Loading chart…">
          {[80, 60, 90, 50, 70, 85, 45].map((h, i) => (
            <div
              key={i}
              className="chart-card__skeleton-bar"
              style={{ height: `${h}%`, animationDelay: `${i * 0.08}s` }}
            />
          ))}
        </div>
      )}

      {!loading && error && (
        <div className="chart-card__state chart-card__state--error" role="alert">
          <ErrorIcon />
          <p className="chart-card__state-message">
            Failed to load data: {error.message}
          </p>
          {onRetry && (
            <button className="chart-card__retry-btn" onClick={onRetry}>
              Try again
            </button>
          )}
        </div>
      )}

      {!loading && !error && empty && (
        <div className="chart-card__state chart-card__state--empty">
          <EmptyIcon />
          <p className="chart-card__state-message">
            No data for the selected filters.
          </p>
          <p className="chart-card__state-hint">
            Try widening your time range or removing filters.
          </p>
        </div>
      )}

      {!loading && !error && !empty && children}
    </div>
  </div>
);

export default ChartCard;
