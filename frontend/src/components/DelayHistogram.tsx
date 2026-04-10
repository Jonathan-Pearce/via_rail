import React, { useMemo } from 'react';
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
import ChartCard from './ChartCard';

interface DelayHistogramProps {
  data: PerformanceDay[];
  loading: boolean;
  error: Error | null;
  onRetry: () => void;
}

interface Bin {
  label: string;
  count: number;
  color: string;
}

const BINS: Array<{ label: string; min: number; max: number; color: string }> = [
  { label: 'On-time\n(≤5 min)',  min: -Infinity, max: 5,   color: 'var(--via-success)' },
  { label: '6–15 min',           min: 5,          max: 15,  color: 'var(--via-yellow)' },
  { label: '16–30 min',          min: 15,         max: 30,  color: 'var(--via-warning)' },
  { label: '31–60 min',          min: 30,         max: 60,  color: '#E67E22' },
  { label: '60+ min',            min: 60,         max: Infinity, color: 'var(--via-danger)' },
];

const CustomTooltip: React.FC<{
  active?: boolean;
  payload?: Array<{ value: number; payload: Bin }>;
  label?: string;
}> = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const bin = payload[0].payload;
  const total = payload[0].value;
  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip__date">{bin.label.replace('\n', ' ')}</div>
      <div className="chart-tooltip__row">
        <span className="chart-tooltip__dot" style={{ background: bin.color }} />
        <span className="chart-tooltip__label">Days:</span>
        <span className="chart-tooltip__value">{total}</span>
      </div>
    </div>
  );
};

const DelayHistogram: React.FC<DelayHistogramProps> = ({ data, loading, error, onRetry }) => {
  const bins: Bin[] = useMemo(() => {
    const counts = BINS.map(b => ({ ...b, count: 0 }));
    for (const row of data) {
      const delay = row.avg_delay_minutes;
      for (const bin of counts) {
        if (delay > bin.min && delay <= bin.max) {
          bin.count++;
          break;
        }
      }
    }
    return counts.map(({ label, count, color }) => ({ label, count, color }));
  }, [data]);

  return (
    <ChartCard
      title="Delay Distribution"
      subtitle="How many days fell into each average delay bucket"
      loading={loading}
      error={error}
      onRetry={onRetry}
      empty={!loading && !error && data.length === 0}
    >
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={bins} margin={{ top: 8, right: 24, left: 0, bottom: 16 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--via-gray-200)" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 10, fill: 'var(--via-gray-500)' }}
            axisLine={false}
            tickLine={false}
            interval={0}
          />
          <YAxis
            tick={{ fontSize: 11, fill: 'var(--via-gray-500)' }}
            axisLine={false}
            tickLine={false}
            width={28}
            allowDecimals={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(0,0,0,0.04)' }} />
          <Bar dataKey="count" radius={[4, 4, 0, 0]} isAnimationActive animationDuration={600}>
            {bins.map((bin, i) => (
              <Cell key={i} fill={bin.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
};

export default DelayHistogram;
