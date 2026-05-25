import React from 'react';

function ClauseTable({ clauses }) {
  return (
    <div className="clause-table">
      <h2>Clause Matrix & Risk Assessment</h2>
      <p>A matrix of identified clauses with associated risk classifications and quotes.</p>
      {/* TODO: Add risk badge classification table */}
    </div>
  );
}

export default ClauseTable;
