import { useState } from 'react';
import './App.css';
import CaseDashboard from './CaseDashboard';
import CaseDetail from './CaseDetail';

import { ConfigurationView, GlobalAuditView } from './Views';

function App() {
  const [view, setView] = useState('dashboard');
  const [selectedCaseId, setSelectedCaseId] = useState(null);

  const navigateToCase = (id) => {
    setSelectedCaseId(id);
    setView('dashboard');
  };

  return (
    <div className="layout">
      <div className="sidebar">
        <h2>🛡️ Agentic KYC</h2>
        <a className={`menu-item ${view === 'dashboard' ? 'active' : ''}`} onClick={() => { setView('dashboard'); setSelectedCaseId(null); }}>
          Dashboard
        </a>
        <a className={`menu-item ${view === 'config' ? 'active' : ''}`} onClick={() => setView('config')}>
          Configuration
        </a>
        <a className={`menu-item ${view === 'audit' ? 'active' : ''}`} onClick={() => setView('audit')}>
          Audit Logs
        </a>
      </div>

      <div className="main-content">
        {view === 'config' && <ConfigurationView />}
        {view === 'audit' && <GlobalAuditView />}

        {view === 'dashboard' && (
          selectedCaseId ? (
            <CaseDetail
              caseId={selectedCaseId}
              onBack={() => setSelectedCaseId(null)}
            />
          ) : (
            <CaseDashboard onSelectCase={navigateToCase} />
          )
        )}
      </div>
    </div>
  );
}

export default App;
