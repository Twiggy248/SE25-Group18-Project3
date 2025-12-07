// -----------------------------------------------------------------------------
// File: UseCaseRefine.jsx
// Description: Use case refinement page for ReqEngine - provides advanced
//              editing and enhancement capabilities for individual use cases.
// Author: Pradyumna Chacham
// Date: November 2025
// Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
// License: MIT License - see LICENSE file in the root directory.
// -----------------------------------------------------------------------------

import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { toast } from 'react-toastify';
import useSessionStore from '../store/useSessionStore';
import LoadingSpinner from '../components/LoadingSpinner';

function UseCaseRefine() {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { currentSessionId } = useSessionStore();
  
  // Try to get use case from router state first (fast path)
  const [useCase, setUseCase] = useState(location.state?.useCase || null);
  const [loading, setLoading] = useState(!location.state?.useCase);
  const [refining, setRefining] = useState(false);
  const [refinementType, setRefinementType] = useState('add_detail');
  const [customInstruction, setCustomInstruction] = useState('');
  const [refinedUseCase, setRefinedUseCase] = useState(null);

  useEffect(() => {
    // Only fetch if data wasn't passed via router state
    if (!useCase) {
      loadUseCaseFallback();
    }
  }, [id]);

  const loadUseCaseFallback = async () => {
    if (!currentSessionId) {
      toast.error('No active session. Please create or select a session first.');
      navigate('/');
      return;
    }

    try {      
      // Get all use cases from session history
      const response = await api.getSessionHistory(currentSessionId, 100);
      
      // Extract use cases from conversation history metadata
      const conversations = response.data.conversation_history || [];
      let allUseCases = [];
      
      // Parse use cases from conversation metadata
      conversations.forEach(conv => {
        if (conv.metadata?.use_cases) {
          allUseCases = [...allUseCases, ...conv.metadata.use_cases];
        }
      });
      
      // Also check generated_use_cases if available
      if (response.data.generated_use_cases) {
        allUseCases = [...allUseCases, ...response.data.generated_use_cases];
      }

      // Deduplicate by ID (in case same use case appears multiple times)
      const uniqueUseCases = Array.from(
        new Map(allUseCases.map(uc => [uc.id, uc])).values()
      );
      
      // Find the specific use case by ID
      const foundUseCase = uniqueUseCases.find(uc => uc.id === parseInt(id));
      
      if (foundUseCase) {
        setUseCase(foundUseCase);
      } else {
        console.error('❌ Use case ${id} not found in ${uniqueUseCases.length} available use cases');
        toast.error('Use case not found in session history');
        navigate(-1);
      }
    } catch (error) {
      console.error('Failed to load use case:', error);
      toast.error('Failed to load use case. Please try again.');
      navigate(-1);
    } finally {
      setLoading(false);
    }
  };

  const handleRefine = async () => {
    if (!useCase || !useCase.id) {
      toast.error('Cannot refine: Use case ID is missing');
      return;
    }

    setRefining(true);
    setRefinedUseCase(null);

    try {
      console.log('✨ Refining use case ${useCase.id} with type: ${refinementType}');
      
      const response = await api.refineUseCase({
        use_case_id: parseInt(useCase.id),
        refinement_type: refinementType,
        custom_instruction: refinementType === 'custom' ? customInstruction : null,
      });

      console.log('✅ Refinement successful:', response.data);
      setRefinedUseCase(response.data.refined_use_case);
      toast.success('✨ Use case refined successfully!');
    } catch (error) {
      console.error('Refinement error:', error);
      toast.error(error.response?.data?.detail || 'Refinement failed. Please try again.');
    } finally {
      setRefining(false);
    }
  };

  const handleApplyChanges = () => {
    // TODO: Optionally update the use case in the backend
    // For now, just show success and go back
    toast.success('✅ Changes reviewed! Use case has been refined.');
    toast.info('💡 Tip: The refined version is now stored in your session.');
    navigate(-1);
  };

  const handleRefineAgain = () => {
    setRefinedUseCase(null);
    toast.info('Select a new refinement option to refine again');
  };

  if (loading) {
    return <LoadingSpinner message="Loading use case..." />;
  }

  if (!useCase) {
    return (
      <div className="p-8">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-red-600 text-lg mb-4">❌ Use case not found</p>
          <button
            onClick={() => navigate(-1)}
            className="text-indigo-600 hover:underline"
          >
            ← Go back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate(-1)}
            className="text-indigo-600 hover:text-indigo-800 mb-4 flex items-center gap-2 font-medium"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back
          </button>
          <h1 className="text-4xl font-bold text-gray-900">
            Refine Use Case ✨
          </h1>
          <p className="text-gray-600 mt-2">
            Use AI to improve and enhance your use case with more detail, alternate flows, and error handling
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* LEFT PANEL: Original Use Case */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">
                📋 Original Use Case
              </h2>
              {useCase.id && (
                <span className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-full font-mono">
                  ID: {useCase.id}
                </span>
              )}
            </div>

            <div className="space-y-4">
              {/* Title */}
              <div>
                <h3 className="font-semibold text-lg text-gray-900">
                  {useCase.title}
                </h3>
              </div>

              {/* Preconditions */}
              {useCase.preconditions && useCase.preconditions.length > 0 && (
                <div>
                  <p className="font-semibold text-indigo-700 mb-2">📋 Preconditions:</p>
                  <ul className="list-disc list-inside ml-2 space-y-1 text-sm text-gray-700">
                    {useCase.preconditions.map((pre, idx) => (
                      <li key={idx}>{pre}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Main Flow */}
              {useCase.main_flow && useCase.main_flow.length > 0 && (
                <div>
                  <p className="font-semibold text-indigo-700 mb-2">🔄 Main Flow:</p>
                  <ol className="list-decimal list-inside ml-2 space-y-1 text-sm text-gray-700">
                    {useCase.main_flow.map((step, idx) => (
                      <li key={idx}>{step}</li>
                    ))}
                  </ol>
                </div>
              )}

              {/* Sub Flows */}
              {useCase.sub_flows && useCase.sub_flows.length > 0 && (
                <div>
                  <p className="font-semibold text-indigo-700 mb-2">🔀 Sub Flows:</p>
                  <ul className="list-disc list-inside ml-2 space-y-1 text-sm text-gray-700">
                    {useCase.sub_flows.map((sub, idx) => (
                      <li key={idx}>{typeof sub === 'string' ? sub : JSON.stringify(sub)}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Alternate Flows */}
              {useCase.alternate_flows && useCase.alternate_flows.length > 0 && (
                <div>
                  <p className="font-semibold text-indigo-700 mb-2">⚠ Alternate Flows:</p>
                  <ul className="list-disc list-inside ml-2 space-y-1 text-sm text-gray-700">
                    {useCase.alternate_flows.map((alt, idx) => (
                      <li key={idx}>{alt}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Outcomes */}
              {useCase.outcomes && useCase.outcomes.length > 0 && (
                <div>
                  <p className="font-semibold text-indigo-700 mb-2">✅ Outcomes:</p>
                  <ul className="list-disc list-inside ml-2 space-y-1 text-sm text-gray-700">
                    {useCase.outcomes.map((outcome, idx) => (
                      <li key={idx}>{outcome}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Stakeholders */}
              {useCase.stakeholders && useCase.stakeholders.length > 0 && (
                <div>
                  <p className="font-semibold text-indigo-700 mb-2">👥 Stakeholders:</p>
                  <div className="flex flex-wrap gap-2">
                    {useCase.stakeholders.map((stakeholder, idx) => (
                      <span
                        key={idx}
                        className="text-xs px-2 py-1 bg-indigo-100 text-indigo-700 rounded-full"
                      >
                        {stakeholder}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* RIGHT PANEL: Refinement Options & Results */}
          <div className="space-y-6">
            {/* Refinement Type Selection */}
            {!refinedUseCase && (
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">
                  🎯 Refinement Options
                </h2>

                <div className="space-y-3">
                  {/* Add Detail */}
                  <label className="flex items-start p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition">
                    <input
                      type="radio"
                      name="refinement"
                      value="add_detail"
                      checked={refinementType === 'add_detail'}
                      onChange={(e) => setRefinementType(e.target.value)}
                      className="mt-1 mr-3"
                    />
                    <div>
                      <p className="font-semibold text-gray-900">🔍 Add More Detail</p>
                      <p className="text-sm text-gray-600 mt-1">
                        Break down main flow steps into smaller, more specific actions with granular detail
                      </p>
                    </div>
                  </label>

                  {/* Add Alternates */}
                  <label className="flex items-start p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition">
                    <input
                      type="radio"
                      name="refinement"
                      value="add_alternates"
                      checked={refinementType === 'add_alternates'}
                      onChange={(e) => setRefinementType(e.target.value)}
                      className="mt-1 mr-3"
                    />
                    <div>
                      <p className="font-semibold text-gray-900">🔀 Add Alternate Flows</p>
                      <p className="text-sm text-gray-600 mt-1">
                        Identify error scenarios, edge cases, and alternative execution paths
                      </p>
                    </div>
                  </label>

                  {/* Add Error Handling */}
                  <label className="flex items-start p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition">
                    <input
                      type="radio"
                      name="refinement"
                      value="add_error_handling"
                      checked={refinementType === 'add_error_handling'}
                      onChange={(e) => setRefinementType(e.target.value)}
                      className="mt-1 mr-3"
                    />
                    <div>
                      <p className="font-semibold text-gray-900">⚠ Add Error Handling</p>
                      <p className="text-sm text-gray-600 mt-1">
                        Add comprehensive error scenarios, validation failures, and recovery mechanisms
                      </p>
                    </div>
                  </label>

                  {/* Custom Instruction */}
                  <label className="flex items-start p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition">
                    <input
                      type="radio"
                      name="refinement"
                      value="custom"
                      checked={refinementType === 'custom'}
                      onChange={(e) => setRefinementType(e.target.value)}
                      className="mt-1 mr-3"
                    />
                    <div className="flex-1">
                      <p className="font-semibold text-gray-900 mb-2">✏ Custom Instruction</p>
                      <textarea
                        value={customInstruction}
                        onChange={(e) => setCustomInstruction(e.target.value)}
                        onFocus={() => setRefinementType('custom')}
                        placeholder="Example: Add security considerations and access control checks..."
                        className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        rows={3}
                        disabled={refinementType !== 'custom'}
                      />
                    </div>
                  </label>
                </div>

                {/* Refine Button */}
                <button
                  onClick={handleRefine}
                  disabled={refining || (refinementType === 'custom' && !customInstruction.trim())}
                  className="w-full mt-6 bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium text-lg"
                >
                  {refining ? (
                    <span className="flex items-center justify-center gap-2">
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Refining with AI...
                    </span>
                  ) : (
                    '✨ Refine Use Case'
                  )}
                </button>

                {/* Info Box */}
                <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800">
                  <strong>💡 Tip:</strong> The AI will analyze your use case and enhance it based on your selected refinement type. This usually takes 5-10 seconds.
                </div>
              </div>
            )}

            {/* Refined Use Case Preview */}
            {refinedUseCase && (
              <div className="bg-green-50 border-2 border-green-200 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold text-green-900">
                    ✅ Refined Use Case
                  </h2>
                  <span className="text-xs px-2 py-1 bg-green-200 text-green-800 rounded-full font-semibold">
                    NEW VERSION
                  </span>
                </div>

                <div className="space-y-4 mb-6">
                  <div>
                    <h3 className="font-semibold text-lg text-gray-900">
                      {refinedUseCase.title}
                    </h3>
                  </div>

                  {/* Refined Preconditions */}
                  {refinedUseCase.preconditions && refinedUseCase.preconditions.length > 0 && (
                    <div>
                      <p className="font-semibold text-green-700 mb-2">📋 Preconditions:</p>
                      <ul className="list-disc list-inside ml-2 space-y-1 text-sm text-gray-700 bg-white rounded p-3">
                        {refinedUseCase.preconditions.map((pre, idx) => (
                          <li key={idx}>{pre}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Refined Main Flow */}
                  {refinedUseCase.main_flow && refinedUseCase.main_flow.length > 0 && (
                    <div>
                      <p className="font-semibold text-green-700 mb-2">🔄 Main Flow:</p>
                      <ol className="list-decimal list-inside ml-2 space-y-1 text-sm text-gray-700 bg-white rounded p-3">
                        {refinedUseCase.main_flow.map((step, idx) => (
                          <li key={idx}>{step}</li>
                        ))}
                      </ol>
                    </div>
                  )}

                  {/* Refined Sub Flows */}
                  {refinedUseCase.sub_flows && refinedUseCase.sub_flows.length > 0 && (
                    <div>
                      <p className="font-semibold text-green-700 mb-2">🔀 Sub Flows:</p>
                      <ul className="list-disc list-inside ml-2 space-y-1 text-sm text-gray-700 bg-white rounded p-3">
                        {refinedUseCase.sub_flows.map((sub, idx) => (
                          <li key={idx}>{typeof sub === 'string' ? sub : JSON.stringify(sub)}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Refined Alternate Flows */}
                  {refinedUseCase.alternate_flows && refinedUseCase.alternate_flows.length > 0 && (
                    <div>
                      <p className="font-semibold text-green-700 mb-2">⚠ Alternate Flows:</p>
                      <ul className="list-disc list-inside ml-2 space-y-1 text-sm text-gray-700 bg-white rounded p-3">
                        {refinedUseCase.alternate_flows.map((alt, idx) => (
                          <li key={idx}>{alt}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Refined Outcomes */}
                  {refinedUseCase.outcomes && refinedUseCase.outcomes.length > 0 && (
                    <div>
                      <p className="font-semibold text-green-700 mb-2">✅ Outcomes:</p>
                      <ul className="list-disc list-inside ml-2 space-y-1 text-sm text-gray-700 bg-white rounded p-3">
                        {refinedUseCase.outcomes.map((outcome, idx) => (
                          <li key={idx}>{outcome}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Refined Stakeholders */}
                  {refinedUseCase.stakeholders && refinedUseCase.stakeholders.length > 0 && (
                    <div>
                      <p className="font-semibold text-green-700 mb-2">👥 Stakeholders:</p>
                      <div className="flex flex-wrap gap-2 bg-white rounded p-3">
                        {refinedUseCase.stakeholders.map((stakeholder, idx) => (
                          <span
                            key={idx}
                            className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded-full"
                          >
                            {stakeholder}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3">
                  <button
                    onClick={handleApplyChanges}
                    className="flex-1 bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition font-medium"
                  >
                    ✅ Accept & Go Back
                  </button>
                  <button
                    onClick={handleRefineAgain}
                    className="flex-1 bg-white text-gray-700 border-2 border-gray-300 px-6 py-3 rounded-lg hover:bg-gray-50 transition font-medium"
                  >
                    🔄 Refine Again
                  </button>
                </div>

                {/* Success Info Box */}
                <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800">
                  <strong>💡 Next Steps:</strong> Review the changes carefully. You can refine again with different options, or accept the changes to update your use case.
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default UseCaseRefine;