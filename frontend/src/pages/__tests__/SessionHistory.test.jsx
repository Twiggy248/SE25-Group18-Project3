import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SessionHistory from '../SessionHistory';
import { api } from '../../api/client';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';
import { formatDate } from '../../utils/formatters';

// Mock dependencies
vi.mock('react-router-dom', () => ({
  useNavigate: vi.fn()
}));

vi.mock('../../api/client', () => ({
  api: {
    getSessions: vi.fn(),
    deleteSession: vi.fn()
  }
}));

vi.mock('react-toastify', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn()
  }
}));

vi.mock('../../utils/formatters', () => ({
  formatDate: vi.fn()
}));

vi.mock('../../components/LoadingSpinner', () => ({
  default: ({ message }) => <div data-testid="loading-spinner">{message}</div>
}));

describe('SessionHistory Component', () => {
  const mockSessions = {
    sessions: [
      {
        session_id: 'session-123',
        session_title: 'Test Session 1',
        project_context: 'Project 1',
        created_at: '2023-01-01T00:00:00Z',
        last_active: '2023-01-02T00:00:00Z'
      },
      {
        session_id: 'session-456',
        project_context: 'Project 2',
        created_at: '2023-02-01T00:00:00Z',
        last_active: '2023-02-02T00:00:00Z'
      }
    ]
  };

  const navigate = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    useNavigate.mockReturnValue(navigate);
    formatDate.mockImplementation(date => date); // Just return the date string for testing
    window.confirm = vi.fn(); // Mock confirm dialog
  });

  it('shows loading state initially', () => {
    api.getSessions.mockImplementationOnce(() => new Promise(() => {}));
    
    render(<SessionHistory />);
    
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    expect(screen.getByText('Loading sessions...')).toBeInTheDocument();
  });

  it('displays empty state when no sessions exist', async () => {
    api.getSessions.mockResolvedValueOnce({ data: { sessions: [] } });
    
    render(<SessionHistory />);
    
    await waitFor(() => {
      expect(screen.getByText('No sessions yet')).toBeInTheDocument();
      expect(screen.getByText('Create Your First Session')).toBeInTheDocument();
    });
  });

  it('navigates to extraction page when clicking create session button', async () => {
    api.getSessions.mockResolvedValueOnce({ data: { sessions: [] } });
    
    render(<SessionHistory />);
    
    await waitFor(() => {
      fireEvent.click(screen.getByText('Create Your First Session'));
      expect(navigate).toHaveBeenCalledWith('/extraction');
    });
  });

  it('displays session list correctly', async () => {
    api.getSessions.mockResolvedValueOnce({ data: mockSessions });
    
    render(<SessionHistory />);
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument();
    });

    // Check table headers
    expect(screen.getByText('Session Title')).toBeInTheDocument();
    expect(screen.getByText('Actions')).toBeInTheDocument();

    // Check session data
    expect(screen.getByText('Test Session 1')).toBeInTheDocument();
    expect(screen.getByText('Project 2')).toBeInTheDocument();
  });

  it('handles session deletion with confirmation', async () => {
    api.getSessions.mockResolvedValueOnce({ data: mockSessions });
    api.deleteSession.mockResolvedValueOnce({});
    window.confirm.mockReturnValueOnce(true);
    
    render(<SessionHistory />);
    
    await waitFor(() => {
      const deleteButtons = screen.getAllByText('Delete');
      fireEvent.click(deleteButtons[0]);
    });
    
    expect(window.confirm).toHaveBeenCalledWith(
      'Are you sure you want to delete this session?'
    );
    
    await waitFor(() => {
      expect(api.deleteSession).toHaveBeenCalledWith('session-123');
      expect(toast.success).toHaveBeenCalledWith('Session deleted successfully');
      expect(api.getSessions).toHaveBeenCalledTimes(2); // Initial + reload
    });
  });

  it('cancels session deletion when user declines', async () => {
    api.getSessions.mockResolvedValueOnce({ data: mockSessions });
    window.confirm.mockReturnValueOnce(false);
    
    render(<SessionHistory />);
    
    await waitFor(() => {
      const deleteButtons = screen.getAllByText('Delete');
      fireEvent.click(deleteButtons[0]);
    });
    
    expect(window.confirm).toHaveBeenCalled();
    expect(api.deleteSession).not.toHaveBeenCalled();
  });

  it('navigates to session details on view button click', async () => {
    api.getSessions.mockResolvedValueOnce({ data: mockSessions });
    
    render(<SessionHistory />);
    
    await waitFor(() => {
      const viewButtons = screen.getAllByText('View');
      fireEvent.click(viewButtons[0]);
    });
    
    expect(navigate).toHaveBeenCalledWith('/sessions/session-123');
  });

  it('handles loading error', async () => {
    api.getSessions.mockRejectedValueOnce(new Error('Failed to load'));
    
    render(<SessionHistory />);
    
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Failed to load sessions');
    });
  });

  it('handles deletion error', async () => {
    api.getSessions.mockResolvedValueOnce({ data: mockSessions });
    api.deleteSession.mockRejectedValueOnce(new Error('Failed to delete'));
    window.confirm.mockReturnValueOnce(true);
    
    render(<SessionHistory />);
    
    await waitFor(() => {
      const deleteButtons = screen.getAllByText('Delete');
      fireEvent.click(deleteButtons[0]);
    });
    
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Failed to delete session');
    });
  });

  it('displays session titles correctly', async () => {
    api.getSessions.mockResolvedValueOnce({ data: mockSessions });
    
    render(<SessionHistory />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Session 1')).toBeInTheDocument();
    });
  });

  it('uses project context as fallback when session title is missing', async () => {
    api.getSessions.mockResolvedValueOnce({ data: mockSessions });
    
    render(<SessionHistory />);
    
    await waitFor(() => {
      // Second session has no title, should show project context
      expect(screen.getByText('Project 2')).toBeInTheDocument();
    });
  });
});