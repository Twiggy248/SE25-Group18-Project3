// -----------------------------------------------------------------------------
// File: vite.config.js
// Description: Vite build configuration for ReqEngine frontend - defines
//              build settings, plugins, and test configuration for React app.
// Author: Pradyumna Chacham
// Date: November 2025
// Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
// License: MIT License - see LICENSE file in the root directory.
// -----------------------------------------------------------------------------

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/setupTests.js',
    passWithNoTests: true,
    coverage: { 
      provider: 'v8',
      reporter: ['text', 'html', 'json', 'lcov'],
      all: true,
      reportOnFailure: true,
      exclude: [
        'node_modules/',
        'src/setupTests.js',
      ],
    },
  },
})
