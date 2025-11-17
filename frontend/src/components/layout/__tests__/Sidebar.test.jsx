import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Sidebar from '../Sidebar';
import useSessionStore from '../../../store/useSessionStore';
import { api } from '../../../api/client';

// Mock dependencies
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => ({ pathname: '/' })
  };
});

vi.mock('../../../api/client', () => ({
  api: {
    getSessions: vi.fn(),
    deleteSession: vi.fn()
  }
}));

vi.mock('../../../store/useSessionStore', () => ({
  default: vi.fn()
}));

describe('Sidebar Component', () => {
  const mockSessions = [
    {
      session_id: 'test-session',
      session_title: 'Test Session',
      project_context: 'Test Project',
      last_active: '2024-01-01T00:00:00Z'
    }
  ];

  const mockSession = {
    currentSessionId: 'test-session',
    setCurrentSession: vi.fn(),
    sessions: [],
    setSessions: vi.fn()
  };

  beforeEach(() => {
    vi.clearAllMocks();
    useSessionStore.mockReturnValue(mockSession);
    api.getSessions.mockResolvedValue({ data: { sessions: mockSessions } });
  });

  const renderWithRouter = () => {
    return render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>
    );
  };

  it('renders new chat button', () => {
    renderWithRouter();
    expect(screen.getByText('New Chat')).toBeInTheDocument();
  });

  it('shows active session indicator when session exists', async () => {
    renderWithRouter();
    // Wait for sessions to load
    await waitFor(() => {
      expect(screen.getByText('Active session')).toBeInTheDocument();
    });
  });

  it('shows no sessions message when no sessions exist', async () => {
    useSessionStore.mockReturnValue({
      ...mockSession,
      sessions: []
    });
    api.getSessions.mockResolvedValue({ data: { sessions: [] } });
    renderWithRouter();
    await waitFor(() => {
      expect(screen.getByText('Loading...')).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(screen.getByText('No sessions yet')).toBeInTheDocument();
    });
  });

  it('handles new chat button click', async () => {
    renderWithRouter();
    fireEvent.click(screen.getByText('New Chat'));
    expect(mockSession.setCurrentSession).toHaveBeenCalledWith(null);
    expect(mockNavigate).toHaveBeenCalledWith('/');
  });

  it('loads and displays sessions on mount', async () => {
    const testSessions = [{
      session_id: 'test-1',
      session_title: 'Test Session',
      last_active: '2024-01-01T00:00:00Z'
    }];

    useSessionStore.mockReturnValue({
      ...mockSession,
      sessions: testSessions
    });
    
    api.getSessions.mockResolvedValue({ data: { sessions: testSessions } });
    renderWithRouter();
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(api.getSessions).toHaveBeenCalled();
    });
    
    // Then check for session display
    await waitFor(() => {
      expect(screen.getByText('Test Session')).toBeInTheDocument();
    });
  });

  it('shows session data with proper formatting', async () => {
    const formattedSession = {
      session_id: 'test-1',
      session_title: 'Test Session',
      project_context: 'Test Project',
      last_active: '2024-01-01T00:00:00Z'
    };

    useSessionStore.mockReturnValue({
      ...mockSession,
      sessions: [formattedSession]
    });

    api.getSessions.mockResolvedValue({ data: { sessions: [formattedSession] } });
    
    renderWithRouter();
    
    await waitFor(() => {
      expect(api.getSessions).toHaveBeenCalled();
    });

    expect(screen.getByText('Recent Sessions')).toBeInTheDocument();
    const session = screen.getByText('Test Session');
    expect(session).toBeInTheDocument();
    
    // Sidebar displays session title only, not timestamp
  });
});