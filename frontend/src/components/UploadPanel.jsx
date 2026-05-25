import React from 'react';

function UploadPanel({ onUploadSuccess }) {
  return (
    <div className="upload-panel">
      <h2>Upload Document</h2>
      <p>Drag and drop your PDF agreement here, or click to browse</p>
      {/* TODO: Add drag & drop and fetch/axios POST upload logic */}
    </div>
  );
}

export default UploadPanel;
