import React from 'react';
import './MapPage.css';

const MapPage: React.FC = () => (
  <main className="map-page">
    <div className="map-page__inner animate-fade-in">
      <svg width="64" height="64" viewBox="0 0 64 64" fill="none" aria-hidden="true">
        <circle cx="32" cy="28" r="14" stroke="var(--via-blue)" strokeWidth="3" />
        <circle cx="32" cy="28" r="5" fill="var(--via-blue)" />
        <path d="M32 42v10M20 54h24" stroke="var(--via-blue)" strokeWidth="3" strokeLinecap="round" />
      </svg>
      <h2 className="map-page__title">Live Train Map</h2>
      <p className="map-page__desc">
        Real-time Via Rail train positions will appear here.
        <br />
        Check back soon — the map feature is coming in a future update.
      </p>
    </div>
  </main>
);

export default MapPage;
