// -----------------------------------------------------------------------------
// File: Summarize.jsx (Debug Version)
// Description: Summary page with debugging to see what's happening
// -----------------------------------------------------------------------------

import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { toast } from 'react-toastify';
import useSessionStore from '../store/useSessionStore';
import SessionHeader from '../components/layout/SessionHeader';
import LoadingSpinner from '../components/LoadingSpinner';

function Summarize() {
  const { currentSessionId } = useSessionStore();
  const [summary, setSummary] = useState(null);
  const [expandedSummaries, setExpandedSummaries] = useState({});
  const [loading, setLoading] = useState(false);
  const [sessionData, setSessionData] = useState(null);
  const [debugInfo, setDebugInfo] = useState({});

  // DEBUG: Log when component mounts and when sessionId changes
  useEffect(() => {
    console.log('🔍 Summarize mounted');
    console.log('🔍 Current Session ID:', currentSessionId);
    
    if (currentSessionId) {
      loadSessionAndSummarize();
    } else {
      console.log('⚠️ No session ID found');
      setSummary(null);
      setSessionData(null);
    }
  }, [currentSessionId]);

  const loadSessionAndSummarize = async () => {
    console.log('📡 Loading session data for:', currentSessionId);
    setLoading(true);
    
    try {
      // First, load the session history
      console.log('📡 Fetching session history...');
      const historyResponse = await api.getSessionHistory(currentSessionId, 50);
      console.log('✅ History response:', historyResponse.data);
      
      const history = historyResponse.data.conversation_history || [];
      const useCases = historyResponse.data.generated_use_cases || [];
      
      console.log('📊 Found messages:', history.length);
      console.log('📊 Found use cases:', useCases.length);

      setDebugInfo({
        totalMessages: history.length,
        totalUseCases: useCases.length,
        messagesWithUseCases: history.filter(m => m.metadata?.use_cases?.length > 0).length,
      });
      
      setSessionData({
        history,
        useCases,
        sessionTitle: historyResponse.data.session_context?.session_title || 'Untitled Session',
      });

      // Check if there are any use cases to summarize
      const messagesWithUseCases = history.filter(
        msg => msg.metadata?.use_cases && msg.metadata.use_cases.length > 0
      );

      console.log('📊 Messages with use cases:', messagesWithUseCases.length);

      if (messagesWithUseCases.length === 0 && useCases.length === 0) {
        console.log('⚠️ No use cases found to summarize');
        setSummary(null);
        setLoading(false);
        return;
      }

      // Format messages for the summarization API
      console.log('🔄 Formatting messages for API...');
      const chatMessages = messagesWithUseCases.map(msg => ({
        role: msg.role,
        content: msg.content || '',
        use_cases: msg.metadata.use_cases.map(uc => ({
          status: 'stored',
          title: uc.title || 'Untitled',
          preconditions: uc.preconditions || [],
          main_flow: uc.main_flow || [],
          sub_flows: uc.sub_flows || [],
          alternate_flows: uc.alternate_flows || [],
          outcomes: uc.outcomes || [],
          stakeholders: uc.stakeholders || [],
        })),
      }));

      // If we have use cases but no messages with use_cases metadata,
      // create synthetic messages from the use cases
      if (chatMessages.length === 0 && useCases.length > 0) {
        console.log('🔄 Creating synthetic message from use cases...');
        chatMessages.push({
          role: 'assistant',
          content: 'Extracted use cases from session',
          use_cases: useCases.map(uc => ({
            status: 'stored',
            title: uc.title || 'Untitled',
            preconditions: uc.preconditions || [],
            main_flow: uc.main_flow || [],
            sub_flows: uc.sub_flows || [],
            alternate_flows: uc.alternate_flows || [],
            outcomes: uc.outcomes || [],
            stakeholders: uc.stakeholders || [],
          })),
        });
      }

      console.log('📡 Calling summarization API with', chatMessages.length, 'messages');
      console.log('📤 Payload:', { messages: chatMessages });

      // Generate summary
      const summaryResponse = await api.summarizeChatUseCases({ 
        messages: chatMessages 
      });

      console.log('✅ Summary response:', summaryResponse.data);
      setSummary(summaryResponse.data);
      
    } catch (error) {
      console.error('❌ Error fetching summary:', error);
      console.error('❌ Error details:', error.response?.data);
      toast.error('Failed to generate summary: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const toggleSummary = (title) => {
    setExpandedSummaries(prev => ({
      ...prev,
      [title]: !prev[title],
    }));
  };

  const handleRefresh = () => {
    console.log('🔄 Manual refresh triggered');
    if (currentSessionId) {
      loadSessionAndSummarize();
    }
  };

  // No session selected
  if (!currentSessionId) {
    return (
      <div className="h-full flex flex-col">
        <SessionHeader />
        <div className="flex-1 flex flex-col items-center justify-center text-center text-gray-700 dark:text-gray-300 p-6">
          <div className="max-w-md">
            <div className="text-6xl mb-4">📊</div>
            <h1 className="text-3xl font-bold mb-2 text-gray-900 dark:text-white">
              No Session Selected
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Select a session from the sidebar or start a new conversation in Chat to see summaries.
            </p>
            <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 text-sm">
              <p className="font-semibold text-yellow-800 dark:text-yellow-200 mb-2">
                🔍 Debug Info:
              </p>
              <p className="text-yellow-700 dark:text-yellow-300">
                currentSessionId: <code className="bg-yellow-100 dark:bg-yellow-900 px-1 rounded">{String(currentSessionId)}</code>
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-gray-900 transition-colors">
      <SessionHeader />

      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto">
          {/* Header with refresh button */}
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Session Summary
            </h1>
            <button
              onClick={handleRefresh}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 transition-colors"
              title="Refresh summary"
            >
              <svg 
                className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" 
                />
              </svg>
              {loading ? 'Updating...' : 'Refresh'}
            </button>
          </div>

          {loading && !summary ? (
            <div className="flex items-center justify-center py-20">
              <LoadingSpinner message="Generating summary..." />
            </div>
          ) : !summary ? (
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-12 text-center">
              <div className="text-5xl mb-4">📝</div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                No Use Cases Yet
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                This session doesn't have any extracted use cases to summarize.
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-500 mb-4">
                Go to the Chat tab and send requirements text or upload a document.
              </p>
              
              {/* Show what we found */}
              {sessionData && (
                <div className="mt-6 bg-gray-50 dark:bg-gray-900 rounded p-4 text-left">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">What we found:</p>
                  <ul className="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                    <li>• {sessionData.history?.length || 0} messages in conversation</li>
                    <li>• {sessionData.useCases?.length || 0} use cases in database</li>
                    <li>• {debugInfo.messagesWithUseCases || 0} messages with use case metadata</li>
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-6">
              {/* Main summary */}
              <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm">
                <div className="flex items-start gap-3 mb-4">
                  <div className="flex-shrink-0 w-10 h-10 bg-indigo-100 dark:bg-indigo-900 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                      Overview
                    </h2>
                    <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
                      {summary.main_summary}
                    </p>
                  </div>
                </div>
              </div>

              {/* Individual use case summaries */}
              {summary.use_case_summaries && summary.use_case_summaries.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-4">
                    <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                      Use Cases
                    </h2>
                    <span className="px-2 py-1 text-xs font-medium bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300 rounded-full">
                      {summary.use_case_summaries.length}
                    </span>
                  </div>
                  
                  <div className="space-y-3">
                    {summary.use_case_summaries.map((uc, index) => (
                      <div
                        key={uc.title}
                        className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden hover:border-indigo-300 dark:hover:border-indigo-700 transition-colors"
                      >
                        <button
                          onClick={() => toggleSummary(uc.title)}
                          className="w-full px-4 py-3 text-left flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors"
                        >
                          <div className="flex items-center gap-3 flex-1 min-w-0">
                            <span className="flex-shrink-0 w-6 h-6 bg-gray-100 dark:bg-gray-700 rounded flex items-center justify-center text-xs font-medium text-gray-600 dark:text-gray-400">
                              {index + 1}
                            </span>
                            <span className="font-medium text-gray-900 dark:text-white truncate">
                              {uc.title}
                            </span>
                          </div>
                          <svg
                            className={`w-5 h-5 text-gray-400 dark:text-gray-500 flex-shrink-0 transition-transform ${
                              expandedSummaries[uc.title] ? 'transform rotate-180' : ''
                            }`}
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                          </svg>
                        </button>
                        
                        {expandedSummaries[uc.title] && (
                          <div className="px-4 py-3 bg-gray-50 dark:bg-gray-750 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                            <p className="bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap ">
                              {uc.summary}
                            </p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Session info footer */}
              {sessionData && (
                <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-4 text-sm text-gray-600 dark:text-gray-400">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <span>
                        <strong className="text-gray-900 dark:text-white">
                          {sessionData.useCases?.length || 0}
                        </strong>{' '}
                        use cases
                      </span>
                      <span>•</span>
                      <span>
                        <strong className="text-gray-900 dark:text-white">
                          {sessionData.history?.length || 0}
                        </strong>{' '}
                        messages
                      </span>
                    </div>
                    <button
                      onClick={handleRefresh}
                      className="text-indigo-600 dark:text-indigo-400 hover:underline text-xs"
                    >
                      Update summary
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Summarize;