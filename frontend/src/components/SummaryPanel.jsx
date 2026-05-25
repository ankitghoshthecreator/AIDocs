import React from 'react';

function SummaryPanel({ summary }) {
  return (
    <div className="summary-panel">
      <h2>Document Summary</h2>
      <p>Key details extracted from the document will be displayed here.</p>
      {/* TODO: Add structured cards for Parties, Dates, Obligations */}
    </div>
  );
}

export default SummaryPanel;
