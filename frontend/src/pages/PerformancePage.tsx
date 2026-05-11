import { useState } from 'react';
import { Sidebar } from '../components/Sidebar';
import { StatCard } from '../components/StatCard';
import { ChartPanel } from '../components/ChartPanel';
import { usePerformance, useSummary, useStations } from '../api';
import type { PerformanceFilters } from '../api';

const DEFAULT_FILTERS: PerformanceFilters = {
  period: '30d',
  corridor_only: false,
};

/** Derive a sorted list of unique train numbers from station names (placeholder).
 *  A dedicated /api/trains endpoint would be better; for now we hard-code common
 *  corridor train numbers. */
const CORRIDOR_TRAINS = [
  '1', '2', '21', '22', '30', '31', '32', '33', '35', '36',
  '40', '41', '42', '43', '44', '45', '46', '48', '50', '51',
  '52', '53', '54', '55', '56', '57', '58', '60', '62', '63',
  '64', '65', '66', '67', '68', '69',
];

export function PerformancePage() {
  const [filters, setFilters] = useState<PerformanceFilters>(DEFAULT_FILTERS);

  const { data: perfData, loading: perfLoading } = usePerformance(filters);
  const { data: summaryData, loading: summaryLoading } = useSummary(filters);
  const { data: stations } = useStations(filters.corridor_only);

  return (
    <div className="performance-page">
      <Sidebar
        filters={filters}
        onFiltersChange={setFilters}
        stations={stations}
        trainNumbers={CORRIDOR_TRAINS}
      />
      <main className="main-content">
        <StatCard data={summaryData} loading={summaryLoading} />
        <ChartPanel
          data={perfData?.data ?? []}
          loading={perfLoading}
        />
      </main>
    </div>
  );
}
