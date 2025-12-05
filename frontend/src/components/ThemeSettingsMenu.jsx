import React, { useState, useRef, useEffect } from 'react';
import { toast } from 'react-toastify';

/**
 * Color palette options available for actors
 */
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

/**
 * Predefined list of actor types for use case coloring
 */
const ACTORS = [
  "user", "customer", "admin", "administrator", "manager", "employee",
  "staff", "member", "visitor", "guest", "buyer", "seller", "vendor",
  "supplier", "student", "teacher", "instructor", "patient", "doctor",
  "nurse", "system", "application", "platform"
];

/**
 * ColorPicker component to select a color for a given actor
 * @param {string} currentColor - Currently selected color
 * @param {function} onSelectColor - Callback when a color is selected
 * @param {string} actorName - Name of the actor being edited
 * @param {function} onClose - Callback to close the color picker
 */
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

/**
 * QuickModelSelector component for rapid switching of AI models
 */
const QuickModelSelector = () => {
  const [models, setModels] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchCurrentModel();
  }, []);

  /**
   * Fetch currently active model and available models
   */
  const fetchCurrentModel = async () => {
    try {
      const response = await fetch('http://localhost:8000/models', {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setModels(data);
      }
    } catch (error) {
      console.error('Error fetching model info:', error);
    }
  };

  /**
   * Switch model quickly
   * @param {string} type - Model type ('local' or 'api')
   * @param {string} model - Model option to activate
   */
  const handleQuickSwitch = async (type, model) => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/model', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          model_type: type,
          model_option: model
        })
      });

      const data = await response.json();

      if (response.ok) {
        toast.success('Model switched successfully');
        fetchCurrentModel();
      } else {
        toast.error(data.detail || 'Failed to switch model');
      }
    } catch (error) {
      toast.error('Failed to switch model');
    } finally {
      setLoading(false);
    }
  };

  if (!models) {
    return (
      <div className="text-sm text-gray-500 dark:text-gray-400">
        Loading models...
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {models.current?.type ? (
        <div className="flex items-center justify-between p-2 bg-green-100 dark:bg-green-900/30 rounded border border-green-300 dark:border-green-800">
          <div className="flex items-center gap-2">
            <span className="text-green-600 dark:text-green-400">🟢</span>
            <span className="text-sm font-medium text-green-900 dark:text-green-200">
              {models.current.name}
            </span>
          </div>
          <span className="text-xs text-green-700 dark:text-green-300 px-2 py-1 bg-green-200 dark:bg-green-800 rounded">
            {models.current.type}
          </span>
        </div>
      ) : (
        <div className="text-sm text-gray-500 dark:text-gray-400 p-2 text-center">
          No model active
        </div>
      )}

      {/* Quick switch buttons */}
      <div className="flex gap-2">
        {models.models.local && models.models.local[0] && (
          <button
            onClick={() => handleQuickSwitch('local', models.models.local[0])}
            disabled={loading || models.current?.name === models.models.local[0]}
            className="flex-1 text-xs px-3 py-2 bg-gray-200 dark:bg-gray-600 text-gray-900 dark:text-white rounded hover:bg-gray-300 dark:hover:bg-gray-500 transition disabled:opacity-50"
          >
            🖥️ Local
          </button>
        )}
        {models.models.api && Object.keys(models.models.api).length > 0 && (
          <button
            onClick={() => {
              const firstService = Object.keys(models.models.api)[0];
              const firstModel = models.models.api[firstService]?.models[0];
              if (firstModel) {
                handleQuickSwitch('api', firstModel);
              }
            }}
            disabled={loading}
            className="flex-1 text-xs px-3 py-2 bg-gray-200 dark:bg-gray-600 text-gray-900 dark:text-white rounded hover:bg-gray-300 dark:hover:bg-gray-500 transition disabled:opacity-50"
          >
            ☁️ API
          </button>
        )}
      </div>
    </div>
  );
};

/**
 * ModelSettingsPanel component for advanced model selection and API setup
 */
