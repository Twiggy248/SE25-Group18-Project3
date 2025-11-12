// -----------------------------------------------------------------------------
// File: useSessionStore.js
// Description: Zustand state management store for ReqEngine - manages session
//              state, project context, and use cases across the application.
// Author: Pradyumna Chacham
// Date: November 2025
// Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
// License: MIT License - see LICENSE file in the root directory.
// -----------------------------------------------------------------------------

import { create } from 'zustand';

const useSessionStore = create((set, get) => ({
  currentSessionId: null,
  sessionTitle: '',
  sessions: [],
  projectContext: '',
  domain: '',
  useCases: [],
  
  setCurrentSession: (sessionId, title = '') => {
    if (sessionId) {
      // Find existing session
      const session = get().sessions.find(s => s.session_id === sessionId);
      // Use title hierarchy: provided title > existing session title > project context > ID-based title
      const finalTitle = title || 
                        session?.session_title || 
                        session?.project_context || 
                        `Session ${sessionId.slice(0, 8)}`;
      set({ 
        currentSessionId: sessionId,
        sessionTitle: finalTitle
      });
    } else {
      set({
        currentSessionId: null,
        sessionTitle: ''
      });
    }
  },
  setSessions: (sessions) => set({ sessions }),
  setProjectContext: (context) => set({ projectContext: context }),
  setDomain: (domain) => set({ domain: domain }),
  setUseCases: (useCases) => set({ useCases: useCases }),
  
  clearSession: () => set({
    currentSessionId: null,
    sessionTitle: '',
    projectContext: '',
    domain: '',
    useCases: [],
  }),
}));

export default useSessionStore;