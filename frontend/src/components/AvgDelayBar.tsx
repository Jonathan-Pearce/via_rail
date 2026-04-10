import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import type { PerformanceDay } from '../api/types';
import { formatShortDate } from '../utils/formatters';
import ChartCard from './ChartCard';

interface AvgDelayBarProps {
  data: PerformanceDay[];
  loading: boolean;
  error: Error | null;
  onRetry: () => void;
}

const CustomTooltip: React.FC<{
  active?: boolean;
  payload?: Array<{ value: number }>;
  label?: string;
}> = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip__date">{label}</div>
      <div className="chart-tooltip__row">
        <span className="chart-tooltip__dot" style={{ background: 'var(--via-yellow)' }} />
        <span className="chart-tooltip__label">Avg delay:</span>
        <span className="chart-tooltip__value">{payload[0].value.toFixed(1)} min</span>
      </div>
    </div>
  );
};

const AvgDelayBar: React.FC<AvgDelayBarProps> = ({ data, loading, error, onRetry }) => {
  const getBarColor = (val: number) => {
    if (val <= 5) return 'var(--via-success)';
    if (val <= 15) return 'var(--via-yellow)';
    if (val <= 60) return 'var(--via-warning)';
    return 'var(--via-danger)';
  };

  return (
    <ChartCard
      title="Average Delay"
      subtitle="Mean delay in minutes per day (green ≤ 5 min, yellow 6–15 min, orange 16–60 min, red > 60 min)"
      loading={loading}
      error={error}
      onRetry={onRetry}
      empty={!loading && !error && data.length === 0}
    >
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} margin={{ top: 8, right: 24, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--via-gray-200)" vertical={false} />
          <XAxis
            dataKey="date"
            tickFormatter={formatShortDate}
            tick={{ fontSize: 11, fill: 'var(--via-gray-500)' }}
            axisLine={false}
            tickLine={false}
            minTickGap={40}
          />
          <YAxis
            tickFormatter={v => `${v}m`}
            tick={{ fontSize: 11, fill: 'var(--via-gray-500)' }}
            axisLine={false}
            tickLine={false}
            width={36}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(0,0,0,0.04)' }} />
          <Bar dataKey="avg_delay_minutes" radius={[3, 3, 0, 0]} isAnimationActive animationDuration={600}>
            {data.map((entry, i) => (
              <Cell key={i} fill={getBarColor(entry.avg_delay_minutes)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
};

export default AvgDelayBar;
