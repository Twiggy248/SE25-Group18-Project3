// -----------------------------------------------------------------------------
// File: Chat.jsx
// Description: Chat interface page for ReqEngine - provides conversational
//              interaction with AI for requirements analysis and use case queries.
// Author: Pradyumna Chacham
// Date: November 2025
// Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
// License: MIT License - see LICENSE file in the root directory.
// -----------------------------------------------------------------------------

import React, { useState, useRef, useEffect } from 'react';
import { api } from '../api/client';
import { toast } from 'react-toastify';
import useSessionStore from '../store/useSessionStore';
import FileUploader from '../components/FileUploader';
import SessionHeader from '../components/layout/SessionHeader';

function Chat() {
  const { currentSessionId, setCurrentSession } = useSessionStore();
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [refiningUseCase, setRefiningUseCase] = useState(null);
  const [refineType, setRefineType] = useState('more_main_flows');
  const [refining, setRefining] = useState(false);
  const messagesEndRef = useRef(null);

  // Check if there's an active session (messages exist or currentSessionId is set)
  const hasActiveSession = messages.length > 0 || currentSessionId;

  // Normalize backend extraction response for consistent rendering
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
      main_flow: Array.isArray(uc.main_flow) ? uc.main_flow : Array.isArray(uc.main_flows) ? uc.main_flows.flat() : [],
      sub_flows: Array.isArray(uc.sub_flows) ? uc.sub_flows : [],
      alternate_flows: Array.isArray(uc.alternate_flows) ? uc.alternate_flows : [],
      outcomes: Array.isArray(uc.outcomes) ? uc.outcomes : [],
      stakeholders: Array.isArray(uc.stakeholders) ? uc.stakeholders : [],
    }));

    return {
      message: data?.message,
      session_id: data?.session_id,
      extracted_count: Number.isFinite(data?.extracted_count) ? data.extracted_count : normalizedResults.length,
      processing_time_seconds: data?.processing_time_seconds,
      validation_results: Array.isArray(data?.validation_results) ? data.validation_results : [],
      results: normalizedResults,
    };
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (currentSessionId) {
      loadConversationHistory();
    } else {
      setMessages([]);
    }
  }, [currentSessionId]);

  const loadConversationHistory = async () => {
    try {
      const response = await api.getSessionHistory(currentSessionId, 50);
      const history = response.data.conversation_history || [];
      const freshUseCases = response.data.generated_use_cases || [];
      
      // Update session title in store if available
      const sessionTitle = response.data.session_context?.session_title;
      if (sessionTitle && sessionTitle !== 'New Session') {
        setCurrentSession(currentSessionId, sessionTitle);
      }
      
      const freshUseCasesMap = new Map();
      freshUseCases.forEach(uc => {
        if (uc.id) {
          freshUseCasesMap.set(uc.id, uc);
        }
      });
      
      const formattedMessages = [];
      for (let i = 0; i < history.length; i++) {
        const msg = history[i];
        const prevMsg = i > 0 ? history[i - 1] : null;
        
        const isLongText = msg.role === 'user' && 
                          msg.content && 
                          msg.content.length > 200;
        
        const prevWasDocumentUpload = prevMsg && 
                                     prevMsg.metadata?.type === 'document_upload';
        
        if (isLongText && prevWasDocumentUpload && msg.metadata?.type !== 'document_upload') {
          continue;
        }
        
        let useCases = undefined;
        if (Array.isArray(msg.metadata?.use_cases)) {
          useCases = msg.metadata.use_cases.map(uc => {
            const ucId = uc.id || uc.use_case_id;
            if (ucId && freshUseCasesMap.has(ucId)) {
              return freshUseCasesMap.get(ucId);
            }
            return {
              ...uc,
              id: ucId || undefined,
            };
          });
        }
        
        formattedMessages.push({
          role: msg.role,
          content: msg.content,
          metadata: msg.metadata,
          results: useCases,
          validation_results: Array.isArray(msg.metadata?.validation_results) ? msg.metadata.validation_results : undefined,
        });
      }
      
      setMessages(formattedMessages);
    } catch (error) {
      console.log('Could not load history');
    }
  };

  const handleSendText = async () => {
    if (!inputText.trim()) {
      toast.error('Please enter some text');
      return;
    }

    const userMessage = {
      role: 'user',
      content: inputText,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setLoading(true);

    try {
      // Enhanced logging for text input
      console.log('💬 Text Input Session Debug:');
      console.log('   Current Session ID:', currentSessionId || 'None (new session will be created)');
      console.log('   Input Text Length:', inputText.length);
      console.log('   Messages in Chat:', messages.length);
      
      const response = await api.extractFromText({
        raw_text: inputText,
        session_id: currentSessionId || undefined,
      });
      const normalized = normalizeExtractionResponse(response.data);

      if (!currentSessionId) {
        // For new sessions, fetch the session title from backend
        try {
          const titleResponse = await api.getSessionTitle(normalized.session_id);
          const sessionTitle = titleResponse.data.session_title || 'New Session';
          setCurrentSession(normalized.session_id, sessionTitle);
        } catch (error) {
          console.warn('Could not fetch session title, using default');
          setCurrentSession(normalized.session_id);
        }
      }

      const { setSessions } = useSessionStore.getState();

      try{
        const sessionsList = await api.getSessions();
        setSessions(sessionsList.data.sessions);
      }catch (err){
        console.warn("Couldn't refresh sessions sidebar")
      }

      const assistantMessage = {
        role: 'assistant',
        content: `✅ Extracted ${normalized.extracted_count} use cases in ${normalized.processing_time_seconds}s`,
        results: normalized.results,
        validation_results: normalized.validation_results,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMessage]);
      toast.success('Use cases extracted!');
    } catch (error) {
      console.error('Extraction error:', error);
      const errorMessage = {
        role: 'assistant',
        content: '⚠ Could not process request. Make sure backend is running.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

 const handleFileUpload = async (file) => {
  const userMessage = {
    role: 'user',
    content: '',
    metadata: {
      type: 'document_upload',
      filename: file.name,
      size: file.size,
    },
    timestamp: new Date().toISOString(),
  };

  setMessages(prev => [...prev, userMessage]);
  setLoading(true);
  setShowFileUpload(false);

  try {
    // Create FormData
    const formData = new FormData();
    formData.append('file', file);

    // Enhanced logging to track session behavior
    console.log('📤 File Upload Session Debug:');
    console.log('   Current Session ID:', currentSessionId || 'None (new session will be created)');
    console.log('   File Name:', file.name);
    console.log('   Messages in Chat:', messages.length);
    
    const response = await api.extractFromDocument(formData, {
      session_id: currentSessionId,  // Pass current session via options
      // project_context and domain are optional - backend will use session context
    });

    console.log('✅ File upload response received:');
    console.log('   Response Session ID:', response.data.session_id);
    console.log('   Expected Session ID:', currentSessionId || 'New session expected');
    
    const normalized = normalizeExtractionResponse(response.data);

    // ✅ Verify session was maintained
    if (currentSessionId && response.data.session_id !== currentSessionId) {
      console.warn('⚠️ WARNING: Backend returned different session!');
      console.warn('   Expected:', currentSessionId);
      console.warn('   Received:', response.data.session_id);
    } else if (currentSessionId) {
      console.log('✅ Session maintained:', currentSessionId);
    }

    if (!currentSessionId) {
      // Only set session for truly new sessions (when we had no current session)
      try {
        const titleResponse = await api.getSessionTitle(normalized.session_id);
        const sessionTitle = titleResponse.data.session_title || 
                            file.name.replace(/\.[^/.]+$/, ""); // Fallback to filename without extension
        setCurrentSession(normalized.session_id, sessionTitle);
        console.log('🆕 New session created from file upload:', normalized.session_id, 'with title:', sessionTitle);
      } catch (error) {
        console.warn('Could not fetch session title, using filename');
        setCurrentSession(normalized.session_id, file.name.replace(/\.[^/.]+$/, ""));
      }
    } else {
      // We had an existing session, it should have been maintained
      console.log('✅ File uploaded to existing session:', currentSessionId);
      if (normalized.session_id !== currentSessionId) {
        console.error('🚨 CRITICAL: Session ID mismatch detected!');
        console.error('   Frontend session:', currentSessionId);
        console.error('   Backend returned:', normalized.session_id);
        // In this case, we should update to use the backend session
        setCurrentSession(normalized.session_id);
      }
    }

    const assistantMessage = {
      role: 'assistant',
      content: `✅ Extracted ${normalized.extracted_count} use cases from ${file.name}`,
      results: normalized.results,
      validation_results: normalized.validation_results,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, assistantMessage]);
    toast.success('Document processed!');
  } catch (error) {
    console.error('Upload error:', error);
    const errorMessage = {
      role: 'assistant',
      content: '⚠ Could not process file. Make sure backend is running.',
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, errorMessage]);
  } finally {
    setLoading(false);
  }
};

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendText();
    }
  };

  const handleRefineUseCase = async (useCaseId, refinementType) => {
    setRefining(true);
    toast.info('Refining use case...', { autoClose: 2000 });
    
    try {
      const response = await api.refineUseCase({
        use_case_id: useCaseId,
        refinement_type: refinementType,
      });

      const refinedData = response.data.refined_use_case;
      
      toast.success('✨ Use case refined successfully! Refreshing...');
      
      await new Promise(resolve => setTimeout(resolve, 800));
      
      if (currentSessionId) {
        await loadConversationHistory();
      } else {
        setMessages(prevMessages => {
          return prevMessages.map(msg => {
            if (msg.results && Array.isArray(msg.results)) {
              return {
                ...msg,
                results: msg.results.map(uc => {
                  if (uc.id === useCaseId) {
                    return {
                      ...uc,
                      ...refinedData,
                      id: useCaseId,
                      _refined: true,
                    };
                  }
                  return uc;
                }),
              };
            }
            return msg;
          });
        });
      }
      
      setRefiningUseCase(null);
      setRefineType('more_main_flows');
      
      setTimeout(() => {
        scrollToBottom();
      }, 100);
      
    } catch (error) {
      console.error('Refinement error:', error);
      toast.error(error.response?.data?.detail || 'Failed to refine use case. Please try again.');
    } finally {
      setRefining(false);
    }
  };

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Show Session Header only when there's an active session */}
      {hasActiveSession && <SessionHeader />}

      <div className="flex-1 overflow-y-auto p-6">
        {messages.length === 0 ? (
          <div className="max-w-3xl mx-auto text-center py-20">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Welcome to ReqEngine 
            </h1>
            <p className="text-lg text-gray-600 mb-8">
              Transform unstructured requirements into structured use cases
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
              <div className="bg-white p-4 rounded-lg border">
                <p className="font-semibold text-gray-900 mb-2">💡 Example:</p>
                <p className="text-sm text-gray-600">
                  "User can login to the system. User can search for products and add items to cart."
                </p>
              </div>
              <div className="bg-white p-4 rounded-lg border">
                <p className="font-semibold text-gray-900 mb-2">📄 Or upload:</p>
                <p className="text-sm text-gray-600">
                  PDF, DOCX, TXT, or MD files with your requirements
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto space-y-6 pb-4">
            {messages.map((message, idx) => {
              const prevMsg = idx > 0 ? messages[idx - 1] : null;
              const isLongParsedText = message.role === 'user' && 
                                      message.content && 
                                      message.content.length > 200 &&
                                      message.metadata?.type !== 'document_upload' &&
                                      prevMsg?.metadata?.type === 'document_upload';
              
              if (isLongParsedText) {
                return null;
              }
              
              return (
              <div
                key={idx}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-3xl rounded-lg p-4 ${
                    message.role === 'user'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-white border'
                  }`}
                >
                  {message.metadata?.type === 'document_upload' ? (
                    <div className={`flex items-center gap-3 ${message.role === 'user' ? 'text-white' : 'text-gray-900'}`}>
                      <div className={`flex items-center justify-center w-9 h-9 rounded-md ${message.role === 'user' ? 'bg-white/15' : 'bg-indigo-100 text-indigo-700'}`}>
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                          <path d="M19.5 8.25v9.75A2.25 2.25 0 0 1 17.25 20.25H6.75A2.25 2.25 0 0 1 4.5 18V6A2.25 2.25 0 0 1 6.75 3.75h6.939a2.25 2.25 0 0 1 1.591.659l3.061 3.061a2.25 2.25 0 0 1 .659 1.591z"/>
                          <path d="M14.25 3.75v3.75a.75.75 0 0 0 .75.75h3.75"/>
                        </svg>
                      </div>
                      <div className="min-w-0">
                        <div className={`font-medium ${message.role === 'user' ? 'text-white' : 'text-gray-900'}`}>
                          {message.metadata.filename}
                        </div>
                        {typeof message.metadata.size === 'number' && (
                          <div className={`text-xs ${message.role === 'user' ? 'text-white/80' : 'text-gray-500'}`}>
                            {(message.metadata.size / 1024).toFixed(1)} KB
                          </div>
                        )}
                      </div>
                    </div>
                  ) : (
                    message.content && !/^\s*Smart extraction:/i.test(message.content) && !/^\s*✅ Extracted/i.test(message.content) && (
                      <p className="whitespace-pre-wrap">{message.content}</p>
                    )
                  )}

                  {message.results && message.results.length > 0 && (
                    <div className="mt-4 space-y-4">
                      {message.results.map((uc, i) => {
                        return (
                          <div 
                            key={i} 
                            className={`bg-gray-50 border rounded-lg p-4 text-gray-900 ${
                              uc._refined ? 'border-green-400 bg-green-50' : ''
                            } transition-all duration-300`}
                          >
                            <div className="flex items-center justify-between mb-3">
                              <div className="flex items-center gap-2">
                                <p className="font-bold text-lg">{uc.title}</p>
                                {uc._refined && (
                                  <span className="text-xs px-2 py-1 bg-green-200 text-green-800 rounded-full">
                                    ✨ Refined
                                  </span>
                                )}
                              </div>
                            </div>

                            {uc.preconditions && uc.preconditions.length > 0 && (
                              <div className="mb-3">
                                <p className="font-semibold text-indigo-700 mb-1">📋 Preconditions:</p>
                                <ul className="list-disc list-inside ml-2 space-y-1">
                                  {uc.preconditions.map((pre, idx) => (
                                    <li key={idx} className="text-sm text-gray-700">
                                      {pre}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {uc.main_flow && uc.main_flow.length > 0 && (
                              <div className="mb-3">
                                <p className="font-semibold text-indigo-700 mb-1">🔄 Main Flow:</p>
                                <ol className="list-decimal list-inside ml-2 space-y-1">
                                  {uc.main_flow.map((step, idx) => (
                                    <li key={idx} className="text-sm text-gray-700">
                                      {step}
                                    </li>
                                  ))}
                                </ol>
                              </div>
                            )}

                            {uc.sub_flows && uc.sub_flows.length > 0 && (
                              <div className="mb-3">
                                <p className="font-semibold text-indigo-700 mb-1">🔀 Sub Flows:</p>
                                <ul className="list-disc list-inside ml-2 space-y-1">
                                  {uc.sub_flows.map((sub, idx) => (
                                    <li key={idx} className="text-sm text-gray-700">
                                      {sub}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {uc.alternate_flows && uc.alternate_flows.length > 0 && (
                              <div className="mb-3">
                                <p className="font-semibold text-indigo-700 mb-1">⚠️ Alternate Flows:</p>
                                <ul className="list-disc list-inside ml-2 space-y-1">
                                  {uc.alternate_flows.map((alt, idx) => (
                                    <li key={idx} className="text-sm text-gray-700">
                                      {alt}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {uc.outcomes && uc.outcomes.length > 0 && (
                              <div className="mb-3">
                                <p className="font-semibold text-indigo-700 mb-1">✅ Outcomes:</p>
                                <ul className="list-disc list-inside ml-2 space-y-1">
                                  {uc.outcomes.map((outcome, idx) => (
                                    <li key={idx} className="text-sm text-gray-700">
                                      {outcome}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {uc.stakeholders && uc.stakeholders.length > 0 && (
                              <div>
                                <p className="font-semibold text-indigo-700 mb-1">👥 Stakeholders:</p>
                                <div className="flex flex-wrap gap-2">
                                  {uc.stakeholders.map((stakeholder, idx) => (
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

                            <div className="mt-4 pt-3 border-t border-gray-200">
                              {uc.id ? (
                                <div className="flex items-center gap-2">
                                  <button
                                    onClick={() => setRefiningUseCase(uc.id)}
                                    className="text-sm px-3 py-1.5 bg-indigo-100 text-indigo-700 rounded hover:bg-indigo-200 transition disabled:opacity-50 disabled:cursor-not-allowed"
                                    disabled={refining || refiningUseCase === uc.id}
                                  >
                                    {refining && refiningUseCase === uc.id ? (
                                      <span className="flex items-center gap-1">
                                        <span className="animate-spin">⏳</span> Refining...
                                      </span>
                                    ) : (
                                      '✨ Refine Use Case'
                                    )}
                                  </button>
                                </div>
                              ) : (
                                <p className="text-xs text-gray-500">
                                  💡 Refinement available for stored use cases only
                                </p>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
              );
            })}

            {loading && (
              <div className="flex justify-start">
                <div className="bg-white border rounded-lg p-4">
                  <div className="flex gap-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: '0.1s' }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: '0.2s' }}
                    ></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

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

      <div className="border-t bg-white p-4 flex-shrink-0">
        <div className="max-w-4xl mx-auto">
          {showFileUpload ? (
            <div>
              <FileUploader onFileSelect={handleFileUpload} uploading={loading} />
              <button
                onClick={() => setShowFileUpload(false)}
                className="mt-2 text-sm text-gray-600 hover:text-gray-900"
              >
                ← Back to text input
              </button>
            </div>
          ) : (
            <div className="flex gap-2 items-end">
              <button
                onClick={() => setShowFileUpload(true)}
                disabled={loading}
                className="p-3 text-gray-600 hover:bg-gray-100 rounded-lg transition disabled:opacity-50 flex-shrink-0"
                title="Upload file"
              >
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"
                  />
                </svg>
              </button>

              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Describe your requirements... (Press Enter to send, Shift+Enter for new line)"
                className="flex-1 px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                rows={2}
                disabled={loading}
              />

              <button
                onClick={handleSendText}
                disabled={loading || !inputText.trim()}
                className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium flex-shrink-0"
              >
                {loading ? '⏳' : '⬆'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Chat;