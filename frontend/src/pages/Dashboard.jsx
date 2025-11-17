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
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Welcome to ReqEngine 🚀
          </h1>
          <p className="text-gray-600">
            Transform unstructured requirements into structured use cases with AI
          </p>
        </div>

        <button onClick={() => apiClient.post("/auth/logout").then(() => window.location = "/login")}
        className='text-sm text-gray-600 hover:text-gray-900'>
          Logout
        </button>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Total Sessions</p>
                <p className="text-3xl font-bold text-gray-900">{stats.totalSessions}</p>
              </div>
              <div className="text-4xl">📚</div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Use Cases Generated</p>
                <p className="text-3xl font-bold text-gray-900">{stats.totalUseCases}</p>
              </div>
              <div className="text-4xl">✨</div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Quick Action</p>
                <Link
                  to="/extraction"
                  className="text-primary hover:underline font-medium"
                >
                  Start New Extraction →
                </Link>
              </div>
              <div className="text-4xl">🎯</div>
            </div>
          </div>
        </div>

        {/* Recent Sessions */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="p-6 border-b">
            <h2 className="text-2xl font-bold text-gray-900">Recent Sessions</h2>
          </div>

          <div className="p-6">
            {sessions.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 mb-4">No sessions yet</p>
                <Link
                  to="/extraction"
                  className="bg-primary text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition inline-block"
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
                    className="block p-4 border rounded-lg hover:border-primary hover:bg-indigo-50 transition"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-semibold text-gray-900">
                          {session.session_title || session.project_context || 'Untitled Session'}
                        </h3>
                        <p className="text-xs text-gray-400 mt-1">
                          Last active: {formatDate(session.last_active)}
                        </p>
                      </div>
                      <span className="text-xs font-mono text-gray-400">
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