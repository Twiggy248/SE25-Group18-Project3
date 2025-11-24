import React, { useState, useRef, useEffect } from 'react';

// Color palette options
const COLOR_OPTIONS = [
  { name: 'Blue', value: 'blue', color: '#3b82f6' },
  { name: 'Purple', value: 'purple', color: '#a855f7' },
  { name: 'Green', value: 'green', color: '#22c55e' },
  { name: 'Orange', value: 'orange', color: '#f97316' },
  { name: 'Red', value: 'red', color: '#ef4444' },
  { name: 'Pink', value: 'pink', color: '#ec4899' },
  { name: 'Yellow', value: 'yellow', color: '#eab308' },
  { name: 'Indigo', value: 'indigo', color: '#6366f1' },
  { name: 'Teal', value: 'teal', color: '#14b8a6' },
  { name: 'Cyan', value: 'cyan', color: '#06b6d4' },
  { name: 'Gray', value: 'gray', color: '#6b7280' }
];

const ACTORS = [
  "user", "customer", "admin", "administrator", "manager", "employee",
  "staff", "member", "visitor", "guest", "buyer", "seller", "vendor",
  "supplier", "student", "teacher", "instructor", "patient", "doctor",
  "nurse", "system", "application", "platform"
];

const ColorPicker = ({ currentColor, onSelectColor, actorName, onClose }) => {
  const pickerRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (pickerRef.current && !pickerRef.current.contains(event.target)) {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black bg-opacity-50">
      <div
        ref={pickerRef}
        className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl border border-gray-200 dark:border-gray-700 p-6 max-w-md"
      >
        <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 capitalize">
          Choose color for {actorName}
        </h4>
        <div className="grid grid-cols-4 gap-3">
          {COLOR_OPTIONS.map((color) => (
            <button
              key={color.value}
              onClick={() => {
                onSelectColor(color.value);
                onClose();
              }}
              className={`group relative h-12 rounded-lg hover:scale-110 transition-transform border-2 ${
                currentColor === color.value ? 'ring-4 ring-gray-900 dark:ring-white border-white' : 'border-gray-300 dark:border-gray-600'
              }`}
              style={{ backgroundColor: color.color }}
              title={color.name}
            >
              <span className="absolute -top-8 left-1/2 -translate-x-1/2 bg-gray-900 dark:bg-gray-700 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10">
                {color.name}
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

const ThemeSettingsMenu = ({ darkMode, stakeholderColorMode, toggleDarkMode, toggleStakeholderColorMode, stakeholderColors = {}, updateStakeholderColor }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('general');
  const [colorPickerOpen, setColorPickerOpen] = useState(null);
  const menuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      // Don't close if color picker is open
      if (colorPickerOpen) return;
      
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, colorPickerOpen]);

  const getColorStyle = (colorName) => {
    const colorMap = {
      blue: '#3b82f6',
      purple: '#a855f7',
      green: '#22c55e',
      orange: '#f97316',
      red: '#ef4444',
      pink: '#ec4899',
      yellow: '#eab308',
      indigo: '#6366f1',
      teal: '#14b8a6',
      cyan: '#06b6d4',
      gray: '#6b7280'
    };
    return colorMap[colorName] || '#6b7280';
  };

  return (
    <>
      {/* Menu Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition"
        title="Theme settings"
      >
        <svg className="w-5 h-5 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <span className="text-sm font-medium text-gray-900 dark:text-gray-100">Settings</span>
      </button>

      {/* Backdrop & Centered Modal */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div
            ref={menuRef}
            className="w-[600px] max-h-[80vh] bg-white dark:bg-gray-800 rounded-lg shadow-2xl border border-gray-200 dark:border-gray-700 flex flex-col"
          >
            {/* Header */}
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Theme Settings</h3>
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-gray-200 dark:border-gray-700">
              <button
                onClick={() => setActiveTab('general')}
                className={`flex-1 px-6 py-4 text-sm font-medium transition ${
                  activeTab === 'general'
                    ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600 dark:border-indigo-400 bg-indigo-50 dark:bg-indigo-900/20'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700/50'
                }`}
              >
                General
              </button>
              <button
                onClick={() => setActiveTab('colors')}
                className={`flex-1 px-6 py-4 text-sm font-medium transition ${
                  activeTab === 'colors'
                    ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600 dark:border-indigo-400 bg-indigo-50 dark:bg-indigo-900/20'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700/50'
                }`}
              >
                Actor Colors
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {activeTab === 'general' && (
                <div className="space-y-6">
                  {/* Dark Mode Toggle */}
                  <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex items-center gap-4">
                      {darkMode ? (
                        <svg className="w-6 h-6 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
                        </svg>
                      ) : (
                        <svg className="w-6 h-6 text-indigo-600" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                        </svg>
                      )}
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">Dark Mode</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {darkMode ? 'Currently in dark mode' : 'Currently in light mode'}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={toggleDarkMode}
                      className={`relative inline-flex h-7 w-14 items-center rounded-full transition ${
                        darkMode ? 'bg-indigo-600' : 'bg-gray-300'
                      }`}
                    >
                      <span
                        className={`inline-block h-5 w-5 transform rounded-full bg-white transition shadow-md ${
                          darkMode ? 'translate-x-8' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>

                  {/* Stakeholder Color Mode Toggle */}
                  <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex items-center gap-4">
                      <svg className="w-6 h-6 text-purple-600 dark:text-purple-400" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
                      </svg>
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">Actor Color Coding</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {stakeholderColorMode ? 'Colors enabled' : 'Colors disabled'}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={toggleStakeholderColorMode}
                      className={`relative inline-flex h-7 w-14 items-center rounded-full transition ${
                        stakeholderColorMode ? 'bg-indigo-600' : 'bg-gray-300'
                      }`}
                    >
                      <span
                        className={`inline-block h-5 w-5 transform rounded-full bg-white transition shadow-md ${
                          stakeholderColorMode ? 'translate-x-8' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>

                  <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                    <p className="text-sm text-blue-800 dark:text-blue-300">
                      💡 <strong>Tip:</strong> Enable actor color coding to visually distinguish different user types in your use cases. Customize colors in the Actor Colors tab.
                    </p>
                  </div>
                </div>
              )}

              {activeTab === 'colors' && (
                <div className="space-y-2">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    Click on a color box to customize the color for each actor type:
                  </p>
                  <div className="grid grid-cols-2 gap-3">
                    {ACTORS.map((actor) => (
                      <div
                        key={actor}
                        className="flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition"
                      >
                        <span className="text-sm font-medium text-gray-900 dark:text-white capitalize select-none">
                          {actor}
                        </span>
                        <button
                          onClick={() => setColorPickerOpen(actor)}
                          className="w-8 h-8 rounded-lg hover:scale-110 transition-transform shadow-md border border-gray-300 dark:border-gray-600 flex-shrink-0"
                          style={{ backgroundColor: getColorStyle(stakeholderColors[actor] || 'gray') }}
                          title={`Change ${actor} color`}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Color Picker Modal */}
      {colorPickerOpen && (
        <ColorPicker
          currentColor={stakeholderColors[colorPickerOpen] || 'gray'}
          onSelectColor={(color) => updateStakeholderColor(colorPickerOpen, color)}
          actorName={colorPickerOpen}
          onClose={() => setColorPickerOpen(null)}
        />
      )}
    </>
  );
};

export default ThemeSettingsMenu;