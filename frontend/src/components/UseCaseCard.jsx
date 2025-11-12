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
import { api } from '../api/client';
import { toast } from 'react-toastify';
import QualityBadge from './QualityBadge';

function UseCaseCard({ useCase, onDelete, onRefined }) {
  const [expanded, setExpanded] = useState(false);
  const [refiningUseCase, setRefiningUseCase] = useState(null);
  const [refineType, setRefineType] = useState('more_main_flows');
  const [refining, setRefining] = useState(false);
  const navigate = useNavigate();

  const qualityScore = useCase.quality_score || 75;

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
      
      // Notify parent component to refresh use cases
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

  return (
    <>
    <div
      data-testid="use-case-card"
      className={`bg-white border rounded-lg p-6 shadow-sm hover:shadow-md transition ${
        useCase._refined ? 'border-green-400 bg-green-50' : ''
      }`}>
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-2 flex-1">
          <h3 className="text-xl font-semibold text-gray-900">
            {useCase.title}
          </h3>
          {useCase._refined && (
            <span className="text-xs px-2 py-1 bg-green-200 text-green-800 rounded-full">
              ✨ Refined
            </span>
          )}
        </div>
        <QualityBadge score={qualityScore} />
      </div>

      {/* Stakeholders */}
      <div className="mb-4">
        <span className="text-sm text-gray-500">Stakeholders: </span>
        <span className="text-sm text-gray-700">
          {useCase.stakeholders?.join(', ') || 'N/A'}
        </span>
      </div>

      {/* Main Flow Preview */}
      <div className="mb-4">
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-sm text-primary hover:underline"
        >
          {expanded ? '▼ Hide Details' : '▶ Show Details'}
        </button>

        {expanded && (
          <div className="mt-4 space-y-4">
            {/* Preconditions */}
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Preconditions:</h4>
              <ul className="list-disc list-inside text-sm text-gray-600">
                {useCase.preconditions?.map((p, i) => (
                  <li key={i}>{p}</li>
                ))}
              </ul>
            </div>

            {/* Main Flows */}
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Main Flows:</h4>
              {/* Support both new `main_flows` and legacy `main_flow` */}
              {(() => {
                const flows = Array.isArray(useCase.main_flows)
                  ? useCase.main_flows
                  : Array.isArray(useCase.main_flow)
                  ? [useCase.main_flow]
                  : [];
                return flows.length > 0 ? (
                <div className="space-y-2">
                  {flows.map((flow, fi) => (
                    <div key={fi} className="text-sm text-gray-600">
                      {Array.isArray(flow) ? (
                        <ol className="list-decimal list-inside">
                          {flow.map((step, si) => (
                            <li key={si}>{step}</li>
                          ))}
                        </ol>
                      ) : typeof flow === 'object' && flow !== null && Array.isArray(flow.steps) ? (
                        <ol className="list-decimal list-inside">
                          {flow.steps.map((step, si) => (
                            <li key={si}>{step}</li>
                          ))}
                        </ol>
                      ) : (
                        <div>• {String(flow)}</div>
                      )}
                    </div>
                  ))}
                </div>
                ) : null;
              })()}
            </div>

            {/* Sub Flows */}
            {Array.isArray(useCase.sub_flows) && useCase.sub_flows.length > 0 && (
              <div>
                <h4 className="font-semibold text-gray-700 mb-2">Sub Flows:</h4>
                <div className="space-y-3">
                  {useCase.sub_flows.map((sub, si) => (
                    <div key={si} className="text-sm text-gray-600">
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
                      ) : Array.isArray(useCase.sub_flows) ? null : null}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Alternate Flows */}
            {Array.isArray(useCase.alternate_flows) && useCase.alternate_flows.length > 0 && (
              <div>
                <h4 className="font-semibold text-gray-700 mb-2">Alternate Flows:</h4>
                <ul className="list-disc list-inside text-sm text-gray-600">
                  {useCase.alternate_flows.map((alt, i) => (
                    <li key={i}>{alt}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Outcomes */}
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Outcomes:</h4>
              <ul className="list-disc list-inside text-sm text-gray-600">
                {useCase.outcomes?.map((o, i) => (
                  <li key={i}>{o}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <button
          onClick={() => navigate(`/use-case/${useCase.id}`)}
          className="px-4 py-2 bg-primary text-white rounded hover:bg-indigo-700 transition text-sm"
        >
          View Details
        </button>
        {useCase.id && (
          <button
            onClick={() => setRefiningUseCase(useCase.id)}
            className="px-4 py-2 bg-indigo-100 text-indigo-700 rounded hover:bg-indigo-200 transition text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={refining || refiningUseCase === useCase.id}
          >
            {refining && refiningUseCase === useCase.id ? (
              <span className="flex items-center gap-1">
                <span className="animate-spin">⏳</span> Refining...
              </span>
            ) : (
              '✨ Refine'
            )}
          </button>
        )}
        {onDelete && (
          <button
            onClick={() => onDelete(useCase.id)}
            className="px-4 py-2 bg-red-100 text-red-600 rounded hover:bg-red-200 transition text-sm"
          >
            Delete
          </button>
        )}
      </div>
    </div>

    {/* Refine Modal */}
    {refiningUseCase && (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Refine Use Case</h2>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Refinement Type
            </label>
            <select
              value={refineType}
              onChange={(e) => setRefineType(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
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
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
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

export default UseCaseCard;