const ModelSettingsPanel = () => {
  const [models, setModels] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedType, setSelectedType] = useState('local');
  const [selectedModel, setSelectedModel] = useState('');
  const [selectedAPIService, setSelectedAPIService] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [showApiKeyInput, setShowApiKeyInput] = useState(false);

  useEffect(() => {
    fetchAvailableModels();
  }, []);

  /**
   * Fetch available models and set current selection
   */
  const fetchAvailableModels = async () => {
    try {
      const response = await fetch('http://localhost:8000/models', {
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error('Failed to fetch models');
      }

      const data = await response.json();
      setModels(data);

      if (data.current?.type) {
        setSelectedType(data.current.type);
        setSelectedModel(data.current.name);
        if (data.current.service) {
          setSelectedAPIService(data.current.service);
        }
      }
    } catch (error) {
      console.error('Error fetching models:', error);
      toast.error('Failed to load available models');
    }
  };

  /**
   * Setup API credentials for the selected API service
   */
  const handleSetupAPI = async () => {
    if (!selectedAPIService || !apiKey) {
      toast.error('Please select an API service and enter your API key');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/model/api', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          API: selectedAPIService,
          API_Key: apiKey
        })
      });

      const data = await response.json();

      if (response.ok) {
        toast.success(data.message);
        setShowApiKeyInput(false);
        setApiKey('');
        fetchAvailableModels();
      } else {
        toast.error(data.detail || 'Failed to set up API');
      }
    } catch (error) {
      console.error('Error setting up API:', error);
      toast.error('Failed to set up API credentials');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Select and activate a model
   */
  const handleSelectModel = async () => {
    if (!selectedModel) {
      toast.error('Please select a model');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/model', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          model_type: selectedType,
          model_option: selectedModel
        })
      });

      const data = await response.json();

      if (response.ok) {
        toast.success(data.message);
        if (data.message.includes('rate-limited')) {
          toast.warning('Consider adding your API key for better performance', {
            autoClose: 5000
          });
        }
        fetchAvailableModels();
      } else {
        toast.error(data.detail || 'Failed to activate model');
      }
    } catch (error) {
      console.error('Error selecting model:', error);
      toast.error('Failed to activate model');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Deactivate currently active model
   */
  const handleDeactivateModel = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/model', {
        method: 'DELETE',
        credentials: 'include'
      });

      const data = await response.json();

      if (response.ok) {
        toast.success(data.message);
        setSelectedModel('');
        fetchAvailableModels();
      } else {
        toast.error(data.detail || 'Failed to deactivate model');
      }
    } catch (error) {
      console.error('Error deactivating model:', error);
      toast.error('Failed to deactivate model');
    } finally {
      setLoading(false);
    }
  };

  if (!models) {
    return (
      <div className="p-4">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-3/4"></div>
          <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-1/2"></div>
          <div className="h-10 bg-gray-300 dark:bg-gray-600 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Current Model Status */}
      {models.current?.type && (
        <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-green-900 dark:text-green-200">
                🟢 Active Model
              </p>
              <p className="text-sm text-green-800 dark:text-green-300 mt-1">
                {models.current.name} ({models.current.type})
                {models.current.service && ` - ${models.current.service}`}
              </p>
              {!models.current.has_api_key && models.current.type === 'api' && (
                <p className="text-xs text-yellow-600 dark:text-yellow-400 mt-1">
                  ⚠️ Using rate-limited service. Add API key for better performance.
                </p>
              )}
            </div>
            <button
              onClick={handleDeactivateModel}
              disabled={loading}
              className="px-3 py-1 text-sm bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded hover:bg-red-200 dark:hover:bg-red-900/50 transition disabled:opacity-50"
            >
              Deactivate
            </button>
          </div>
        </div>
      )}

      {/* Model Type Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Model Type
        </label>
        <div className="flex gap-4">
          <button
            onClick={() => {
              setSelectedType('local');
              setSelectedModel('');
            }}
            className={`flex-1 p-3 border-2 rounded-lg transition ${
              selectedType === 'local'
                ? 'border-indigo-600 dark:border-indigo-400 bg-indigo-50 dark:bg-indigo-900/20'
                : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
            }`}
          >
            <div className="text-center">
              <p className="font-medium text-gray-900 dark:text-white">🖥️ Local Model</p>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                Run on your hardware
              </p>
            </div>
          </button>
          <button
            onClick={() => {
              setSelectedType('api');
              setSelectedModel('');
            }}
            className={`flex-1 p-3 border-2 rounded-lg transition ${
              selectedType === 'api'
                ? 'border-indigo-600 dark:border-indigo-400 bg-indigo-50 dark:bg-indigo-900/20'
                : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
            }`}
          >
            <div className="text-center">
              <p className="font-medium text-gray-900 dark:text-white">☁️ Cloud API</p>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                Use external services
              </p>
            </div>
          </button>
        </div>
      </div>

      {/* Local Models */}
      {selectedType === 'local' && (
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Select Local Model
          </label>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="w-full px-4 py-2 border dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="">Choose a model...</option>
            {models.models.local.map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* API Models */}
      {selectedType === 'api' && (
        <div className="space-y-4">
          {/* API Service Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              API Service
            </label>
            <select
              value={selectedAPIService}
              onChange={(e) => {
                setSelectedAPIService(e.target.value);
                setSelectedModel('');
              }}
              className="w-full px-4 py-2 border dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">Choose a service...</option>
              {models.hosts.api.map((service) => (
                <option key={service} value={service}>
                  {models.models.api[service]?.name || service}
                </option>
              ))}
            </select>
          </div>

          {/* API Key Setup */}
          {selectedAPIService && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  API Key (Optional)
                </label>
                <button
                  onClick={() => setShowApiKeyInput(!showApiKeyInput)}
                  className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline"
                >
                  {showApiKeyInput ? 'Hide' : 'Add API Key'}
                </button>
              </div>
              
              {showApiKeyInput && (
                <div className="space-y-2">
                  <input
                    type="password"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="Enter your API key"
                    className="w-full px-4 py-2 border dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                  <button
                    onClick={handleSetupAPI}
                    disabled={loading || !apiKey}
                    className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? '⏳ Setting up...' : '🔑 Save API Key'}
                  </button>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    💡 Your API key is stored securely and never shared
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Model Selection */}
          {selectedAPIService && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Select Model
              </label>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="w-full px-4 py-2 border dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">Choose a model...</option>
                {models.models.api[selectedAPIService]?.models.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      )}

      {/* Activate Button */}
      <button
        onClick={handleSelectModel}
        disabled={loading || !selectedModel || models.current?.name === selectedModel}
        className="w-full px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium"
      >
        {loading ? '⏳ Activating...' : '✨ Activate Model'}
      </button>

      {/* Info Box */}
      <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
        <p className="text-sm text-blue-800 dark:text-blue-300">
          💡 <strong>Tip:</strong> Local models run on your hardware and don't require API keys. 
          Cloud API models offer better performance but may have usage limits without an API key.
        </p>
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
        title="Settings"
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
            className="w-[700px] max-h-[85vh] bg-white dark:bg-gray-800 rounded-lg shadow-2xl border border-gray-200 dark:border-gray-700 flex flex-col"
          >
            {/* Header */}
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Settings</h3>
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
                ⚙️ General
              </button>
              <button
                onClick={() => setActiveTab('colors')}
                className={`flex-1 px-6 py-4 text-sm font-medium transition ${
                  activeTab === 'colors'
                    ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600 dark:border-indigo-400 bg-indigo-50 dark:bg-indigo-900/20'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700/50'
                }`}
              >
                🎨 Actor Colors
              </button>
              <button
                onClick={() => setActiveTab('model')}
                className={`flex-1 px-6 py-4 text-sm font-medium transition ${
                  activeTab === 'model'
                    ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600 dark:border-indigo-400 bg-indigo-50 dark:bg-indigo-900/20'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700/50'
                }`}
              >
                🤖 AI Model
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
                          stakeholderColorMode ? 'translate-x-8' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>

                  {/* Quick Model Selector */}
                  <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <svg className="w-6 h-6 text-indigo-600 dark:text-indigo-400" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">AI Model</p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            Quick model selection
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => setActiveTab('model')}
                        className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline"
                      >
                        Advanced →
                      </button>
                    </div>
                    <QuickModelSelector />
                  </div>

                  <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                    <p className="text-sm text-blue-800 dark:text-blue-300">
                      💡 <strong>Tip:</strong> Enable actor color coding to visually distinguish different user types in your use cases. Customize colors in the Actor Colors tab.
                    </p>
                  </div>
                </div>
              )}

              {activeTab === 'colors' && (
                <div className="space-y-4">
                  {/* Toggle for Color Mode */}
                  <div className="flex items-center justify-between p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg">
                    <div className="flex items-center gap-3">
                      <svg className="w-5 h-5 text-purple-600 dark:text-purple-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M4 2a2 2 0 00-2 2v11a3 3 0 106 0V4a2 2 0 00-2-2H4zm1 14a1 1 0 100-2 1 1 0 000 2zm5-1.757l4.9-4.9a2 2 0 000-2.828L13.485 5.1a2 2 0 00-2.828 0L10 5.757v8.486zM16 18H9.071l6-6H16a2 2 0 012 2v2a2 2 0 01-2 2z" clipRule="evenodd" />
                      </svg>
                      <div>
                        <p className="font-medium text-purple-900 dark:text-purple-200">Color Coding Active</p>
                        <p className="text-xs text-purple-700 dark:text-purple-300">
                          {stakeholderColorMode ? 'Use case cards will be colored by actor type' : 'Use case cards will use default styling'}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={toggleStakeholderColorMode}
                      className={`relative inline-flex h-7 w-14 items-center rounded-full transition ${
                        stakeholderColorMode ? 'bg-purple-600' : 'bg-gray-300'
                      }`}
                    >
                      <span
                        className={`inline-block h-5 w-5 transform rounded-full bg-white transition shadow-md ${
                          stakeholderColorMode ? 'translate-x-8' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>

                  {/* Color customization section */}
                  <div className={stakeholderColorMode ? '' : 'opacity-50 pointer-events-none'}>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                      {stakeholderColorMode 
                        ? 'Click on a color box to customize the color for each actor type:' 
                        : 'Enable color coding above to customize actor colors'}
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
                            onClick={() => stakeholderColorMode && setColorPickerOpen(actor)}
                            className="w-8 h-8 rounded-lg hover:scale-110 transition-transform shadow-md border border-gray-300 dark:border-gray-600 flex-shrink-0"
                            style={{ backgroundColor: getColorStyle(stakeholderColors[actor] || 'gray') }}
                            title={stakeholderColorMode ? `Change ${actor} color` : 'Enable color coding to customize'}
                            disabled={!stakeholderColorMode}
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'model' && (
                <ModelSettingsPanel />
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
