// -----------------------------------------------------------------------------
// File: Extraction.jsx
// Description: Use case extraction page for ReqEngine - handles document upload,
//              text input, and displays extracted use cases with refinement options.
// Author: Pradyumna Chacham
// Date: November 2025
// Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
// License: MIT License - see LICENSE file in the root directory.
// -----------------------------------------------------------------------------

import React, { useState } from 'react';
import { api } from '../api/client';
import { toast } from 'react-toastify';
import useSessionStore from '../store/useSessionStore';
import UseCaseCard from '../components/UseCaseCard';
import FileUploader from '../components/FileUploader';
import LoadingSpinner from '../components/LoadingSpinner';

function Extraction() {
  const {
    currentSessionId,
    setCurrentSession,
    projectContext,
    setProjectContext,
    domain,
    setDomain,
  } = useSessionStore();

  const [activeTab, setActiveTab] = useState('text'); // 'text' or 'file'
  const [rawText, setRawText] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState(null);

  // Normalize backend response to a consistent shape the UI can render
  const normalizeExtractionResponse = (data) => {
    const resultsArray = Array.isArray(data?.results)
      ? data.results
      : Array.isArray(data?.generated_use_cases)
      ? data.generated_use_cases
      : [];

    const normalizedResults = resultsArray.map((uc) => ({
      status: uc.status || 'stored',
      id: uc.id,
      title: uc.title || 'Untitled',
      preconditions: Array.isArray(uc.preconditions) ? uc.preconditions : [],
      // Support singular main_flow by wrapping it
      main_flows: Array.isArray(uc.main_flows)
        ? uc.main_flows
        : Array.isArray(uc.main_flow)
        ? [uc.main_flow]
        : [],
      // Keep original singular for other consumers, but UI uses main_flows above
      main_flow: Array.isArray(uc.main_flow) ? uc.main_flow : [],
      sub_flows: Array.isArray(uc.sub_flows) ? uc.sub_flows : [],
      alternate_flows: Array.isArray(uc.alternate_flows) ? uc.alternate_flows : [],
      outcomes: Array.isArray(uc.outcomes) ? uc.outcomes : [],
      stakeholders: Array.isArray(uc.stakeholders) ? uc.stakeholders : [],
    }));

    return {
      message: data?.message,
      session_id: data?.session_id,
      extracted_count: Number.isFinite(data?.extracted_count) ? data.extracted_count : normalizedResults.length,
      stored_count: data?.stored_count ?? 0,
      duplicate_count: data?.duplicate_count ?? 0,
      processing_time_seconds: data?.processing_time_seconds ?? undefined,
      validation_results: Array.isArray(data?.validation_results) ? data.validation_results : [],
      extraction_method: data?.extraction_method,
      results: normalizedResults,
    };
  };

  // Handle text extraction
  const handleTextExtraction = async () => {
    if (!rawText.trim()) {
      toast.error('Please enter some requirements text');
      return;
    }

    setLoading(true);

    try {
      const response = await api.extractFromText({
        raw_text: rawText,
        session_id: currentSessionId || undefined,
        project_context: projectContext,
        domain: domain,
      });

      const normalized = normalizeExtractionResponse(response.data);
      setResults(normalized);
      setCurrentSession(normalized.session_id);
      
      toast.success(
        `✅ Extracted ${response.data.extracted_count} use cases in ${response.data.processing_time_seconds}s!`
      );
    } catch (error) {
      console.error('Extraction error:', error);
      toast.error(error.response?.data?.detail || 'Extraction failed');
    } finally {
      setLoading(false);
    }
  };

  // Handle file upload
  const handleFileUpload = async (file) => {
    setUploading(true);

    const formData = new FormData();
    formData.append('file', file);
    if (currentSessionId) formData.append('session_id', currentSessionId);
    if (projectContext) formData.append('project_context', projectContext);
    if (domain) formData.append('domain', domain);

    try {
      const response = await api.extractFromDocument(formData);
      const normalized = normalizeExtractionResponse(response.data);
      setResults(normalized);
      setCurrentSession(normalized.session_id);
      
      toast.success(
        `✅ Extracted ${response.data.extracted_count} use cases from ${file.name}!`
      );
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(error.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          Extract Use Cases ✨
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* LEFT PANEL: INPUT */}
          <div>
            <div className="bg-white rounded-lg shadow-sm border p-6">
              {/* Session Info */}
              <div className="mb-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Session Information
                </h2>
                
                <div className="space-y-4">
                  <div>
                    <label 
                      htmlFor="projectContext" 
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Project Context
                    </label>
                    <input
                      id="projectContext"
                      type="text"
                      value={projectContext}
                      onChange={(e) => setProjectContext(e.target.value)}
                      placeholder="e.g., E-commerce Platform"
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label 
                      htmlFor="domain" 
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Domain
                    </label>
                    <input
                      id="domain"
                      type="text"
                      value={domain}
                      onChange={(e) => setDomain(e.target.value)}
                      placeholder="e.g., Online Retail"
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                    />
                  </div>

                  {currentSessionId && (
                    <div className="text-sm text-gray-500">
                      Session ID: <span className="font-mono">{currentSessionId.substring(0, 12)}...</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Tabs */}
              <div className="mb-4 border-b">
                <div className="flex gap-4">
                  <button
                  onClick={() => setActiveTab('text')}
                    className={`pb-2 px-1 font-medium transition ${
                      activeTab === 'text'
                        ? 'border-b-2 border-primary text-primary'
                        : 'text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    📝 Text Input
                  </button>
                  <button
                    onClick={() => setActiveTab('file')}
                    className={`pb-2 px-1 font-medium transition ${
                      activeTab === 'file'
                        ? 'border-b-2 border-primary text-primary'
                        : 'text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    📁 File Upload
                  </button>
                </div>
              </div>

              {/* Tab Content */}
              {activeTab === 'text' ? (
                <div>
                  <label 
                    htmlFor="requirementsText" 
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Requirements Text
                  </label>
                  <textarea
                    id="requirementsText"
                    rows={15}
                    value={rawText}
                    onChange={(e) => setRawText(e.target.value)}
                    placeholder="Enter your requirements here...&#10;&#10;Example:&#10;User can login to the system&#10;User can search for products&#10;User can add items to cart..."
                    className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
                  />

                  <button
                    onClick={handleTextExtraction}
                    disabled={loading || !rawText.trim()}
                    className="w-full mt-4 bg-primary text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                  >
                    {loading ? '⏳ Extracting...' : '✨ Extract Use Cases'}
                  </button>
                </div>
              ) : (
                <div>
                  <FileUploader
                    onFileSelect={handleFileUpload}
                    uploading={uploading}
                  />
                </div>
              )}
            </div>
          </div>

          {/* RIGHT PANEL: RESULTS */}
          <div>
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Results
              </h2>

              {loading || uploading ? (
                <LoadingSpinner message="Processing your requirements..." />
              ) : results ? (
                <div>
                  {/* Summary */}
                  <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4 mb-6">
                    <h3 className="font-semibold text-indigo-900 mb-2">
                      Extraction Summary
                    </h3>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-indigo-600">Extracted:</span>{' '}
                        <span className="font-bold">{results.extracted_count}</span>
                      </div>
                      <div>
                        <span className="text-indigo-600">Stored:</span>{' '}
                        <span className="font-bold">{results.stored_count}</span>
                      </div>
                      <div>
                        <span className="text-indigo-600">Duplicates:</span>{' '}
                        <span className="font-bold">{results.duplicate_count || 0}</span>
                      </div>
                      <div>
                        <span className="text-indigo-600">Time:</span>{' '}
                        <span className="font-bold">{results.processing_time_seconds}s</span>
                      </div>
                    </div>
                  </div>

                  {/* Use Case List */}
                  <div className="space-y-4">
                    <h3 className="font-semibold text-gray-900">
                      Generated Use Cases ({results.results?.length || 0})
                    </h3>
                    
                    {results.results && results.results.length > 0 ? (
                      results.results.map((uc, idx) => (
                        <div
                          key={idx}
                          className={`p-4 border rounded-lg ${
                            uc.status === 'stored'
                              ? 'border-green-200 bg-green-50'
                              : 'border-yellow-200 bg-yellow-50'
                          }`}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h4 className="font-medium text-gray-900">
                                {uc.title}
                              </h4>
                              <span
                                className={`text-xs px-2 py-1 rounded-full inline-block mt-2 ${
                                  uc.status === 'stored'
                                    ? 'bg-green-200 text-green-800'
                                    : 'bg-yellow-200 text-yellow-800'
                                }`}
                              >
                                {uc.status === 'stored' ? '✅ Stored' : '🔄 Duplicate'}
                              </span>

                              {/* Details Preview */}
                              <div className="mt-3 space-y-3">
                                {Array.isArray(uc.preconditions) && uc.preconditions.length > 0 && (
                                  <div>
                                    <div className="text-xs font-semibold text-gray-700">Preconditions</div>
                                    <ul className="list-disc list-inside text-xs text-gray-700">
                                      {uc.preconditions.map((p, i) => (
                                        <li key={i}>{p}</li>
                                      ))}
                                    </ul>
                                  </div>
                                )}

                                {(() => {
                                  const flows = Array.isArray(uc.main_flows)
                                    ? uc.main_flows
                                    : Array.isArray(uc.main_flow)
                                    ? [uc.main_flow]
                                    : [];
                                  return flows.length > 0 ? (
                                    <div>
                                      <div className="text-xs font-semibold text-gray-700">Main Flows</div>
                                      <div className="space-y-1 text-xs text-gray-700">
                                        {flows.map((flow, fi) => (
                                          <div key={fi}>
                                            {Array.isArray(flow) ? (
                                              <ol className="list-decimal list-inside">
                                                {flow.map((s, si) => (
                                                  <li key={si}>{s}</li>
                                                ))}
                                              </ol>
                                            ) : typeof flow === 'object' && flow !== null && Array.isArray(flow.steps) ? (
                                              <ol className="list-decimal list-inside">
                                                {flow.steps.map((s, si) => (
                                                  <li key={si}>{s}</li>
                                                ))}
                                              </ol>
                                            ) : (
                                              <div>• {String(flow)}</div>
                                            )}
                                          </div>
                                        ))}
                                      </div>
                                    </div>
                                  ) : null;
                                })()}

                                {Array.isArray(uc.sub_flows) && uc.sub_flows.length > 0 && (
                                  <div>
                                    <div className="text-xs font-semibold text-gray-700">Sub Flows</div>
                                    <div className="space-y-1 text-xs text-gray-700">
                                      {uc.sub_flows.map((sub, si) => (
                                        <div key={si}>
                                          {typeof sub?.title === 'string' && (
                                            <div className="font-medium text-gray-700">{sub.title}</div>
                                          )}
                                          {Array.isArray(sub?.steps) ? (
                                            <ol className="list-decimal list-inside">
                                              {sub.steps.map((s, i) => (
                                                <li key={i}>{s}</li>
                                              ))}
                                            </ol>
                                          ) : Array.isArray(sub) ? (
                                            <ol className="list-decimal list-inside">
                                              {sub.map((s, i) => (
                                                <li key={i}>{s}</li>
                                              ))}
                                            </ol>
                                          ) : null}
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {Array.isArray(uc.alternate_flows) && uc.alternate_flows.length > 0 && (
                                  <div>
                                    <div className="text-xs font-semibold text-gray-700">Alternate Flows</div>
                                    <ul className="list-disc list-inside text-xs text-gray-700">
                                      {uc.alternate_flows.map((alt, i) => (
                                        <li key={i}>{alt}</li>
                                      ))}
                                    </ul>
                                  </div>
                                )}

                                {Array.isArray(uc.outcomes) && uc.outcomes.length > 0 && (
                                  <div>
                                    <div className="text-xs font-semibold text-gray-700">Outcomes</div>
                                    <ul className="list-disc list-inside text-xs text-gray-700">
                                      {uc.outcomes.map((o, i) => (
                                        <li key={i}>{o}</li>
                                      ))}
                                    </ul>
                                  </div>
                                )}

                                {Array.isArray(uc.stakeholders) && uc.stakeholders.length > 0 && (
                                  <div>
                                    <div className="text-xs font-semibold text-gray-700">Stakeholders</div>
                                    <div className="text-xs text-gray-700">{uc.stakeholders.join(', ')}</div>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="text-gray-500 text-sm">No use cases extracted</p>
                    )}
                  </div>

                  {/* Validation Results */}
                  {results.validation_results && results.validation_results.length > 0 && (
                    <div className="mt-6">
                      <h3 className="font-semibold text-gray-900 mb-3">
                        Quality Validation
                      </h3>
                      <div className="space-y-2">
                        {results.validation_results.map((validation, idx) => (
                          <div
                            key={idx}
                            className="text-sm p-3 border rounded bg-gray-50"
                          >
                            <div className="font-medium text-gray-900 mb-1">
                              {validation.title}
                            </div>
                            {validation.quality_score && (
                              <div className="text-gray-600">
                                Quality: {validation.quality_score}/100
                              </div>
                            )}
                            {validation.issues && validation.issues.length > 0 && (
                              <div className="text-yellow-600 text-xs mt-1">
                                {validation.issues.length} issue(s) found
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <p className="text-4xl mb-4">📋</p>
                  <p>Results will appear here after extraction</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Extraction;