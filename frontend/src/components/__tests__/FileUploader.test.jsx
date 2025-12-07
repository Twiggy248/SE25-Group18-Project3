import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { act } from 'react-dom/test-utils'
import FileUploader from '../FileUploader'

// Mock react-dropzone
const mocks = vi.hoisted(() => ({
  useDropzone: vi.fn(() => ({
    getRootProps: () => ({ role: 'presentation' }),
    getInputProps: () => ({}),
    isDragActive: false
  }))
}));

vi.mock('react-dropzone', () => ({
  useDropzone: mocks.useDropzone
}));

describe('FileUploader Component', () => {
  const mockOnFileSelect = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();

    mocks.useDropzone.mockReturnValue({
      getRootProps: () => ({ role: 'presentation' }),
      getInputProps: () => ({}),
      isDragActive: false
    });
  });

  it('renders basic uploader state', () => {
    render(<FileUploader onFileSelect={mockOnFileSelect} uploading={false} />)
    
    expect(screen.getByText('📁 Drag & drop a file here')).toBeInTheDocument()
    expect(screen.getByText('or click to select')).toBeInTheDocument()
    expect(screen.getByText('Supported: PDF, DOCX, TXT, MD (max 10MB)')).toBeInTheDocument()
  })

  it('shows uploading state', () => {
    render(<FileUploader onFileSelect={mockOnFileSelect} uploading={true} />)
    
    expect(screen.getByText('Uploading and processing...')).toBeInTheDocument()
  })

  it('handles file selection', async () => {
    const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
    let onDropCallback;
    mocks.useDropzone.mockImplementation((options) => {
      onDropCallback = options.onDrop;
      return {
        getRootProps: () => ({
          className: ''
        }),
        getInputProps: () => ({
          disabled: false
        }),
        isDragActive: false
      };
    });

    render(<FileUploader onFileSelect={mockOnFileSelect} uploading={false} />);

    // Simulate file drop
    await act(async () => {
      onDropCallback([file]);
    });

    expect(mockOnFileSelect).toHaveBeenCalledWith(file);
  });

  it('shows drag active state', () => {
    mocks.useDropzone.mockReturnValue({
      getRootProps: () => ({
        className: ''
      }),
      getInputProps: () => ({
        disabled: false
      }),
      isDragActive: true
    });

    render(<FileUploader onFileSelect={mockOnFileSelect} uploading={false} />)
    
    expect(screen.getByText('Drop the file here...')).toBeInTheDocument()
  })

  it('disables upload during uploading state', () => {
    render(<FileUploader onFileSelect={mockOnFileSelect} uploading={true} />)
    
    const container = screen.getByText('Uploading and processing...').closest('div');
    const dropzoneRoot = container.closest('[role="presentation"]');
    expect(dropzoneRoot).toHaveClass('opacity-50');
    expect(dropzoneRoot).toHaveClass('cursor-not-allowed');
  })

  it('validates file size', async () => {
    // Create a mock file larger than 10MB
    const largeFile = new File(['x'.repeat(11 * 1024 * 1024)], 'large.txt', { type: 'text/plain' });
    
    render(<FileUploader onFileSelect={mockOnFileSelect} uploading={false} />);

    // Verify maxSize is passed correctly in the hook call
    expect(mocks.useDropzone).toHaveBeenCalledWith(
      expect.objectContaining({
        maxSize: 10 * 1024 * 1024
      })
    );
  });

  it('validates file type', async () => {
    render(<FileUploader onFileSelect={mockOnFileSelect} uploading={false} />);

    // Verify dropzone was called with correct accept options
    expect(mocks.useDropzone).toHaveBeenCalledWith(
      expect.objectContaining({
        accept: {
          'application/pdf': ['.pdf'],
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
          'text/plain': ['.txt'],
          'text/markdown': ['.md']
        }
      })
    );
  });
})