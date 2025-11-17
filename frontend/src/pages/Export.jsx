// -----------------------------------------------------------------------------
// File: Export.jsx
// Description: Export page component for ReqEngine - handles exporting use cases
//              to various formats including DOCX, Markdown, and PDF.
// Author: Pradyumna Chacham
// Date: November 2025
// Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
// License: MIT License - see LICENSE file in the root directory.
// -----------------------------------------------------------------------------

import React, { useState } from 'react';
import { api } from '../api/client';
import { toast } from 'react-toastify';
import useSessionStore from '../store/useSessionStore';
import { downloadFile } from '../utils/formatters';
import SessionHeader from '../components/layout/SessionHeader';

function Export() {
  const { currentSessionId } = useSessionStore();
  const [format, setFormat] = useState('docx');
  const [exporting, setExporting] = useState(false);

  const handleExport = async () => {
    if (!currentSessionId) {
      toast.error('Please select a session first');
      return;
    }

    setExporting(true);

    try {
      if (format === 'docx') {
        const response = await api.exportDOCX(currentSessionId);
        downloadFile(response.data, `use_cases_${currentSessionId}.docx`);
        toast.success('DOCX exported successfully!');
      } else if (format === 'markdown') {
        const response = await api.exportMarkdown(currentSessionId);
        downloadFile(response.data, `use_cases_${currentSessionId}.md`);
        toast.success('Markdown exported successfully!');
      } 
    } catch (error) {
      console.error('Export error:', error);
      toast.error('Export failed');
    } finally {
      setExporting(false);
    }
  };

  // If no session is selected
  if (!currentSessionId) {
    return (
      <div className="flex flex-col h-full">
        <div className="flex-1 p-8">
          <div className="max-w-4xl mx-auto">
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
              <p className="text-yellow-800">
                Please select a session from the sidebar or create a new chat to export
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Main export UI with session header
  return (
    <div className="flex flex-col h-full">
      {/* Session Header */}
      <SessionHeader />

      {/* Content */}
      <div className="flex-1 p-8 overflow-y-auto">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold text-gray-900 mb-8">Export 📥</h1>

          <div className="bg-white rounded-lg shadow-sm border p-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">
              Export Options
            </h2>

            {/* Format Selection */}
            <div className="space-y-4 mb-8">
              {/* DOCX */}
              <label className="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50 transition">
                <input
                  type="radio"
                  name="format"
                  value="docx"
                  checked={format === 'docx'}
                  onChange={(e) => setFormat(e.target.value)}
                  className="mr-4"
                  data-testid="docx-radio"
                />
                <div>
                  <p className="font-semibold text-gray-900">Microsoft Word (DOCX)</p>
                  <p className="text-sm text-gray-600">
                    Professional document with formatted sections
                  </p>
                </div>
              </label>

              {/* Markdown */}
              <label className="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50 transition">
                <input
                  type="radio"
                  name="format"
                  value="markdown"
                  checked={format === 'markdown'}
                  onChange={(e) => setFormat(e.target.value)}
                  className="mr-4"
                  data-testid="markdown-radio"
                />
                <div>
                  <p className="font-semibold text-gray-900">Markdown (MD)</p>
                  <p className="text-sm text-gray-600">
                    Plain text format, great for GitHub/documentation
                  </p>
                </div>
              </label>

            
            </div>

            {/* Export Button */}
            <button
              onClick={handleExport}
              disabled={exporting}
              className="w-full bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {exporting ? '⏳ Exporting...' : `📥 Export as ${format.toUpperCase()}`}
            </button>

            {/* Info */}
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>Note:</strong> The export will include all use cases from the current session.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Export;