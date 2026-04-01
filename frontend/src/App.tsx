import { useState } from 'react'
import { PerformancePage } from './pages/PerformancePage'
import { MapPage } from './pages/MapPage'
import './index.css'

type Tab = 'performance' | 'map'

function App() {
  const [tab, setTab] = useState<Tab>('performance')

  return (
    <div className="app">
      <header className="app-header">
        <span className="app-logo">🚆 Via Rail Performance</span>
        <nav className="tab-nav">
          <button
            className={`tab-btn${tab === 'performance' ? ' active' : ''}`}
            onClick={() => setTab('performance')}
          >
            Performance
          </button>
          <button
            className={`tab-btn${tab === 'map' ? ' active' : ''}`}
            onClick={() => setTab('map')}
          >
            Live Map
          </button>
        </nav>
      </header>
      <div className="tab-content">
        {tab === 'performance' ? <PerformancePage /> : <MapPage />}
      </div>
    </div>
  )
}

export default App
