import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AppHeader from './components/AppHeader';
import Sidebar from './components/Sidebar';
import PerformancePage from './pages/PerformancePage';
import MapPage from './pages/MapPage';
import { useFilterState } from './utils/useFilterState';
import { useStations } from './api/hooks';
import type { FilterState } from './api/types';
import './App.css';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 2, refetchOnWindowFocus: false } },
});

// Inner component so hooks can access Router context
const AppInner: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { filters, setFilters, resetFilters } = useFilterState();
  const [draft, setDraft] = useState<FilterState>(filters);

  const stationsQuery = useStations();

  const handleMenuToggle = () => setSidebarOpen(o => !o);
  const handleSidebarClose = () => setSidebarOpen(false);

  const handleDraftChange = (patch: Partial<FilterState>) => {
    setDraft(prev => ({ ...prev, ...patch }));
  };

  const handleApply = () => {
    setFilters(draft);
    setSidebarOpen(false);
  };

  const handleReset = () => {
    const def: FilterState = { period: '30d', corridorOnly: false, trainNumber: '', stationCode: '' };
    setDraft(def);
    resetFilters();
    setSidebarOpen(false);
  };

  return (
    <div className="app">
      <AppHeader onMenuToggle={handleMenuToggle} sidebarOpen={sidebarOpen} />
      <div className="app__body">
        <Sidebar
          open={sidebarOpen}
          onClose={handleSidebarClose}
          filters={filters}
          draft={draft}
          onDraftChange={handleDraftChange}
          onApply={handleApply}
          onReset={handleReset}
          stations={stationsQuery.data ?? []}
          stationsLoading={stationsQuery.isLoading}
        />
        <Routes>
          <Route path="/" element={<PerformancePage sidebarOpen={sidebarOpen} />} />
          <Route path="/map" element={<MapPage />} />
        </Routes>
      </div>
    </div>
  );
};

const App: React.FC = () => (
  <QueryClientProvider client={queryClient}>
    <BrowserRouter>
      <AppInner />
    </BrowserRouter>
  </QueryClientProvider>
);

export default App;
