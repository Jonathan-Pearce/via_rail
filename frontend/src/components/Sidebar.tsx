import React, { useCallback, useRef, useEffect } from 'react';
import type { FilterState } from '../api/types';
import type { Station } from '../api/types';
import './Sidebar.css';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
  filters: FilterState;
  draft: FilterState;
  onDraftChange: (patch: Partial<FilterState>) => void;
  onApply: () => void;
  onReset: () => void;
  stations: Station[];
  stationsLoading: boolean;
}

const PERIODS: Array<{ value: FilterState['period']; label: string }> = [
  { value: '7d', label: '7 days' },
  { value: '30d', label: '30 days' },
  { value: '365d', label: '1 year' },
];

const FilterIcon: React.FC = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path d="M4 6h16M7 12h10M10 18h4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
  </svg>
);

const ResetIcon: React.FC = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path d="M3 12a9 9 0 1 0 9-9 9 9 0 0 0-6.36 2.64L3 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    <path d="M3 3v6h6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const Sidebar: React.FC<SidebarProps> = ({
  open,
  onClose,
  draft,
  onDraftChange,
  onApply,
  onReset,
  stations,
  stationsLoading,
}) => {
  const overlayRef = useRef<HTMLDivElement>(null);

  // Close on overlay click
  const handleOverlayClick = useCallback(
    (e: React.MouseEvent) => {
      if (e.target === overlayRef.current) onClose();
    },
    [onClose],
  );

  // Close on Escape key
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && open) onClose();
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [open, onClose]);

  // Deduplicate train numbers from stations data — use a separate trains query if available,
  // but for now build unique list from station names for demo.
  const trainNumbers = React.useMemo(() => {
    // We don't have a /api/trains endpoint, so show a curated list of corridor trains
    return ['1', '2', '11', '12', '14', '15', '21', '22', '30', '31', '40', '41',
            '51', '52', '53', '54', '55', '56', '57', '58', '60', '61', '62', '63',
            '64', '65', '66', '67', '68', '69', '70', '71', '72', '73', '74', '75'].sort();
  }, []);

  const stationOptions = React.useMemo(
    () => [...stations].sort((a, b) => a.station_name.localeCompare(b.station_name)),
    [stations],
  );

  return (
    <>
      {/* Backdrop */}
      <div
        ref={overlayRef}
        className={`sidebar-overlay${open ? ' sidebar-overlay--visible' : ''}`}
        onClick={handleOverlayClick}
        aria-hidden="true"
      />

      {/* Panel */}
      <aside
        className={`sidebar${open ? ' sidebar--open' : ''}`}
        aria-label="Filters panel"
        aria-hidden={!open}
      >
        <div className="sidebar__header">
          <span className="sidebar__header-icon"><FilterIcon /></span>
          <h2 className="sidebar__title">Filters</h2>
          <button className="sidebar__close-btn" onClick={onClose} aria-label="Close filters">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </button>
        </div>

        <div className="sidebar__body">
          {/* Period Selector */}
          <div className="sidebar__section">
            <label className="sidebar__label">Time Period</label>
            <div className="period-selector" role="group" aria-label="Select time period">
              {PERIODS.map(({ value, label }) => (
                <button
                  key={value}
                  className={`period-selector__btn${draft.period === value ? ' period-selector__btn--active' : ''}`}
                  onClick={() => onDraftChange({ period: value })}
                  aria-pressed={draft.period === value}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Corridor Toggle */}
          <div className="sidebar__section">
            <label className="sidebar__label">Route Type</label>
            <label className="toggle" htmlFor="corridor-toggle">
              <input
                type="checkbox"
                id="corridor-toggle"
                className="toggle__input"
                checked={draft.corridorOnly}
                onChange={e => onDraftChange({ corridorOnly: e.target.checked })}
              />
              <span className="toggle__track" />
              <span className="toggle__label-text">
                Windsor–Québec Corridor only
              </span>
            </label>
          </div>

          {/* Train Selector */}
          <div className="sidebar__section">
            <label className="sidebar__label" htmlFor="train-select">Train Number</label>
            <div className="select-wrapper">
              <select
                id="train-select"
                className="sidebar__select"
                value={draft.trainNumber}
                onChange={e => onDraftChange({ trainNumber: e.target.value })}
              >
                <option value="">All trains</option>
                {trainNumbers.map(n => (
                  <option key={n} value={n}>Train {n}</option>
                ))}
              </select>
              <span className="select-wrapper__arrow" aria-hidden="true">▾</span>
            </div>
          </div>

          {/* Station Selector */}
          <div className="sidebar__section">
            <label className="sidebar__label" htmlFor="station-select">Station</label>
            <div className="select-wrapper">
              <select
                id="station-select"
                className="sidebar__select"
                value={draft.stationCode}
                onChange={e => onDraftChange({ stationCode: e.target.value })}
                disabled={stationsLoading}
              >
                <option value="">All stations</option>
                {stationOptions.map(s => (
                  <option key={s.station_code} value={s.station_code}>
                    {s.station_name} ({s.station_code})
                  </option>
                ))}
              </select>
              <span className="select-wrapper__arrow" aria-hidden="true">▾</span>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="sidebar__footer">
          <button className="sidebar__apply-btn" onClick={onApply}>
            Apply Filters
          </button>
          <button className="sidebar__reset-btn" onClick={onReset}>
            <ResetIcon /> Reset
          </button>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
