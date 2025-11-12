import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import Query from '../Query';
import { api } from '../../api/client';
import { toast } from 'react-toastify';
import useSessionStore from '../../store/useSessionStore';

// Mock dependencies
vi.mock('../../api/client', () => ({
  api: {
    queryRequirements: vi.fn()
  }
}));

vi.mock('react-toastify', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn()
  }
}));

vi.mock('../../store/useSessionStore', () => ({
  default: vi.fn()
}));

describe('Query Component', () => {
  const mockSession = {
    currentSessionId: 'test-session-123'
  };

  const mockNoSession = {
    currentSessionId: null
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  const renderWithRouter = (component) => {
    return render(<MemoryRouter>{component}</MemoryRouter>);
  };

  describe('Session Validation', () => {
    it('shows warning when no session is selected', () => {
      useSessionStore.mockReturnValue(mockNoSession);
      
      renderWithRouter(<Query />);
      
      expect(screen.getByText(/Please select a session from the sidebar or create a new chat/i)).toBeInTheDocument();
    });

    it('renders query interface when session is selected', () => {
      useSessionStore.mockReturnValue(mockSession);
      
      renderWithRouter(<Query />);
      
      // Should have input and send button
      expect(screen.getByPlaceholderText('Ask a question...')).toBeInTheDocument();
      expect(screen.getByText('Send')).toBeInTheDocument();
    });
  });

  describe('Question Input and Submission', () => {
    beforeEach(() => {
      useSessionStore.mockReturnValue(mockSession);
    });

    it('handles question input', async () => {
      renderWithRouter(<Query />);
      
      const input = screen.getByPlaceholderText('Ask a question...');
      await userEvent.type(input, 'What are the main actors?');
      
      expect(input.value).toBe('What are the main actors?');
    });

    it('disables send button when input is empty', () => {
      renderWithRouter(<Query />);
      
      const sendButton = screen.getByText('Send');
      expect(sendButton).toBeDisabled();
    });

    it('enables send button when input has content', async () => {
      renderWithRouter(<Query />);
      
      const input = screen.getByPlaceholderText('Ask a question...');
      await userEvent.type(input, 'Test question');
      
      const sendButton = screen.getByText('Send');
      expect(sendButton).not.toBeDisabled();
    });

    it('submits question on Enter key press', async () => {
      api.queryRequirements.mockResolvedValueOnce({
        data: { answer: 'Test answer', relevant_use_cases: [] }
      });
      
      renderWithRouter(<Query />);
      
      const input = screen.getByPlaceholderText('Ask a question...');
      await userEvent.type(input, 'Test question{enter}');
      
      expect(api.queryRequirements).toHaveBeenCalledWith({
        session_id: 'test-session-123',
        question: 'Test question'
      });
    });

    it('clears input after submission', async () => {
      api.queryRequirements.mockResolvedValueOnce({
        data: { answer: 'Test answer', relevant_use_cases: [] }
      });
      
      renderWithRouter(<Query />);
      
      const input = screen.getByPlaceholderText('Ask a question...');
      await userEvent.type(input, 'Test question');
      fireEvent.click(screen.getByText('Send'));
      
      await waitFor(() => {
        expect(input.value).toBe('');
      });
    });
  });

  describe('Conversation Display', () => {
    beforeEach(() => {
      useSessionStore.mockReturnValue(mockSession);
    });

    it('shows empty state when no messages', () => {
      renderWithRouter(<Query />);
      
      expect(screen.getByText('Ask questions about your requirements')).toBeInTheDocument();
      expect(screen.getByText(/Example:/)).toBeInTheDocument();
    });

    it('displays user and assistant messages', async () => {
      api.queryRequirements.mockResolvedValueOnce({
        data: { answer: 'Test answer', relevant_use_cases: ['UC1', 'UC2'] }
      });
      
      renderWithRouter(<Query />);
      
      const input = screen.getByPlaceholderText('Ask a question...');
      await userEvent.type(input, 'Test question');
      fireEvent.click(screen.getByText('Send'));
      
      await waitFor(() => {
        expect(screen.getByText('Test question')).toBeInTheDocument();
        expect(screen.getByText('Test answer')).toBeInTheDocument();
        expect(screen.getByText('UC1')).toBeInTheDocument();
        expect(screen.getByText('UC2')).toBeInTheDocument();
      });
    });

    it('displays relevant use cases when provided', async () => {
      api.queryRequirements.mockResolvedValueOnce({
        data: {
          answer: 'Test answer',
          relevant_use_cases: ['Login Use Case', 'Payment Use Case']
        }
      });
      
      renderWithRouter(<Query />);
      
      await userEvent.type(screen.getByPlaceholderText('Ask a question...'), 'Test');
      fireEvent.click(screen.getByText('Send'));
      
      await waitFor(() => {
        expect(screen.getByText('Relevant Use Cases:')).toBeInTheDocument();
        expect(screen.getByText('Login Use Case')).toBeInTheDocument();
        expect(screen.getByText('Payment Use Case')).toBeInTheDocument();
      });
    });
  });

  describe('Loading and Error States', () => {
    beforeEach(() => {
      useSessionStore.mockReturnValue(mockSession);
    });

    it('shows loading state while fetching answer', async () => {
      api.queryRequirements.mockImplementationOnce(() => new Promise(resolve => setTimeout(resolve, 100)));
      
      renderWithRouter(<Query />);
      
      await userEvent.type(screen.getByPlaceholderText('Ask a question...'), 'Test');
      fireEvent.click(screen.getByText('Send'));
      
      expect(screen.getByText('Send')).toBeDisabled();
      expect(screen.getByPlaceholderText('Ask a question...')).toBeDisabled();
      
      // Check for loading animation dots
      const loadingDots = screen.getAllByRole('generic').filter(
        element => element.className.includes('animate-bounce')
      );
      expect(loadingDots.length).toBe(3);
    });

    it('handles API errors', async () => {
      api.queryRequirements.mockRejectedValueOnce(new Error('API Error'));
      
      renderWithRouter(<Query />);
      
      await userEvent.type(screen.getByPlaceholderText('Ask a question...'), 'Test');
      fireEvent.click(screen.getByText('Send'));
      
      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('Query failed');
      });
    });

    it('removes user message on API error', async () => {
      api.queryRequirements.mockRejectedValueOnce(new Error('API Error'));
      
      renderWithRouter(<Query />);
      
      await userEvent.type(screen.getByPlaceholderText('Ask a question...'), 'Test question');
      fireEvent.click(screen.getByText('Send'));
      
      await waitFor(() => {
        expect(screen.queryByText('Test question')).not.toBeInTheDocument();
      });
    });
  });

  describe('Input Validation', () => {
    beforeEach(() => {
      useSessionStore.mockReturnValue(mockSession);
    });

    it('prevents submission of empty questions', async () => {
      renderWithRouter(<Query />);
      
      fireEvent.click(screen.getByText('Send'));
      
      expect(api.queryRequirements).not.toHaveBeenCalled();
    });

    it('disables button with whitespace-only questions', async () => {
      renderWithRouter(<Query />);
      
      await userEvent.type(screen.getByPlaceholderText('Ask a question...'), '   ');
      const sendButton = screen.getByText('Send');
      
      expect(sendButton).toBeDisabled();
      expect(api.queryRequirements).not.toHaveBeenCalled();
    });

    it('requires session selection', () => {
      useSessionStore.mockReturnValue(mockNoSession);
      renderWithRouter(<Query />);
      
      // Match the actual text from Query.jsx line 71
      expect(screen.getByText('Please select a session from the sidebar or create a new chat to query requirements')).toBeInTheDocument();
      // The input and send button should not be visible
      expect(screen.queryByPlaceholderText('Ask a question...')).not.toBeInTheDocument();
      expect(screen.queryByText('Send')).not.toBeInTheDocument();
    });
  });
});
