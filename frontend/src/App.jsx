import React, { useState } from 'react';
import UploadPanel from './components/UploadPanel';
import SummaryPanel from './components/SummaryPanel';
import ClauseTable from './components/ClauseTable';
import ChatPanel from './components/ChatPanel';

function App() {
  const [docId, setDocId] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>AIDocs - Document & Contract Analyzer</h1>
      </header>
      
      {!docId ? (
        <UploadPanel onUploadSuccess={(id, data) => { setDocId(id); setAnalysis(data); }} />
      ) : (
        <div className="dashboard-grid">
          <div className="dashboard-left">
            <SummaryPanel summary={analysis?.summary} />
            <ClauseTable clauses={analysis?.clauses} />
          </div>
          <div className="dashboard-right">
            <ChatPanel docId={docId} />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
