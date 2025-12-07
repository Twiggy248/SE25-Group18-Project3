import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Extraction from '../Extraction';
import { api } from '../../api/client';
import { toast } from 'react-toastify';
import useSessionStore from '../../store/useSessionStore';

// Mock dependencies
vi.mock('../../api/client', () => ({
  api: {
    extractFromText: vi.fn(),
    extractFromDocument: vi.fn(),
  }
}));

vi.mock('react-toastify', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn(),
  }
}));

vi.mock('../../store/useSessionStore', () => ({
  default: vi.fn()
}));

// Mock components
vi.mock('../../components/FileUploader', () => ({
  default: ({ onFileSelect, uploading }) => (
    <div data-testid="file-uploader">
      <button 
        onClick={() => onFileSelect(new File(['test'], 'test.txt'))}
        disabled={uploading}
      >
        Upload File
      </button>
    </div>
  )
}));

vi.mock('../../components/LoadingSpinner', () => ({
  default: ({ message }) => <div data-testid="loading-spinner">{message}</div>
}));

describe('Extraction Component', () => {
  const mockSessionStore = {
    currentSessionId: 'test-session-123',
    setCurrentSession: vi.fn(),
    projectContext: 'Test Project',
    setProjectContext: vi.fn(),
    domain: 'Test Domain',
    setDomain: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    useSessionStore.mockReturnValue(mockSessionStore);
  });

  it('renders initial state correctly', () => {
    render(<Extraction />);
    
    // Check title
    expect(screen.getByText('Extract Use Cases ✨')).toBeInTheDocument();
    
    // Check session info fields
    expect(screen.getByLabelText('Project Context')).toBeInTheDocument();
    expect(screen.getByLabelText('Domain')).toBeInTheDocument();
    
    // Check tabs
    expect(screen.getByText('📝 Text Input')).toBeInTheDocument();
    expect(screen.getByText('📁 File Upload')).toBeInTheDocument();
    
    // Check session ID display
    expect(screen.getByText('Session ID:')).toBeInTheDocument();
    // Session ID is truncated with "..." in the component, so use partial match
    expect(screen.getByText(/test-session/)).toBeInTheDocument();
  });

  it('handles tab switching correctly', async () => {
    render(<Extraction />);
    
    // Initially should show text input
    expect(screen.getByLabelText('Requirements Text')).toBeInTheDocument();
    
    // Switch to file upload
    await userEvent.click(screen.getByText('📁 File Upload'));
    expect(screen.getByTestId('file-uploader')).toBeInTheDocument();
    
    // Switch back to text input
    await userEvent.click(screen.getByText('📝 Text Input'));
    expect(screen.getByLabelText('Requirements Text')).toBeInTheDocument();
  });

  it('handles project context and domain updates', async () => {
    render(<Extraction />);
    
    const projectInput = screen.getByLabelText('Project Context');
    const domainInput = screen.getByLabelText('Domain');
    
    await userEvent.type(projectInput, ' Updated');
    await userEvent.type(domainInput, ' Updated');
    
    expect(mockSessionStore.setProjectContext).toHaveBeenCalled();
    expect(mockSessionStore.setDomain).toHaveBeenCalled();
  });

  describe('Text Extraction', () => {
    const mockExtractResponse = {
      data: {
        session_id: 'new-session-456',
        extracted_count: 2,
        stored_count: 2,
        duplicate_count: 0,
        processing_time_seconds: 1.5,
        results: [
          {
            title: 'Test Use Case 1',
            status: 'stored',
            preconditions: ['Pre 1'],
            main_flows: [['Step 1', 'Step 2']],
            outcomes: ['Outcome 1']
          },
          {
            title: 'Test Use Case 2',
            status: 'stored',
            preconditions: ['Pre 2'],
            main_flows: [['Step 3', 'Step 4']],
            outcomes: ['Outcome 2']
          }
        ]
      }
    };

    it('handles text extraction successfully', async () => {
      api.extractFromText.mockImplementation(async () =>{
        await new Promise(resolve => setTimeout(resolve, 100));
        return mockExtractResponse;
      });
      
      render(<Extraction />);
      
      // Type requirements text
      const textArea = screen.getByLabelText('Requirements Text');
      await userEvent.type(textArea, 'Test requirements');
      
      // Click extract button
      const extractButton = screen.getByText('✨ Extract Use Cases');
      await userEvent.click(extractButton);
      
      // Check loading state (LoadingSpinner shows message in a <p> tag)
      expect(screen.getByText('⏳ Extracting...')).toBeInTheDocument();
      // Wait for results
      await waitFor(() => {
        expect(screen.getByText('Extraction Summary')).toBeInTheDocument();
      });
      
      // Verify API call
      expect(api.extractFromText).toHaveBeenCalledWith({
        raw_text: 'Test requirements',
        session_id: 'test-session-123',
        project_context: 'Test Project',
        domain: 'Test Domain'
      });
      
      // Check results display
      expect(screen.getByText('Test Use Case 1')).toBeInTheDocument();
      expect(screen.getByText('Test Use Case 2')).toBeInTheDocument();
      
      // Check summary stats
      const extractedLabel = screen.getByText('Extracted:');
      expect(extractedLabel.parentElement).toHaveTextContent(/^Extracted:\s+2$/);


      expect(screen.getByText('1.5s')).toBeInTheDocument(); // Processing time
      
      // Verify session update
      expect(mockSessionStore.setCurrentSession).toHaveBeenCalledWith('new-session-456');
      
      // Verify success toast
      expect(toast.success).toHaveBeenCalledWith(
        '✅ Extracted 2 use cases in 1.5s!'
      );
    });

    it('handles text extraction errors', async () => {
      api.extractFromText.mockRejectedValueOnce({
        response: { data: { detail: 'Test error' } }
      });
      
      render(<Extraction />);
      
      const textArea = screen.getByLabelText('Requirements Text');
      await userEvent.type(textArea, 'Test requirements');
      
      const extractButton = screen.getByText('✨ Extract Use Cases');
      await userEvent.click(extractButton);
      
      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('Test error');
      });
    });

    it('validates empty text input', async () => {
      render(<Extraction />);
      
      const extractButton = screen.getByText('✨ Extract Use Cases');
      expect(extractButton).toBeDisabled();
      
      await userEvent.click(extractButton);
      expect(api.extractFromText).not.toHaveBeenCalled();
    });
  });

  describe('File Upload', () => {
    const mockFileResponse = {
      data: {
        session_id: 'file-session-789',
        extracted_count: 1,
        stored_count: 1,
        processing_time_seconds: 2.0,
        results: [
          {
            title: 'File Use Case',
            status: 'stored',
            main_flows: [['Step 1']]
          }
        ]
      }
    };

    it('handles file upload successfully', async () => {
      api.extractFromDocument.mockResolvedValueOnce(mockFileResponse);
      
      render(<Extraction />);
      
      // Switch to file upload tab
      await userEvent.click(screen.getByText('📁 File Upload'));
      
      // Trigger file upload
      const uploadButton = screen.getByText('Upload File');
      await userEvent.click(uploadButton);
      
      // Verify API call
      await waitFor(() => {
        expect(api.extractFromDocument).toHaveBeenCalled();
      });
      
      // Check results display
      expect(screen.getByText('File Use Case')).toBeInTheDocument();
      
      // Verify session update
      expect(mockSessionStore.setCurrentSession).toHaveBeenCalledWith('file-session-789');
      
      // Verify success toast
      expect(toast.success).toHaveBeenCalled();
    });

    it('handles file upload errors', async () => {
      api.extractFromDocument.mockRejectedValueOnce({
        response: { data: { detail: 'Upload failed' } }
      });
      
      render(<Extraction />);
      
      await userEvent.click(screen.getByText('📁 File Upload'));
      await userEvent.click(screen.getByText('Upload File'));
      
      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('Upload failed');
      });
    });
  });

  describe('Results Display', () => {
    const mockResults = {
      session_id: 'test-session',
      extracted_count: 2,
      stored_count: 1,
      duplicate_count: 1,
      processing_time_seconds: 1.0,
      results: [
        {
          title: 'Stored Use Case',
          status: 'stored',
          preconditions: ['Pre 1'],
          main_flows: [['Step 1']],
          sub_flows: [{ sub_title: 'Sub 1', steps: ['Sub step 1'] }],
          alternate_flows: ['Alt 1'],
          outcomes: ['Outcome 1'],
          stakeholders: ['User', 'Admin']
        },
        {
          title: 'Duplicate Use Case',
          status: 'duplicate',
          main_flows: [['Step 1']]
        }
      ]
    };

    it('displays all use case details correctly', async () => {
      api.extractFromText.mockResolvedValueOnce({ data: mockResults });
      
      render(<Extraction />);
      
      await userEvent.type(screen.getByLabelText('Requirements Text'), 'Test');
      await userEvent.click(screen.getByText('✨ Extract Use Cases'));
      
      // First wait for loading to complete
      await waitFor(() => {
        expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument();
      });
      
      // Then check the results
      const storedUseCase = screen.getByText('Stored Use Case').closest('.p-4');
      const duplicateUseCase = screen.getByText('Duplicate Use Case').closest('.p-4');
      
      // Verify elements exist
      expect(storedUseCase).toBeInTheDocument();
      expect(duplicateUseCase).toBeInTheDocument();
      
      // Check status badges
      expect(screen.getByText('✅ Stored')).toBeInTheDocument();
      expect(screen.getByText('🔄 Duplicate')).toBeInTheDocument();
      
      // Check details sections in stored use case
      within(storedUseCase).getByText('Pre 1');
      within(storedUseCase).getByText('Step 1');
      within(storedUseCase).getByText('Sub step 1');
      within(storedUseCase).getByText('Alt 1');
      within(storedUseCase).getByText('Outcome 1');
      within(storedUseCase).getByText('User, Admin');
      
      // Check details sections in duplicate use case
      within(duplicateUseCase).getByText('Step 1');
    });

    it('shows empty state when no results', () => {
      render(<Extraction />);
      
      expect(screen.getByText('Results will appear here after extraction')).toBeInTheDocument();
    });

    it('handles loading state', async () => {
      api.extractFromText.mockImplementationOnce(() => new Promise(resolve => setTimeout(resolve, 100)));
      
      render(<Extraction />);
      
      await userEvent.type(screen.getByLabelText('Requirements Text'), 'Test');
      await userEvent.click(screen.getByText('✨ Extract Use Cases'));
      
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
      expect(screen.getByText('Processing your requirements...')).toBeInTheDocument();
    });
  });
});