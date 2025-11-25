// -----------------------------------------------------------------------------
// File: App.jsx
// Description: Main React application component for ReqEngine frontend -
//              handles routing, layout structure, and global state management.
// Author: Pradyumna Chacham
// Date: November 2025
// Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
// License: MIT License - see LICENSE file in the root directory.
// -----------------------------------------------------------------------------

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { ThemeProvider } from './context/ThemeContext';

// Layout Components
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';

// Pages
import Chat from './pages/Chat';
import Extraction from './pages/Extraction';
import Export from './pages/Export';
import Query from './pages/Query';
import UseCaseDetail from './pages/UseCaseDetail';
import UseCaseRefine from './pages/UseCaseRefine';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login'

function App() {
  return (
    <ThemeProvider>
      <Router>
        <div className="flex h-screen bg-gray-50">
          {/* Sidebar */}
          <Sidebar />

          {/* Main Content Area */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Header */}
            <Header />

            {/* Page Content */}
            <main className="flex-1 overflow-y-auto">
              <Routes>
                <Route path="/" element={<ProtectedRoute><Chat /></ProtectedRoute>} />
                <Route path="/extraction" element={<ProtectedRoute><Extraction /></ProtectedRoute>} />
                <Route path="/export" element={<ProtectedRoute><Export /></ProtectedRoute>} />
                <Route path="/query" element={<ProtectedRoute><Query /></ProtectedRoute>} />
                <Route path="/use-case/:id" element={<ProtectedRoute><UseCaseDetail /></ProtectedRoute>} />
                <Route path="/use-case/:id/refine" element={<ProtectedRoute><UseCaseRefine /></ProtectedRoute>} />
                <Route path="/login" element={<Login />}/>
              </Routes>
            </main>
          </div>

          {/* Toast Notifications */}
          <ToastContainer
            position="top-right"
            autoClose={3000}
            hideProgressBar={false}
            newestOnTop={false}
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
          />
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;