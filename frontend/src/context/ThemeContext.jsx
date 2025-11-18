// -----------------------------------------------------------------------------
// File: ThemeContext.jsx
// Description: Theme management context for ReqEngine - provides dark mode
//              and stakeholder-based color coding functionality.
// Author: Pradyumna Chacham
// Date: November 2025
// Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
// License: MIT License - see LICENSE file in the root directory.
// -----------------------------------------------------------------------------

import React, { createContext, useContext, useState, useEffect } from 'react';

// Theme Context
const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

// Stakeholder color mapping
const STAKEHOLDER_COLORS = {
  'customer': {
    light: { bg: 'bg-blue-50', border: 'border-blue-300', text: 'text-blue-900', badge: 'bg-blue-200 text-blue-800' },
    dark: { bg: 'bg-gray-800', border: 'border-blue-500', text: 'text-blue-300', badge: 'bg-blue-900 text-blue-200' }
  },
  'admin': {
    light: { bg: 'bg-purple-50', border: 'border-purple-300', text: 'text-purple-900', badge: 'bg-purple-200 text-purple-800' },
    dark: { bg: 'bg-gray-800', border: 'border-purple-500', text: 'text-purple-300', badge: 'bg-purple-900 text-purple-200' }
  },
  'user': {
    light: { bg: 'bg-green-50', border: 'border-green-300', text: 'text-green-900', badge: 'bg-green-200 text-green-800' },
    dark: { bg: 'bg-gray-800', border: 'border-green-500', text: 'text-green-300', badge: 'bg-green-900 text-green-200' }
  },
  'system': {
    light: { bg: 'bg-orange-50', border: 'border-orange-300', text: 'text-orange-900', badge: 'bg-orange-200 text-orange-800' },
    dark: { bg: 'bg-gray-800', border: 'border-orange-500', text: 'text-orange-300', badge: 'bg-orange-900 text-orange-200' }
  },
  'manager': {
    light: { bg: 'bg-red-50', border: 'border-red-300', text: 'text-red-900', badge: 'bg-red-200 text-red-800' },
    dark: { bg: 'bg-gray-800', border: 'border-red-500', text: 'text-red-300', badge: 'bg-red-900 text-red-200' }
  },
  'default': {
    light: { bg: 'bg-gray-50', border: 'border-gray-300', text: 'text-gray-900', badge: 'bg-gray-200 text-gray-800' },
    dark: { bg: 'bg-gray-800', border: 'border-gray-600', text: 'text-gray-100', badge: 'bg-gray-700 text-gray-200' }
  }
};

export const ThemeProvider = ({ children }) => {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : false;
  });
  
  const [stakeholderColorMode, setStakeholderColorMode] = useState(() => {
    const saved = localStorage.getItem('stakeholderColorMode');
    return saved ? JSON.parse(saved) : false;
  });

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  useEffect(() => {
    localStorage.setItem('stakeholderColorMode', JSON.stringify(stakeholderColorMode));
  }, [stakeholderColorMode]);

  const getStakeholderColor = (stakeholders) => {
    if (!stakeholderColorMode || !stakeholders || stakeholders.length === 0) {
      return STAKEHOLDER_COLORS.default[darkMode ? 'dark' : 'light'];
    }

    // Get primary stakeholder (first in array) and normalize
    const primaryStakeholder = stakeholders[0].toLowerCase().trim();
    
    // Find matching color scheme
    for (const [key, colors] of Object.entries(STAKEHOLDER_COLORS)) {
      if (primaryStakeholder.includes(key)) {
        return colors[darkMode ? 'dark' : 'light'];
      }
    }
    
    return STAKEHOLDER_COLORS.default[darkMode ? 'dark' : 'light'];
  };

  const toggleDarkMode = () => setDarkMode(prev => !prev);
  const toggleStakeholderColorMode = () => setStakeholderColorMode(prev => !prev);

  return (
    <ThemeContext.Provider value={{
      darkMode,
      stakeholderColorMode,
      toggleDarkMode,
      toggleStakeholderColorMode,
      getStakeholderColor
    }}>
      {children}
    </ThemeContext.Provider>
  );
};

// Theme Toggle Component
export const ThemeControls = () => {
  const { darkMode, stakeholderColorMode, toggleDarkMode, toggleStakeholderColorMode } = useTheme();

  return (
    <div className="flex items-center gap-4">
      {/* Dark Mode Toggle */}
      <button
        onClick={toggleDarkMode}
        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition"
        title="Toggle dark mode"
      >
        {darkMode ? (
          <>
            <svg className="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
            </svg>
            <span className="text-sm font-medium text-gray-900 dark:text-gray-100">Light</span>
          </>
        ) : (
          <>
            <svg className="w-5 h-5 text-indigo-600" fill="currentColor" viewBox="0 0 20 20">
              <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
            </svg>
            <span className="text-sm font-medium text-gray-900 dark:text-gray-100">Dark</span>
          </>
        )}
      </button>

      {/* Stakeholder Color Mode Toggle */}
      <button
        onClick={toggleStakeholderColorMode}
        className={`flex items-center gap-2 px-3 py-2 rounded-lg transition ${
          stakeholderColorMode 
            ? 'bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300' 
            : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300'
        } hover:opacity-80`}
        title="Toggle stakeholder colors"
      >
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
        </svg>
        <span className="text-sm font-medium">
          {stakeholderColorMode ? 'Stakeholder Colors' : 'Default Colors'}
        </span>
      </button>
    </div>
  );
};

export default ThemeProvider;