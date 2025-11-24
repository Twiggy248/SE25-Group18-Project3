// -----------------------------------------------------------------------------
// File: Dashboard.jsx
// Description: Dashboard page component for ReqEngine - displays session
//              overview, statistics, and navigation to main application features.
// Author: Pradyumna Chacham
// Date: November 2025
// Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
// License: MIT License - see LICENSE file in the root directory.
// -----------------------------------------------------------------------------

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import { toast } from 'react-toastify';
import LoadingSpinner from '../components/LoadingSpinner';
import { formatDate } from '../utils/formatters';
import { ThemeControls } from '../context/ThemeContext';

function Dashboard() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalSessions: 0,
    totalUseCases: 0,
  });

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const response = await api.getSessions();
      setSessions(response.data.sessions);
      setStats({
        totalSessions: response.data.sessions.length,
        totalUseCases: 0, // You can calculate this if needed
      });
    } catch (error) {
      toast.error('Failed to load sessions');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading dashboard..." />;

  return (
    <div className="p-8 bg-gray-50 dark:bg-gray-900 min-h-screen transition-colors">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                Welcome to ReqEngine 🚀
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Transform unstructured requirements into structured use cases with AI
              </p>
            </div>
          </div>
          <button 
            onClick={() => apiClient.post("/auth/logout").then(() => window.location = "/login")}
            className='text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 transition-colors'
          >
            Logout
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 transition-colors">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 dark:text-gray-400 text-sm">Total Sessions</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.totalSessions}</p>
              </div>
              <div className="text-4xl">📚</div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 transition-colors">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 dark:text-gray-400 text-sm">Use Cases Generated</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.totalUseCases}</p>
              </div>
              <div className="text-4xl">✨</div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 transition-colors">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 dark:text-gray-400 text-sm">Quick Action</p>
                <Link
                  to="/extraction"
                  className="text-indigo-600 dark:text-indigo-400 hover:underline font-medium"
                >
                  Start New Extraction →
                </Link>
              </div>
              <div className="text-4xl">🎯</div>
            </div>
          </div>
        </div>

        {/* Recent Sessions */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 transition-colors">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Recent Sessions</h2>
          </div>

          <div className="p-6">
            {sessions.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 dark:text-gray-400 mb-4">No sessions yet</p>
                <Link
                  to="/extraction"
                  className="bg-indigo-600 dark:bg-indigo-500 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 dark:hover:bg-indigo-600 transition-colors inline-block"
                >
                  Create Your First Session
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {sessions.slice(0, 5).map((session) => (
                  <Link
                    key={session.session_id}
                    to={`/sessions/${session.session_id}`}
                    className="block p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-indigo-500 dark:hover:border-indigo-400 hover:bg-indigo-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-semibold text-gray-900 dark:text-white">
                          {session.session_title || session.project_context || 'Untitled Session'}
                        </h3>
                        <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                          Last active: {formatDate(session.last_active)}
                        </p>
                      </div>
                      <span className="text-xs font-mono text-gray-400 dark:text-gray-500">
                        {session.session_id.substring(0, 8)}
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;