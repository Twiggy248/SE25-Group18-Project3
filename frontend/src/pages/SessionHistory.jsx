// -----------------------------------------------------------------------------
// File: SessionHistory.jsx
// Description: Session history page for ReqEngine - displays all user sessions
//              with navigation, management, and historical overview functionality.
// Author: Pradyumna Chacham
// Date: November 2025
// Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
// License: MIT License - see LICENSE file in the root directory.
// -----------------------------------------------------------------------------

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { toast } from 'react-toastify';
import LoadingSpinner from '../components/LoadingSpinner';
import { formatDate } from '../utils/formatters';

function SessionHistory() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const response = await api.getSessions();
      setSessions(response.data.sessions);
    } catch (error) {
      toast.error('Failed to load sessions');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (sessionId) => {
    if (!window.confirm('Are you sure you want to delete this session?')) {
      return;
    }

    try {
      await api.deleteSession(sessionId);
      toast.success('Session deleted successfully');
      loadSessions(); // Reload
    } catch (error) {
      toast.error('Failed to delete session');
    }
  };

  const handleViewDetails = (sessionId) => {
    navigate(`/sessions/${sessionId}`);
  };

  if (loading) return <LoadingSpinner message="Loading sessions..." />;

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Session History 📚
          </h1>
          <p className="text-gray-600">
            View and manage all your requirement sessions
          </p>
        </div>

        {sessions.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border p-12 text-center">
            <p className="text-gray-500 text-lg mb-4">No sessions yet</p>
            <button
              onClick={() => navigate('/extraction')}
              className="bg-primary text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition"
            >
              Create Your First Session
            </button>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Session Title
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {sessions.map((session) => (
                    <tr key={session.session_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-gray-900">
                          {session.session_title || session.project_context || 'Untitled Session'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => handleViewDetails(session.session_id)}
                          className="text-primary hover:text-indigo-900 mr-4"
                        >
                          View
                        </button>
                        <button
                          onClick={() => handleDelete(session.session_id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default SessionHistory;