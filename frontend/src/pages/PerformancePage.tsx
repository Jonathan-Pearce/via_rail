import React from 'react';
import { usePerformance, useSummary } from '../api/hooks';
import { useFilterState } from '../utils/useFilterState';
import StatCards from '../components/StatCards';
import OnTimeTrend from '../components/OnTimeTrend';
import AvgDelayBar from '../components/AvgDelayBar';
import DelayHistogram from '../components/DelayHistogram';
import './PerformancePage.css';

interface PerformancePageProps {
  sidebarOpen: boolean;
}

const PerformancePage: React.FC<PerformancePageProps> = ({ sidebarOpen }) => {
  const { filters } = useFilterState();

  const performanceQuery = usePerformance(filters);
  const summaryQuery = useSummary(filters);

  const perfData = performanceQuery.data ?? [];

  return (
    <div className={`perf-page${sidebarOpen ? ' perf-page--sidebar-open' : ''}`}>
      <main className="perf-page__main" id="main-content">
        <div className="perf-page__content">
          {/* Page heading */}
          <div className="perf-page__heading animate-fade-in">
            <h1 className="perf-page__title">Train Performance</h1>
            <p className="perf-page__period-badge">
              {filters.period === '7d' ? 'Last 7 days'
                : filters.period === '30d' ? 'Last 30 days'
                : 'Last 12 months'}
              {filters.corridorOnly && ' · Corridor'}
              {filters.trainNumber && ` · Train ${filters.trainNumber}`}
              {filters.stationCode && ` · ${filters.stationCode}`}
            </p>
          </div>

          {/* Stat Cards */}
          <StatCards
            summary={summaryQuery.data}
            loading={summaryQuery.isLoading}
          />

          {/* Charts grid */}
          <div className="charts-grid">
            <div className="charts-grid__full">
              <OnTimeTrend
                data={perfData}
                loading={performanceQuery.isLoading}
                error={performanceQuery.error}
                onRetry={() => performanceQuery.refetch()}
              />
            </div>
            <div className="charts-grid__half">
              <AvgDelayBar
                data={perfData}
                loading={performanceQuery.isLoading}
                error={performanceQuery.error}
                onRetry={() => performanceQuery.refetch()}
              />
            </div>
            <div className="charts-grid__half">
              <DelayHistogram
                data={perfData}
                loading={performanceQuery.isLoading}
                error={performanceQuery.error}
                onRetry={() => performanceQuery.refetch()}
              />
            </div>
          </div>

          <footer className="perf-page__footer">
            All dates shown in EST (Eastern Standard Time).
            Data sourced from the Via Rail live tracking API.
          </footer>
        </div>
      </main>
    </div>
  );
};

export default PerformancePage;
