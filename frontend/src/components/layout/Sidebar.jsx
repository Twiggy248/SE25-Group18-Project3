// -----------------------------------------------------------------------------
// File: Sidebar.jsx
// Description: Sidebar navigation component for ReqEngine - provides session
//              management, navigation menu, and quick access to main features.
// Author: Pradyumna Chacham
// Date: November 2025
// Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
// License: MIT License - see LICENSE file in the root directory.
// -----------------------------------------------------------------------------

import React, { useEffect, useState, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { api } from '../../api/client';
import useSessionStore from '../../store/useSessionStore';
import { formatDate } from '../../utils/formatters';

function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { currentSessionId, setCurrentSession, sessions, setSessions } = useSessionStore();
  const [loading, setLoading] = useState(true);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [sidebarWidth, setSidebarWidth] = useState(256); // 256px = w-64
  const [isResizing, setIsResizing] = useState(false);
  const sidebarRef = useRef(null);
  const minWidth = 200;
  const maxWidth = 500;
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await api.me(); 
        if (res.data && res.data.authenticated) {
          setAuthenticated(true);
        } else {
          setAuthenticated(false);
        }
      } catch (err) {
        setAuthenticated(false);
      }
    };
  
    checkAuth();
  }, []);  

  useEffect(() => {
    const initializeSessions = async () => {
      await loadSessions();
      // Don't automatically select a session
    };
    initializeSessions();
  }, []);

  useEffect(() => {
    if (isResizing) {
      const handleMouseMove = (e) => {
        const newWidth = e.clientX;
        if (newWidth >= minWidth && newWidth <= maxWidth) {
          setSidebarWidth(newWidth);
        }
      };

      const handleMouseUp = () => {
        setIsResizing(false);
      };

      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);

      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isResizing]);

  const loadSessions = async () => {
    try {
      const response = await api.getSessions();
      setSessions(response.data.sessions);
    } catch (error) {
      console.log('Sessions not loaded');
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = () => {
    setCurrentSession(null);
    navigate('/');
  };

  const handleSelectSession = (session) => {
    setCurrentSession(session.session_id, session.session_title || '');
    navigate('/');
  };

  const handleDeleteSession = async (sessionId, e) => {
    e.stopPropagation();
    if (!window.confirm('Delete this session?')) return;
    
    try {
      await api.deleteSession(sessionId);
      setSessions(sessions.filter(s => s.session_id !== sessionId));
      if (currentSessionId === sessionId) {
        setCurrentSession(null);
      }
    } catch (error) {
      console.log('Delete failed');
    }
  };

  const handleRenameSession = async (sessionId, e) => {
    e.stopPropagation();

    const newTitle = window.prompt("Enter new session title: ");
    if(!newTitle || !newTitle.trim()) return; 

    try{
      await api.renameSession(sessionId, newTitle.trim());

      setSessions(
        sessions.map(s => 
          s.session_id === sessionId
          ? {...s, session_title: newTitle.trim()}
          : s
        )
      );

      if(currentSessionId === sessionId){
        setCurrentSession(sessionId, newTitle.trim());
      }
    }catch(err){
      console.log("Renaming failed :(", err);
    }
  }

  const startResizing = () => {
    setIsResizing(true);
  };

  if (isCollapsed) {
    return (
      <>
        <aside className="w-16 bg-gray-900 text-white flex flex-col h-screen relative">
          {/* Collapsed - just show toggle button */}
          <div className="p-4 flex justify-center">
            <button
              onClick={() => setIsCollapsed(false)}
              className="p-2 hover:bg-gray-800 rounded-lg transition"
              title="Expand sidebar"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </aside>
      </>
    );
  }

  return (
    <>
      <aside 
        ref={sidebarRef}
        style={{ width: `${sidebarWidth}px` }}
        className="bg-gray-900 text-white flex flex-col h-screen relative transition-all duration-150"
      >
        {/* Header with ReqEngine and Toggle */}
        <div className="p-4 flex items-center justify-between border-b border-gray-700">
          <span className="text-lg font-bold">ReqEngine</span>
          <button
            onClick={() => setIsCollapsed(true)}
            className="p-2 hover:bg-gray-800 rounded-lg transition"
            title="Collapse sidebar"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        </div>

        {/* New Chat Button */}
        <div className="p-4">
          <button
            onClick={handleNewChat}
            className="w-full flex items-center justify-center gap-2 bg-gray-800 hover:bg-gray-700 px-4 py-3 rounded-lg transition font-medium"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>New Chat</span>
          </button>
        </div>

        {/* Session History */}
        <div className="flex-1 overflow-y-auto px-2">
          <div className="text-xs text-gray-400 px-3 py-2 font-semibold uppercase tracking-wider">
            Recent Sessions
          </div>
          
          {loading ? (
            <div className="px-3 py-2 text-sm text-gray-400">Loading...</div>
          ) : sessions.length === 0 ? (
            <div className="px-3 py-2 text-sm text-gray-400">No sessions yet</div>
          ) : (
            <div className="space-y-1">
              {sessions.map((session) => (
                <div
                  key={session.session_id}
                  onClick={() => handleSelectSession(session)}
                  className={`group relative px-3 py-2 rounded-lg cursor-pointer transition ${
                    currentSessionId === session.session_id
                      ? 'bg-gray-700'
                      : 'hover:bg-gray-800'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {session.session_title || session.project_context || `Session ${session.session_id.slice(0, 8)}`}
                      </p>
                    </div>
                    <button
                      onClick={(e) => handleDeleteSession(session.session_id, e)}
                      className="opacity-0 group-hover:opacity-100 ml-2 p-1.5 hover:bg-red-600 rounded transition flex-shrink-0"
                      title="Delete session"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>

                    <button
                      onClick = {(e) => handleRenameSession(session.session_id, e)}
                      className='opacity-0 group-hover:opacity-100 ml-2 p-1.5 hover:bg-blue-600 rounded transition flex-shrink-0'
                      title='Rename'
                    >
                      <svg className = 'w-4 h-4' fill='none' stroke = 'currentColor' viewBox='0 0 24 24'>
                        <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M15.232 5.232l3.536 3.536M9 11l6.232-6.232a2 2 0 112.828 2.828L11.828 13.828 9 14l.172-1.828z'/>
                      </svg>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Bottom Info */}
        <div className="p-4 border-t border-gray-700 space-y-3">
          {/* Logout Button */}
          {authenticated && (
            <button
              onClick={async () => {
                try{
                  await api.logout(); 
                  useSessionStore.getState().setCurrentSession(null);
                  useSessionStore.getState().setSessions([]);
                  window.location.reload();
                } catch (err){
                  console.log('Logout failed', err);
                }
              }}
              className='w-full flex items-center justify-center gap-2 bg-red-600 hover:bg-red-500 px-4 py-2 rounded-lg transition font-medium'
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1m0-10V5" />
              </svg>
              <span>Logout</span>
            </button>
          )}
          <div className="text-xs text-gray-400">
            {currentSessionId && (
              <div className="mb-2 flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-gray-500">Active session</span>
              </div>
            )}
            <div className="text-gray-500">ReqEngine v1.0</div>
          </div>
        </div>

        {/* Resize Handle */}
        <div
          onMouseDown={startResizing}
          className="absolute right-0 top-0 bottom-0 w-1 cursor-col-resize hover:bg-blue-500 transition-colors z-10"
          style={{ userSelect: 'none' }}
        />
      </aside>

      {/* Overlay during resizing */}
      {isResizing && (
        <div className="fixed inset-0 z-50 cursor-col-resize" style={{ userSelect: 'none' }} />
      )}
    </>
  );
}

export default Sidebar;
