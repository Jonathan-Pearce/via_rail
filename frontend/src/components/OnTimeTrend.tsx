import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { PerformanceDay } from '../api/types';
import { formatShortDate } from '../utils/formatters';
import ChartCard from './ChartCard';

interface OnTimeTrendProps {
  data: PerformanceDay[];
  loading: boolean;
  error: Error | null;
  onRetry: () => void;
}

const CustomTooltip: React.FC<{
  active?: boolean;
  payload?: Array<{ value: number; name: string }>;
  label?: string;
}> = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip__date">{label}</div>
      {payload.map(p => (
        <div key={p.name} className="chart-tooltip__row">
          <span className="chart-tooltip__dot" style={{ background: 'var(--via-blue)' }} />
          <span className="chart-tooltip__label">On-time rate:</span>
          <span className="chart-tooltip__value">{p.value.toFixed(1)}%</span>
        </div>
      ))}
    </div>
  );
};

const OnTimeTrend: React.FC<OnTimeTrendProps> = ({ data, loading, error, onRetry }) => (
  <ChartCard
    title="On-Time Rate Trend"
    subtitle="Daily percentage of stops arriving within 5 minutes of schedule"
    loading={loading}
    error={error}
    onRetry={onRetry}
    empty={!loading && !error && data.length === 0}
  >
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data} margin={{ top: 8, right: 24, left: 0, bottom: 0 }}>
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
          domain={[0, 100]}
          tickFormatter={v => `${v}%`}
          tick={{ fontSize: 11, fill: 'var(--via-gray-500)' }}
          axisLine={false}
          tickLine={false}
          width={42}
        />
        <Tooltip content={<CustomTooltip />} />
        <ReferenceLine y={80} stroke="var(--via-success)" strokeDasharray="4 4" strokeOpacity={0.6} />
        <Line
          type="monotone"
          dataKey="on_time_pct"
          name="on_time_pct"
          stroke="var(--via-blue)"
          strokeWidth={2.5}
          dot={data.length < 30 ? { r: 4, fill: 'var(--via-blue)', strokeWidth: 0 } : false}
          activeDot={{ r: 6, fill: 'var(--via-blue)', strokeWidth: 2, stroke: 'white' }}
          isAnimationActive
          animationDuration={600}
        />
      </LineChart>
    </ResponsiveContainer>
    <div className="chart-legend">
      <span className="chart-legend__item">
        <span className="chart-legend__swatch" style={{ background: 'var(--via-blue)' }} />
        On-time rate
      </span>
      <span className="chart-legend__item">
        <span
          className="chart-legend__swatch"
          style={{ background: 'transparent', border: '2px dashed var(--via-success)' }}
        />
        80% target
      </span>
    </div>
  </ChartCard>
);

export default OnTimeTrend;
