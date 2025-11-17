// -----------------------------------------------------------------------------
// File: SessionHeader.jsx
// Description: Session header component for ReqEngine - displays current session
//              information, title, and navigation context across application pages.
// Author: Pradyumna Chacham
// Date: November 2025
// Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
// License: MIT License - see LICENSE file in the root directory.
// -----------------------------------------------------------------------------

import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import useSessionStore from '../../store/useSessionStore';
import { api } from '../../api/client';

function SessionHeader() {
  const location = useLocation();
  const { currentSessionId, sessionTitle, sessions } = useSessionStore();
  
  const displayTitle = currentSessionId 
    ? (sessionTitle || 'New Session')
    : 'New Chat Session';

  const navItems = [
    { 
      path: '/', 
      label: 'Chat', 
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      )
    },
    { 
      path: '/export', 
      label: 'Export', 
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
      )
    },
    { 
      path: '/query', 
      label: 'Query', 
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      )
    },
  ];

  return (
    <div className="bg-gray-50 border-b border-gray-200 px-6 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Session Title */}
        <div className="flex items-center gap-3">
          <span className="text-2xl"></span>
          <h2 className="text-lg font-semibold text-gray-900">
            {displayTitle}
          </h2>
        </div>
        {/* Session Controls */}
        <nav className="flex items-center gap-1">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition text-sm ${
                location.pathname === item.path
                  ? 'bg-indigo-100 text-indigo-700 font-medium'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              {item.icon}
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>
      </div>
    </div>
  );
}

export default SessionHeader;