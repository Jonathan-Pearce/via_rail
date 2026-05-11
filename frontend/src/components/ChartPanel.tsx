import { useState } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import type { PerformanceDataPoint } from '../api';

interface Props {
  data: PerformanceDataPoint[];
  loading: boolean;
}

const DIST_COLORS = ['#22c55e', '#f59e0b', '#f97316', '#ef4444'];

/** Build delay-distribution histogram data from the daily timeseries. */
function buildDistribution(data: PerformanceDataPoint[]) {
  if (data.length === 0) return [];

  // We derive the four buckets from the aggregated percentages
  // using weighted average across all data points.
  const totalStops = data.reduce((s, d) => s + d.total_stops, 0);
  if (totalStops === 0) return [];

  const late15Weighted = data.reduce((s, d) => s + d.late_15_pct * d.total_stops, 0) / totalStops;
  const late60Weighted = data.reduce((s, d) => s + d.late_60_pct * d.total_stops, 0) / totalStops;
  const onTimeWeighted = data.reduce((s, d) => s + d.on_time_pct * d.total_stops, 0) / totalStops;

  // med = late15 - late60 (15–60 min bucket)
  // slight = 100 - onTime - late15 (1–15 min bucket)
  const late60 = late60Weighted;
  const late15to60 = Math.max(0, late15Weighted - late60Weighted);
  const slight = Math.max(0, 100 - onTimeWeighted - late15Weighted);
  const onTime = onTimeWeighted;

  return [
    { bucket: 'On time (≤5 min)', pct: onTime },
    { bucket: '1–15 min late', pct: slight },
    { bucket: '15–60 min late', pct: late15to60 },
    { bucket: '60+ min late', pct: late60 },
  ];
}

/** Format date string to short display */
function fmtDate(d: string) {
  const dt = new Date(d + 'T00:00:00Z');
  return dt.toLocaleDateString('en-CA', { month: 'short', day: 'numeric', timeZone: 'UTC' });
}

export function ChartPanel({ data, loading }: Props) {
  const [barGroupBy, setBarGroupBy] = useState<'day' | 'train'>('day');

  const distribution = buildDistribution(data);

  if (loading) {
    return <div className="chart-loading">Loading charts…</div>;
  }

  if (data.length === 0) {
    return <div className="chart-empty">No data available for the selected filters.</div>;
  }

  const trendData = data.map((d) => ({ ...d, date: fmtDate(d.date) }));

  return (
    <div className="chart-panel">
      {/* On-time % trend */}
      <section className="chart-section">
        <h3 className="chart-title">On-Time % Trend</h3>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={trendData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#94a3b8' }} />
            <YAxis
              domain={[0, 100]}
              tickFormatter={(v: number) => `${v}%`}
              tick={{ fontSize: 11, fill: '#94a3b8' }}
            />
            <Tooltip
              formatter={(v) => [`${(v as number).toFixed(1)}%`, 'On-time']}
              contentStyle={{ background: '#1e293b', border: '1px solid #334155' }}
              labelStyle={{ color: '#e2e8f0' }}
            />
            <Legend wrapperStyle={{ color: '#94a3b8' }} />
            <Line
              type="monotone"
              dataKey="on_time_pct"
              name="On-time %"
              stroke="#22c55e"
              dot={false}
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </section>

      {/* Average delay bar chart */}
      <section className="chart-section">
        <div className="chart-title-row">
          <h3 className="chart-title">Average Delay (min)</h3>
          <div className="toggle-group">
            <button
              className={`toggle-btn${barGroupBy === 'day' ? ' active' : ''}`}
              onClick={() => setBarGroupBy('day')}
            >
              By day
            </button>
            <button
              className={`toggle-btn${barGroupBy === 'train' ? ' active' : ''}`}
              onClick={() => setBarGroupBy('train')}
            >
              By train
            </button>
          </div>
        </div>
        {barGroupBy === 'day' ? (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={trendData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#94a3b8' }} />
              <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
              <Tooltip
                formatter={(v) => [`${(v as number).toFixed(1)} min`, 'Avg delay']}
                contentStyle={{ background: '#1e293b', border: '1px solid #334155' }}
                labelStyle={{ color: '#e2e8f0' }}
              />
              <Legend wrapperStyle={{ color: '#94a3b8' }} />
              <Bar dataKey="avg_delay_minutes" name="Avg delay" fill="#3b82f6" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="chart-note">
            Per-train breakdown requires selecting a specific station or enabling a filter.
            Switch to <strong>By day</strong> to see the daily trend.
          </p>
        )}
      </section>

      {/* Delay distribution histogram */}
      <section className="chart-section">
        <h3 className="chart-title">Delay Distribution</h3>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={distribution} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="bucket" tick={{ fontSize: 11, fill: '#94a3b8' }} />
            <YAxis
              tickFormatter={(v: number) => `${v.toFixed(0)}%`}
              tick={{ fontSize: 11, fill: '#94a3b8' }}
            />
            <Tooltip
              formatter={(v) => [`${(v as number).toFixed(1)}%`, 'Share']}
              contentStyle={{ background: '#1e293b', border: '1px solid #334155' }}
              labelStyle={{ color: '#e2e8f0' }}
            />
            <Bar dataKey="pct" name="Share" radius={[3, 3, 0, 0]}>
              {distribution.map((_, i) => (
                <Cell key={i} fill={DIST_COLORS[i % DIST_COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </section>
    </div>
  );
}
