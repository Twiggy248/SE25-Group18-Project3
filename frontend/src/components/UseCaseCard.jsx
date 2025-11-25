// -----------------------------------------------------------------------------
// File: UseCaseCard.jsx
// Description: Use case display component for ReqEngine - renders individual
//              use cases with expand/collapse, refinement, and quality indicators.
// Author: Pradyumna Chacham
// Date: November 2025
// Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
// License: MIT License - see LICENSE file in the root directory.
// -----------------------------------------------------------------------------

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import { api } from '../api/client';
import { toast } from 'react-toastify';
import QualityBadge from './QualityBadge';

function UseCaseCard({ useCase, onDelete, onRefined, compact = false, showActions = true }) {
  const [expanded, setExpanded] = useState(false);
  const [refiningUseCase, setRefiningUseCase] = useState(null);
  const [refineType, setRefineType] = useState('more_main_flows');
  const [refining, setRefining] = useState(false);
  const navigate = useNavigate();
  const { getStakeholderColor, stakeholderColorMode, darkMode } = useTheme();

  const qualityScore = useCase.quality_score || 75;

  // Get themed colors for this use case
  const colors = getStakeholderColor(useCase.stakeholders);

  // Handle use case refinement
  const handleRefineUseCase = async (useCaseId, refinementType) => {
    setRefining(true);
    toast.info('Refining use case...', { autoClose: 2000 });
    
    try {
      const response = await api.refineUseCase({
        use_case_id: useCaseId,
        refinement_type: refinementType,
      });

      console.log('Refinement response:', response.data);
      toast.success('✨ Use case refined successfully!');
      
      if (onRefined) {
        onRefined();
      }
      
      setRefiningUseCase(null);
      setRefineType('more_main_flows');
    } catch (error) {
      console.error('Refinement error:', error);
      toast.error(error.response?.data?.detail || 'Failed to refine use case. Please try again.');
    } finally {
      setRefining(false);
    }
  };

  // Compact view for chat
  if (compact) {
    return (
      <>
        <div 
          className={`rounded-lg p-4 transition-all duration-300 ${
            useCase._refined ? 'ring-2 ring-green-400 dark:ring-green-500' : ''
          }`}
          style={stakeholderColorMode ? {
            backgroundColor: colors.backgroundColor,
            borderWidth: '2px',
            borderStyle: 'solid',
            borderColor: colors.borderColor
          } : {
            backgroundColor: darkMode ? '#1f2937' : '#ffffff',
            borderWidth: '2px',
            borderStyle: 'solid',
            borderColor: darkMode ? '#374151' : '#e5e7eb'
          }}
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <p 
                className="font-bold text-lg"
                style={stakeholderColorMode ? { 
                  color: colors.textColor 
                } : { 
                  color: darkMode ? '#f3f4f6' : '#111827' 
                }}
              >
                {useCase.title}
              </p>
              {useCase._refined && (
                <span className="text-xs px-2 py-1 bg-green-200 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-full">
                  ✨ Refined
                </span>
              )}
            </div>
          </div>

          {/* Preconditions */}
          {useCase.preconditions && useCase.preconditions.length > 0 && (
            <div className="mb-3">
              <p 
                className="font-semibold mb-1"
                style={stakeholderColorMode ? { 
                  color: colors.textColor 
                } : { 
                  color: darkMode ? '#f3f4f6' : '#111827' 
                }}
              >
                📋 Preconditions:
              </p>
              <ul className="list-disc list-inside ml-2 space-y-1">
                {useCase.preconditions.map((pre, idx) => (
                  <li 
                    key={idx} 
                    className="text-sm"
                    style={stakeholderColorMode ? { 
                      color: colors.textColor,
                      opacity: 0.9
                    } : { 
                      color: darkMode ? '#d1d5db' : '#4b5563'
                    }}
                  >
                    {pre}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Main Flow */}
          {useCase.main_flow && useCase.main_flow.length > 0 && (
            <div className="mb-3">
              <p 
                className="font-semibold mb-1"
                style={stakeholderColorMode ? { 
                  color: colors.textColor 
                } : { 
                  color: darkMode ? '#f3f4f6' : '#111827' 
                }}
              >
                🔄 Main Flow:
              </p>
              <ol className="list-decimal list-inside ml-2 space-y-1">
                {useCase.main_flow.map((step, idx) => (
                  <li 
                    key={idx} 
                    className="text-sm"
                    style={stakeholderColorMode ? { 
                      color: colors.textColor,
                      opacity: 0.9
                    } : { 
                      color: darkMode ? '#d1d5db' : '#4b5563'
                    }}
                  >
                    {step}
                  </li>
                ))}
              </ol>
            </div>
          )}

          {/* Sub Flows */}
          {useCase.sub_flows && useCase.sub_flows.length > 0 && (
            <div className="mb-3">
              <p 
                className="font-semibold mb-1"
                style={stakeholderColorMode ? { 
                  color: colors.textColor 
                } : { 
                  color: darkMode ? '#f3f4f6' : '#111827' 
                }}
              >
                🔀 Sub Flows:
              </p>
              <ul className="list-disc list-inside ml-2 space-y-1">
                {useCase.sub_flows.map((sub, idx) => (
                  <li 
                    key={idx} 
                    className="text-sm"
                    style={stakeholderColorMode ? { 
                      color: colors.textColor,
                      opacity: 0.9
                    } : { 
                      color: darkMode ? '#d1d5db' : '#4b5563'
                    }}
                  >
                    {sub}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Alternate Flows */}
          {useCase.alternate_flows && useCase.alternate_flows.length > 0 && (
            <div className="mb-3">
              <p 
                className="font-semibold mb-1"
                style={stakeholderColorMode ? { 
                  color: colors.textColor 
                } : { 
                  color: darkMode ? '#f3f4f6' : '#111827' 
                }}
              >
                ⚠️ Alternate Flows:
              </p>
              <ul className="list-disc list-inside ml-2 space-y-1">
                {useCase.alternate_flows.map((alt, idx) => (
                  <li 
                    key={idx} 
                    className="text-sm"
                    style={stakeholderColorMode ? { 
                      color: colors.textColor,
                      opacity: 0.9
                    } : { 
                      color: darkMode ? '#d1d5db' : '#4b5563'
                    }}
                  >
                    {alt}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Outcomes */}
          {useCase.outcomes && useCase.outcomes.length > 0 && (
            <div className="mb-3">
              <p 
                className="font-semibold mb-1"
                style={stakeholderColorMode ? { 
                  color: colors.textColor 
                } : { 
                  color: darkMode ? '#f3f4f6' : '#111827' 
                }}
              >
                ✅ Outcomes:
              </p>
              <ul className="list-disc list-inside ml-2 space-y-1">
                {useCase.outcomes.map((outcome, idx) => (
                  <li 
                    key={idx} 
                    className="text-sm"
                    style={stakeholderColorMode ? { 
                      color: colors.textColor,
                      opacity: 0.9
                    } : { 
                      color: darkMode ? '#d1d5db' : '#4b5563'
                    }}
                  >
                    {outcome}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Stakeholders */}
          {useCase.stakeholders && useCase.stakeholders.length > 0 && (
            <div>
              <p 
                className="font-semibold mb-1"
                style={stakeholderColorMode ? { 
                  color: colors.textColor 
                } : { 
                  color: darkMode ? '#f3f4f6' : '#111827' 
                }}
              >
                👥 Stakeholders:
              </p>
              <div className="flex flex-wrap gap-2">
                {useCase.stakeholders.map((stakeholder, idx) => {
                  const stakeholderColors = getStakeholderColor([stakeholder]);
                  return (
                    <span
                      key={idx}
                      className="text-xs px-2 py-1 rounded-full font-medium"
                      style={stakeholderColorMode ? {
                        backgroundColor: stakeholderColors.badgeBackgroundColor,
                        color: stakeholderColors.badgeTextColor,
                      } : {
                        backgroundColor: darkMode ? '#374151' : '#e5e7eb',
                        color: darkMode ? '#d1d5db' : '#374151',
                      }}
                    >
                      {stakeholder}
                    </span>
                  );
                })}
              </div>
            </div>
          )}

          {/* Actions for compact view */}
          <div className="mt-4 pt-3 border-t" style={{ 
            borderColor: darkMode ? '#374151' : '#e5e7eb' 
          }}>
            {useCase.id ? (
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setRefiningUseCase(useCase.id)}
                  className="text-sm px-3 py-1.5 rounded transition disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{
                    backgroundColor: darkMode ? '#312e81' : '#e0e7ff',
                    color: darkMode ? '#a5b4fc' : '#4338ca'
                  }}
                  disabled={refining || refiningUseCase === useCase.id}
                >
                  {refining && refiningUseCase === useCase.id ? (
                    <span className="flex items-center gap-1">
                      <span className="animate-spin">⏳</span> Refining...
                    </span>
                  ) : (
                    '✨ Refine Use Case'
                  )}
                </button>
              </div>
            ) : (
              <p className="text-xs" style={{ color: darkMode ? '#9ca3af' : '#6b7280' }}>
                💡 Refinement available for stored use cases only
              </p>
            )}
          </div>
        </div>

        {/* Refine Modal */}
        {refiningUseCase && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className={`rounded-lg p-6 max-w-md w-full mx-4 ${
              darkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'
            }`}>
              <h2 className="text-xl font-bold mb-4">Refine Use Case</h2>
              
              <div className="mb-4">
                <label className={`block text-sm font-medium mb-2 ${
                  darkMode ? 'text-gray-200' : 'text-gray-700'
                }`}>
                  Refinement Type
                </label>
                <select
                  value={refineType}
                  onChange={(e) => setRefineType(e.target.value)}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                    darkMode 
                      ? 'bg-gray-700 border-gray-600 text-white' 
                      : 'bg-white border-gray-300 text-gray-900'
                  }`}
                >
                  <option value="more_main_flows">Refine Main Flows</option>
                  <option value="more_sub_flows">Refine Sub Flows</option>
                  <option value="more_alternate_flows">Refine Alternate Flows</option>
                  <option value="more_preconditions">Refine Preconditions</option>
                  <option value="more_stakeholders">Refine Stakeholders</option>
                </select>
              </div>

              <div className="flex gap-3 justify-end">
                <button
                  onClick={() => {
                    setRefiningUseCase(null);
                    setRefineType('more_main_flows');
                  }}
                  className={`px-4 py-2 rounded-lg transition ${
                    darkMode
                      ? 'bg-gray-700 text-gray-200 hover:bg-gray-600'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                  disabled={refining}
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleRefineUseCase(refiningUseCase, refineType)}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  disabled={refining}
                >
                  {refining ? (
                    <>
                      <span className="animate-spin">⏳</span>
                      <span>Refining...</span>
                    </>
                  ) : (
                    <>
                      <span>✨</span>
                      <span>Refine</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}
      </>
    );
  }

  // Full view for other pages (original functionality)
  return (
    <>
      <div
        data-testid="use-case-card"
        className={`border rounded-lg p-6 shadow-sm hover:shadow-md transition ${
          darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
        } ${useCase._refined ? 'border-green-400 bg-green-50 dark:bg-green-900' : ''}`}
        style={!useCase._refined && stakeholderColorMode ? {
          backgroundColor: colors.backgroundColor,
          borderColor: colors.borderColor,
          borderWidth: '2px',
          borderStyle: 'solid',
        } : {}}
      >
        {/* Header */}
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center gap-2 flex-1">
            <h3 
              className={`text-xl font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}
              style={stakeholderColorMode ? { color: colors.textColor } : {}}
            >
              {useCase.title}
            </h3>
            {useCase._refined && (
              <span className="text-xs px-2 py-1 bg-green-200 text-green-800 dark:bg-green-700 dark:text-green-100 rounded-full">
                ✨ Refined
              </span>
            )}
          </div>
          {showActions && <QualityBadge score={qualityScore} />}
        </div>

        {/* Stakeholders */}
        <div className="mb-4">
          <span className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
            Stakeholders:{' '}
          </span>
          <div className="inline-flex flex-wrap gap-2 mt-1">
            {useCase.stakeholders?.map((stakeholder, index) => {
              const stakeholderColors = getStakeholderColor([stakeholder]);
              return (
                <span
                  key={index}
                  className="text-xs px-2 py-1 rounded-full font-medium"
                  style={stakeholderColorMode ? {
                    backgroundColor: stakeholderColors.badgeBackgroundColor,
                    color: stakeholderColors.badgeTextColor,
                  } : {
                    backgroundColor: darkMode ? '#374151' : '#e5e7eb',
                    color: darkMode ? '#d1d5db' : '#374151',
                  }}
                >
                  {stakeholder}
                </span>
              );
            })}
          </div>
        </div>

        {/* Expandable Details */}
        <div className="mb-4">
          <button
            onClick={() => setExpanded(!expanded)}
            className={`text-sm hover:underline ${
              darkMode ? 'text-indigo-400' : 'text-indigo-600'
            }`}
            style={stakeholderColorMode ? { color: colors.textColor } : {}}
          >
            {expanded ? '▼ Hide Details' : '▶ Show Details'}
          </button>

          {expanded && (
            <div className="mt-4 space-y-4">
              {/* All the details sections... */}
              <div>
                <h4 className={`font-semibold mb-2 ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>
                  Preconditions:
                </h4>
                <ul className={`list-disc list-inside text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                  {useCase.preconditions?.map((p, i) => (
                    <li key={i}>{p}</li>
                  ))}
                </ul>
              </div>
              {/* ...rest of expanded content... */}
            </div>
          )}
        </div>

        {/* Actions */}
        {showActions && (
          <div className="flex gap-2">
            <button
              onClick={() => navigate(`/use-case/${useCase.id}`)}
              className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition text-sm"
            >
              View Details
            </button>
            {useCase.id && (
              <button
                onClick={() => setRefiningUseCase(useCase.id)}
                className={`px-4 py-2 rounded transition text-sm disabled:opacity-50 ${
                  darkMode
                    ? 'bg-indigo-900 text-indigo-200 hover:bg-indigo-800'
                    : 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200'
                }`}
                disabled={refining}
              >
                {refining ? '⏳ Refining...' : '✨ Refine'}
              </button>
            )}
            {onDelete && (
              <button
                onClick={() => onDelete(useCase.id)}
                className={`px-4 py-2 rounded transition text-sm ${
                  darkMode
                    ? 'bg-red-900 text-red-200 hover:bg-red-800'
                    : 'bg-red-100 text-red-600 hover:bg-red-200'
                }`}
              >
                Delete
              </button>
            )}
          </div>
        )}
      </div>

      {/* Refine Modal for full view */}
      {refiningUseCase && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className={`rounded-lg p-6 max-w-md w-full mx-4 ${
            darkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'
          }`}>
            <h2 className="text-xl font-bold mb-4">Refine Use Case</h2>
            
            <div className="mb-4">
              <label className={`block text-sm font-medium mb-2 ${
                darkMode ? 'text-gray-200' : 'text-gray-700'
              }`}>
                Refinement Type
              </label>
              <select
                value={refineType}
                onChange={(e) => setRefineType(e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg ${
                  darkMode 
                    ? 'bg-gray-700 border-gray-600 text-white' 
                    : 'bg-white border-gray-300 text-gray-900'
                }`}
              >
                <option value="more_main_flows">Refine Main Flows</option>
                <option value="more_sub_flows">Refine Sub Flows</option>
                <option value="more_alternate_flows">Refine Alternate Flows</option>
                <option value="more_preconditions">Refine Preconditions</option>
                <option value="more_stakeholders">Refine Stakeholders</option>
              </select>
            </div>

            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setRefiningUseCase(null);
                  setRefineType('more_main_flows');
                }}
                className={`px-4 py-2 rounded-lg ${
                  darkMode ? 'bg-gray-700 text-gray-200 hover:bg-gray-600' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
                disabled={refining}
              >
                Cancel
              </button>
              <button
                onClick={() => handleRefineUseCase(refiningUseCase, refineType)}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 flex items-center gap-2"
                disabled={refining}
              >
                {refining ? (
                  <>
                    <span className="animate-spin">⏳</span>
                    <span>Refining...</span>
                  </>
                ) : (
                  <>
                    <span>✨</span>
                    <span>Refine</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default UseCaseCard;