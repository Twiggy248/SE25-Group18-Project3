// -----------------------------------------------------------------------------
// File: setupTests.js
// Description: Test environment setup for ReqEngine frontend - configures
//              Vitest, React Testing Library, and global test utilities.
// Author: Pradyumna Chacham
// Date: November 2025
// Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
// License: MIT License - see LICENSE file in the root directory.
// -----------------------------------------------------------------------------

import '@testing-library/jest-dom'
import { vi } from 'vitest'
import { cleanup } from '@testing-library/react'

// Mock react-toastify
vi.mock('react-toastify', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn(),
  },
}))

// Clean up after each test
afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})