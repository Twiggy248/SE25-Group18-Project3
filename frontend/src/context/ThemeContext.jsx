import React, { createContext, useContext, useState, useEffect } from 'react';
import ThemeSettingsMenu from '../components/ThemeSettingsMenu';

// Theme Context
const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

// Default actor colors
const DEFAULT_ACTOR_COLORS = {
  'customer': 'blue',
  'admin': 'purple',
  'administrator': 'purple',
  'user': 'green',
  'system': 'orange',
  'application': 'orange',
  'platform': 'orange',
  'manager': 'red',
  'employee': 'teal',
  'staff': 'teal',
  'member': 'cyan',
  'visitor': 'gray',
  'guest': 'gray',
  'buyer': 'indigo',
  'seller': 'pink',
  'vendor': 'pink',
  'supplier': 'pink',
  'student': 'yellow',
  'teacher': 'indigo',
  'instructor': 'indigo',
  'patient': 'blue',
  'doctor': 'red',
  'nurse': 'teal'
};

// API client for user preferences
const API_BASE_URL = 'http://localhost:8000';

const saveUserPreferences = async (preferences) => {
  try {
    const response = await fetch(`${API_BASE_URL}/user/preferences`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(preferences),
    });
    
    if (!response.ok) {
      throw new Error('Failed to save preferences');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error saving preferences:', error);
    throw error;
  }
};

const loadUserPreferences = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/user/preferences`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });
    
    if (!response.ok) {
      return null;
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error loading preferences:', error);
    return null;
  }
};

// Generate actual color values (NOT Tailwind classes)
const getColorStyles = (colorName, darkMode) => {
  const colorMap = {
    blue: { light: '#3b82f6', dark: '#60a5fa' },
    purple: { light: '#a855f7', dark: '#c084fc' },
    green: { light: '#22c55e', dark: '#4ade80' },
    orange: { light: '#f97316', dark: '#fb923c' },
    red: { light: '#ef4444', dark: '#f87171' },
    pink: { light: '#ec4899', dark: '#f472b6' },
    yellow: { light: '#eab308', dark: '#facc15' },
    indigo: { light: '#6366f1', dark: '#818cf8' },
    teal: { light: '#14b8a6', dark: '#2dd4bf' },
    cyan: { light: '#06b6d4', dark: '#22d3ee' },
    gray: { light: '#6b7280', dark: '#9ca3af' }
  };

  const color = colorMap[colorName] || colorMap.gray;
  const mainColor = darkMode ? color.dark : color.light;
  
  return {
    // Card background - subtle tint
    backgroundColor: darkMode ? '#1f2937' : `${mainColor}0d`,
    // Border color - full opacity
    borderColor: mainColor,
    // Text color - full opacity for readability
    textColor: mainColor,
    // Badge background - semi-transparent
    badgeBackgroundColor: darkMode ? `${mainColor}40` : `${mainColor}26`,
    // Badge text - full opacity
    badgeTextColor: mainColor,
    // Raw color for other uses
    rawColor: mainColor,
    // Tailwind classes for compatibility
    classes: {
      bg: darkMode ? 'bg-gray-800' : 'bg-white',
      text: darkMode ? 'text-gray-100' : 'text-gray-900',
      border: 'border-2',
    }
  };
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

  const [stakeholderColors, setStakeholderColors] = useState(() => {
    const saved = localStorage.getItem('stakeholderColors');
    return saved ? JSON.parse(saved) : DEFAULT_ACTOR_COLORS;
  });

  const [preferencesLoaded, setPreferencesLoaded] = useState(false);

  // Load user preferences from API on mount
  useEffect(() => {
    const loadPreferences = async () => {
      try {
        const preferences = await loadUserPreferences();
        if (preferences) {
          if (preferences.darkMode !== undefined) {
            setDarkMode(preferences.darkMode);
          }
          if (preferences.stakeholderColorMode !== undefined) {
            setStakeholderColorMode(preferences.stakeholderColorMode);
          }
          if (preferences.stakeholderColors) {
            setStakeholderColors(preferences.stakeholderColors);
          }
          console.log('✅ Loaded preferences from API');
        }
      } catch (error) {
        console.log('Using local preferences (not authenticated or error)');
      } finally {
        setPreferencesLoaded(true);
      }
    };

    loadPreferences();
  }, []);

  // Save to localStorage and apply dark mode class
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

  useEffect(() => {
    localStorage.setItem('stakeholderColors', JSON.stringify(stakeholderColors));
  }, [stakeholderColors]);

  // Save to API whenever preferences change (debounced)
  useEffect(() => {
    if (!preferencesLoaded) return;

    const saveTimeout = setTimeout(async () => {
      try {
        await saveUserPreferences({
          darkMode,
          stakeholderColorMode,
          stakeholderColors,
        });
        console.log('💾 Saved preferences to API');
      } catch (error) {
        console.log('Could not save to API (using local storage)');
      }
    }, 1000);

    return () => clearTimeout(saveTimeout);
  }, [darkMode, stakeholderColorMode, stakeholderColors, preferencesLoaded]);

  const getStakeholderColor = (stakeholders) => {
    if (!stakeholderColorMode || !stakeholders || stakeholders.length === 0) {
      return getColorStyles('gray', darkMode);
    }

    const primaryStakeholder = stakeholders[0].toLowerCase().trim();
    const colorName = stakeholderColors[primaryStakeholder] || 'gray';
    
    return getColorStyles(colorName, darkMode);
  };

  const updateStakeholderColor = (actor, color) => {
    setStakeholderColors(prev => ({
      ...prev,
      [actor]: color
    }));
  };

  const resetToDefaultColors = () => {
    setStakeholderColors(DEFAULT_ACTOR_COLORS);
  };

  const toggleDarkMode = () => setDarkMode(prev => !prev);
  const toggleStakeholderColorMode = () => setStakeholderColorMode(prev => !prev);

  return (
    <ThemeContext.Provider value={{
      darkMode,
      stakeholderColorMode,
      stakeholderColors,
      toggleDarkMode,
      toggleStakeholderColorMode,
      getStakeholderColor,
      updateStakeholderColor,
      resetToDefaultColors
    }}>
      {children}
    </ThemeContext.Provider>
  );
};

// Theme Controls Component
export const ThemeControls = () => {
  const {
    darkMode,
    stakeholderColorMode,
    stakeholderColors,
    toggleDarkMode,
    toggleStakeholderColorMode,
    updateStakeholderColor
  } = useTheme();

  return (
    <ThemeSettingsMenu
      darkMode={darkMode}
      stakeholderColorMode={stakeholderColorMode}
      stakeholderColors={stakeholderColors}
      toggleDarkMode={toggleDarkMode}
      toggleStakeholderColorMode={toggleStakeholderColorMode}
      updateStakeholderColor={updateStakeholderColor}
    />
  );
};

export default ThemeProvider;
export { ThemeContext }