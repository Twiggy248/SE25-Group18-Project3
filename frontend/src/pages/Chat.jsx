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
import UseCaseCard from '../components/UseCaseCard';

function Chat() {
  const { currentSessionId, setCurrentSession } = useSessionStore();
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const messagesEndRef = useRef(null);

  const hasActiveSession = messages.length > 0 || currentSessionId;

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
      console.error('Could not load conversation history:', error);
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
      const response = await api.extractFromText({
        raw_text: inputText,
        session_id: currentSessionId || undefined,
      });
      const normalized = normalizeExtractionResponse(response.data);

      if (!currentSessionId) {
        try {
          const titleResponse = await api.getSessionTitle(normalized.session_id);
          const sessionTitle = titleResponse.data.session_title || 'New Session';
          setCurrentSession(normalized.session_id, sessionTitle);
        } catch (error) {
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
        content: '⚠️ Could not process request. Make sure backend is running.',
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
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await api.extractFromDocument(formData, {
        session_id: currentSessionId,
      });
      
      const normalized = normalizeExtractionResponse(response.data);

      if (!currentSessionId) {
        try {
          const titleResponse = await api.getSessionTitle(normalized.session_id);
          const sessionTitle = titleResponse.data.session_title || 
                              file.name.replace(/\.[^/.]+$/, "");
          setCurrentSession(normalized.session_id, sessionTitle);
        } catch (error) {
          setCurrentSession(normalized.session_id, file.name.replace(/\.[^/.]+$/, ""));
        }
      } else if (normalized.session_id !== currentSessionId) {
        setCurrentSession(normalized.session_id);
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
        content: '⚠️ Could not process file. Make sure backend is running.',
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

  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-gray-900 transition-colors">      
      {hasActiveSession && <SessionHeader />}

      <div className="flex-1 overflow-y-auto p-6">
        {messages.length === 0 ? (
          <div className="max-w-3xl mx-auto text-center py-20">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Welcome to ReqEngine 
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">
              Transform unstructured requirements into structured use cases
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
              <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
                <p className="font-semibold text-gray-900 dark:text-white mb-2">💡 Example:</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  "User can login to the system. User can search for products and add items to cart."
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
                <p className="font-semibold text-gray-900 dark:text-white mb-2">📄 Or upload:</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
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
                        ? 'bg-indigo-600 dark:bg-indigo-500 text-white'
                        : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700'
                    }`}
                  >
                    {message.metadata?.type === 'document_upload' ? (
                      <div className={`flex items-center gap-3 ${message.role === 'user' ? 'text-white' : 'text-gray-900 dark:text-white'}`}>
                        <div className={`flex items-center justify-center w-9 h-9 rounded-md ${message.role === 'user' ? 'bg-white/15' : 'bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300'}`}>
                          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                            <path d="M19.5 8.25v9.75A2.25 2.25 0 0 1 17.25 20.25H6.75A2.25 2.25 0 0 1 4.5 18V6A2.25 2.25 0 0 1 6.75 3.75h6.939a2.25 2.25 0 0 1 1.591.659l3.061 3.061a2.25 2.25 0 0 1 .659 1.591z"/>
                            <path d="M14.25 3.75v3.75a.75.75 0 0 0 .75.75h3.75"/>
                          </svg>
                        </div>
                        <div className="min-w-0">
                          <div className={`font-medium ${message.role === 'user' ? 'text-white' : 'text-gray-900 dark:text-white'}`}>
                            {message.metadata.filename}
                          </div>
                          {typeof message.metadata.size === 'number' && (
                            <div className={`text-xs ${message.role === 'user' ? 'text-white/80' : 'text-gray-500 dark:text-gray-400'}`}>
                              {(message.metadata.size / 1024).toFixed(1)} KB
                            </div>
                          )}
                        </div>
                      </div>
                    ) : (
                      message.content && !/^\s*Smart extraction:/i.test(message.content) && !/^\s*✅ Extracted/i.test(message.content) && (
                        <p className={`whitespace-pre-wrap ${message.role === 'assistant' ? 'text-gray-900 dark:text-gray-100' : ''}`}>
                          {message.content}
                        </p>
                      )
                    )}

                    {message.results && message.results.length > 0 && (
                      <div className="mt-4 space-y-4">
                        {message.results.map((uc, i) => (
                          <UseCaseCard
                            key={i}
                            useCase={uc}
                            compact={true}
                            showActions={false}
                            onRefined={loadConversationHistory}
                          />
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {loading && (
              <div className="flex justify-start">
                <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <div className="flex gap-2">
                    <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce"></div>
                    <div
                      className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce"
                      style={{ animationDelay: '0.1s' }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce"
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

      <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4 flex-shrink-0 transition-colors">
        <div className="max-w-4xl mx-auto">
          {showFileUpload ? (
            <div>
              <FileUploader onFileSelect={handleFileUpload} uploading={loading} />
              <button
                onClick={() => setShowFileUpload(false)}
                className="mt-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
              >
                ← Back to text input
              </button>
            </div>
          ) : (
            <div className="flex gap-2 items-end">
              <button
                onClick={() => setShowFileUpload(true)}
                disabled={loading}
                className="p-3 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition disabled:opacity-50 flex-shrink-0"
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
                onKeyDown={handleKeyPress}
                placeholder="Describe your requirements... (Press Enter to send, Shift+Enter for new line)"
                className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none transition-colors"
                rows={2}
                disabled={loading}
              />

              <button
                onClick={handleSendText}
                disabled={loading || !inputText.trim()}
                className="px-6 py-3 bg-indigo-600 dark:bg-indigo-500 text-white rounded-lg hover:bg-indigo-700 dark:hover:bg-indigo-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium flex-shrink-0"
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