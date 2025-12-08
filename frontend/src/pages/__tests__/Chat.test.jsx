import React from 'react';
import { describe, it, expect, vi, beforeEach, beforeAll } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Chat from '../Chat';
import { api } from '../../api/client';
import { toast } from 'react-toastify';
import useSessionStore from '../../store/useSessionStore';

// Mock dependencies
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
    useLocation: () => ({
      pathname: '/',
    }),
  };
});

vi.mock('../../context/ThemeContext', () => ({
  useTheme: () => ({
    darkMode: false,
    getStakeholderColor: () => 'bg-blue-100', 
    stakeholderColorMode: 'default'
  })
}));

vi.mock('../../api/client', () => ({
  api: {
    extractFromText: vi.fn(),
    extractFromDocument: vi.fn(), 
    getSessionTitle: vi.fn(), 
    getSessions: vi.fn(), 
    getSessionHistory: vi.fn(), 
  }
}));

vi.mock('react-toastify', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn()
  }
}));

const mocks = vi.hoisted(() => ({
  setSessions: vi.fn()
}));

vi.mock('../../store/useSessionStore', () => {
  const mockStore = vi.fn(() => ({
    currentSessionId: 'test-session', 
    setCurrentSession: vi.fn(), 
  }));

  mockStore.getState = vi.fn(() => ({
    setSessions: mocks.setSessions
  }));

  return { default: mockStore};
});

// Mock components
vi.mock('../../components/FileUploader', () => ({
  default: ({ onFileSelect }) => (
    <div data-testid="file-uploader">
      <button onClick={() => onFileSelect(new File([''], 'test.txt'))}>
        Upload File
      </button>
    </div>
  )
}));

vi.mock('../../components/layout/SessionHeader', () => ({
  default: () => <div data-testid="session-header">Session Header</div>
}));

describe('Chat Component', () => {
  const mockSession = {
    currentSessionId: 'test-session',
    projectContext: 'Test Project',
    domain: 'Test Domain'
  };

  //mock layout method  
  beforeAll(() => {
    Element.prototype.scrollIntoView = vi.fn();
  });

  beforeEach(() => {
    vi.clearAllMocks();
    useSessionStore.mockReturnValue(mockSession);
    api.getSessionHistory.mockResolvedValue({ data: { conversation_history: [] } });
  });

  it('renders chat interface', () => {
    render(<Chat />);
    expect(screen.getByTestId('session-header')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Describe your requirements... (Press Enter to send, Shift+Enter for new line)')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /upload file/i})).toBeInTheDocument();
  });

  it('handles text input submission', async () => {
    api.extractFromText.mockResolvedValueOnce({
      data: { results: [{ title: 'Test Use Case' }] }
    });

    render(<Chat />);
    
    const textarea = screen.getByPlaceholderText('Describe your requirements... (Press Enter to send, Shift+Enter for new line)');
    await userEvent.type(textarea, 'Test requirements');
    fireEvent.click(screen.getByText('⬆'));

    expect(api.extractFromText).toHaveBeenCalledWith({
      raw_text: 'Test requirements',
      session_id: 'test-session'
    });
  });

  it('handles file upload', async () => {
    api.extractFromDocument.mockResolvedValueOnce({
      data: { results: [{ title: 'Test Use Case' }] }
    });

    render(<Chat />);
    
    // Switch to file upload tab
    fireEvent.click(screen.getByRole('button', { name: /upload file/i}));

    fireEvent.click(screen.getByText(/upload file/i));

    await waitFor(() => {
      expect(api.extractFromDocument).toHaveBeenCalled();
    });
  });

  it('shows loading state during extraction', async () => {
    api.extractFromText.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    render(<Chat />);
    
    const textarea = screen.getByPlaceholderText('Describe your requirements... (Press Enter to send, Shift+Enter for new line)');
    await userEvent.type(textarea, 'Test requirements');
    fireEvent.click(screen.getByText('⬆'));

    expect(screen.getByText('⏳')).toBeInTheDocument();
  });

  it('handles extraction errors', async () => {
    api.extractFromText.mockRejectedValueOnce(new Error('Extraction failed'));

    render(<Chat />);
    
    const textarea = screen.getByPlaceholderText('Describe your requirements... (Press Enter to send, Shift+Enter for new line)');
    await userEvent.type(textarea, 'Test requirements');
    fireEvent.click(screen.getByText('⬆'));

    await waitFor(() => {
      expect(screen.getByText(/Could not process request/i)).toBeInTheDocument;
    });
  });

  //our logic has changed 
  it(' does not require session selection', () => {
    useSessionStore.mockReturnValue({ currentSessionId: null });
    
    render(<Chat />);
    
    expect(screen.getByPlaceholderText('Describe your requirements... (Press Enter to send, Shift+Enter for new line)')).toBeInTheDocument();
    expect(screen.getByText('⬆')).toBeDisabled();
  });

  it('validates input before submission', async () => {
    render(<Chat />);
    
    // Try submitting empty text
    expect(screen.getByText('⬆')).toBeDisabled();
    fireEvent.keyDown(screen.getByPlaceholderText(/Describe your requirements/i), { key: 'Enter', code: 'Enter', charCode: 13 });
    
    expect(api.extractFromText).not.toHaveBeenCalled();
    expect(toast.error).toHaveBeenCalledWith('Please enter some text');
  });

  it('displays extraction results', async () => {
    api.extractFromText.mockResolvedValueOnce({
      data: {
        results: [
          { title: 'Use Case 1', main_flow: ['Step 1'] },
          { title: 'Use Case 2', main_flow: ['Step 1'] }
        ], 
        extracted_count: 2, 
        processing_time_seconds: 0.5, 
        session_id:'new-session-id'
      }
    });

    api.getSessionTitle.mockResolvedValueOnce({
      data: { session_title: 'New Session' }
    });

    api.getSessions.mockResolvedValueOnce({
      data: { sessions: [] }
    });

    render(<Chat />);
    
    const textarea = screen.getByPlaceholderText(/Describe your requirements/i);
    await userEvent.type(textarea, 'Test requirements');
    fireEvent.click(screen.getByText('⬆'));

    await waitFor(() => {
      expect(screen.getByText('Use Case 1')).toBeInTheDocument();
      expect(screen.getByText('Use Case 2')).toBeInTheDocument();
    });
  });
});