import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import Chat from '../Chat';
import { api } from '../../api/client';
import { toast } from 'react-toastify';
import useSessionStore from '../../store/useSessionStore';

// Mock dependencies
vi.mock('../../api/client', () => ({
  api: {
    extractFromText: vi.fn(),
    extractFromDocument: vi.fn()
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

vi.mock('../../components/Layout/SessionHeader', () => ({
  default: () => <div data-testid="session-header">Session Header</div>
}));

describe('Chat Component', () => {
  const mockSession = {
    currentSessionId: 'test-session',
    projectContext: 'Test Project',
    domain: 'Test Domain'
  };

  beforeEach(() => {
    vi.clearAllMocks();
    useSessionStore.mockReturnValue(mockSession);
  });

  it('renders chat interface', () => {
    render(<Chat />);
    expect(screen.getByTestId('session-header')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Enter your requirements/i)).toBeInTheDocument();
    expect(screen.getByTestId('file-uploader')).toBeInTheDocument();
  });

  it('handles text input submission', async () => {
    api.extractFromText.mockResolvedValueOnce({
      data: { results: [{ title: 'Test Use Case' }] }
    });

    render(<Chat />);
    
    const textarea = screen.getByPlaceholderText(/Enter your requirements/i);
    await userEvent.type(textarea, 'Test requirements');
    fireEvent.click(screen.getByText('Extract Use Cases'));

    expect(api.extractFromText).toHaveBeenCalledWith({
      text: 'Test requirements',
      session_id: 'test-session'
    });
  });

  it('handles file upload', async () => {
    api.extractFromDocument.mockResolvedValueOnce({
      data: { results: [{ title: 'Test Use Case' }] }
    });

    render(<Chat />);
    
    // Switch to file upload tab
    fireEvent.click(screen.getByText('📁 File Upload'));
    
    // Trigger file upload
    fireEvent.click(screen.getByText('Upload File'));

    await waitFor(() => {
      expect(api.extractFromDocument).toHaveBeenCalled();
    });
  });

  it('shows loading state during extraction', async () => {
    api.extractFromText.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    render(<Chat />);
    
    const textarea = screen.getByPlaceholderText(/Enter your requirements/i);
    await userEvent.type(textarea, 'Test requirements');
    fireEvent.click(screen.getByText('Extract Use Cases'));

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  it('handles extraction errors', async () => {
    api.extractFromText.mockRejectedValueOnce(new Error('Extraction failed'));

    render(<Chat />);
    
    const textarea = screen.getByPlaceholderText(/Enter your requirements/i);
    await userEvent.type(textarea, 'Test requirements');
    fireEvent.click(screen.getByText('Extract Use Cases'));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Failed to extract use cases');
    });
  });

  it('requires session selection', () => {
    useSessionStore.mockReturnValue({ currentSessionId: null });
    
    render(<Chat />);
    
    expect(screen.getByText('Please select or create a session to continue')).toBeInTheDocument();
    expect(screen.getByText('Extract Use Cases')).toBeDisabled();
  });

  it('validates input before submission', async () => {
    render(<Chat />);
    
    // Try submitting empty text
    fireEvent.click(screen.getByText('Extract Use Cases'));
    
    expect(api.extractFromText).not.toHaveBeenCalled();
    expect(toast.error).toHaveBeenCalledWith('Please enter some requirements text');
  });

  it('displays extraction results', async () => {
    api.extractFromText.mockResolvedValueOnce({
      data: {
        results: [
          { title: 'Use Case 1', description: 'First use case' },
          { title: 'Use Case 2', description: 'Second use case' }
        ]
      }
    });

    render(<Chat />);
    
    const textarea = screen.getByPlaceholderText(/Enter your requirements/i);
    await userEvent.type(textarea, 'Test requirements');
    fireEvent.click(screen.getByText('Extract Use Cases'));

    await waitFor(() => {
      expect(screen.getByText('Use Case 1')).toBeInTheDocument();
      expect(screen.getByText('Use Case 2')).toBeInTheDocument();
    });
  });
});