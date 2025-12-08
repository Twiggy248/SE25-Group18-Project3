// -----------------------------------------------------------------------------
// File: Query.jsx
// Description: Query page component for ReqEngine - enables natural language
//              queries against extracted use cases using RAG functionality.
// Author: Pradyumna Chacham
// Date: November 2025
// Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
// License: MIT License - see LICENSE file in the root directory.
// -----------------------------------------------------------------------------

import React, { useState } from 'react';
import { api } from '../api/client';
import { toast } from 'react-toastify';
import useSessionStore from '../store/useSessionStore';
import SessionHeader from '../components/layout/SessionHeader';

function Query() {
  const { currentSessionId } = useSessionStore();
  const [question, setQuestion] = useState('');
  const [conversation, setConversation] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleQuery = async () => {
    if (!currentSessionId) {
      toast.error('Please select a session first');
      return;
    }
    if (!question.trim()) {
      toast.error('Please enter a question');
      return;
    }
    const userMessage = { role: 'user', content: question };
    setConversation([...conversation, userMessage]);
    setLoading(true);
    setQuestion('');

    try {
      const response = await api.queryRequirements({
        session_id: currentSessionId,
        question,
      });
      const assistantMessage = {
        role: 'assistant',
        content: response.data.answer,
        relevant_use_cases: response.data.relevant_use_cases,
      };
      setConversation((prev) => [...prev, assistantMessage]);
    } catch {
      toast.error('Query failed');
      setConversation((prev) => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleQuery();
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
                Please select a session from the sidebar or create a new chat to query requirements
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Main query UI with session header
  return (
    <div className="flex flex-col h-full">
      {/* Session Header */}
      <SessionHeader />

      {/* Content */}
      <div className="flex-1 p-8 overflow-y-auto bg-gray-50 dark:bg-gray-900">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-8">
            Query Requirements 💬
          </h1>

            {/* Chat Container */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border">
              <div className="h-96 overflow-y-auto p-6 space-y-4">
                {conversation.length === 0 ? (
                  <div className="text-center text-gray-500 dark:text-gray-400 py-12">
                    <p className="text-4xl mb-4">💬</p>
                    <p>Ask questions about your requirements</p>
                    <p className="text-sm mt-2 dark:text-gray-500">
                      Example: "What are the main actors?" or "Which use cases involve payment?"
                    </p>
                  </div>
                ) : (
                  conversation.map((message, idx) => (
                    <div
                      key={idx}
                      className={`flex ${
                        message.role === 'user' ? 'justify-end' : 'justify-start'
                      }`}
                    >
                      <div
                        className={`max-w-xl rounded-lg p-4 ${
                          message.role === 'user'
                            ? 'bg-primary text-white'
                            : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                        }`}
                      >
                        <p className="whitespace-pre-wrap">{message.content}</p>
                        {message.relevant_use_cases &&
                          message.relevant_use_cases.length > 0 && (
                            <div className="mt-2 pt-2 border-t border-gray-300 dark:border-gray-600">
                              <p className="text-xs font-semibold mb-1 dark:text-gray-300">Relevant Use Cases:</p>
                              <ul className="text-xs list-disc list-inside dark:text-gray-400">
                                {message.relevant_use_cases.map((uc, i) => (
                                  <li key={i}>{uc}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                      </div>
                    </div>
                  ))
                )}

                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-4">
                      <div className="flex gap-2">
                        <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce delay-100"></div>
                        <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce delay-200"></div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Input */}
              <div className="border-t p-4 dark:border-gray-700">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask a question..."
                    className="flex-1 px-4 py-2 border dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent"
                    disabled={loading}
                  />
                  <button
                    onClick={handleQuery}
                    disabled={loading || !question.trim()}
                    className="bg-primary bg-indigo-600 dark:bg-indigo-500 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Send
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
}

export default Query;