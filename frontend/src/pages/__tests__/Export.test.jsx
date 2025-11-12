import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Export from '../Export'
import { api } from '../../api/client'
import { toast } from 'react-toastify'
import useSessionStore from '../../store/useSessionStore'
import { downloadFile } from '../../utils/formatters'

// Mock dependencies
vi.mock('../../api/client', () => ({
  api: {
    exportDOCX: vi.fn(),
    exportMarkdown: vi.fn()
  }
}))

vi.mock('react-toastify', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn()
  }
}))

vi.mock('../../utils/formatters', () => ({
  downloadFile: vi.fn()
}))

vi.mock('../../store/useSessionStore', () => ({
  default: vi.fn()
}))

vi.mock('../components/Layout/SessionHeader', () => ({
  default: () => <div data-testid="session-header">Session Header</div>
}))

// Helper function to render with router
const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

describe('Export Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows warning when no session is selected', () => {
    useSessionStore.mockReturnValue({ currentSessionId: null })
    
    renderWithRouter(<Export />)
    
    expect(screen.getByText(/Please select a session/)).toBeInTheDocument()
  })

  describe('With Active Session', () => {
    const mockSessionId = 'test-session-123'
    
    beforeEach(() => {
      useSessionStore.mockReturnValue({ currentSessionId: mockSessionId })
    })

    it('renders export options correctly', () => {
      renderWithRouter(<Export />)
      
      expect(screen.getByText('Export 📥')).toBeInTheDocument()
      expect(screen.getByText('Microsoft Word (DOCX)')).toBeInTheDocument()
      expect(screen.getByText('Markdown (MD)')).toBeInTheDocument()
    })

    it('handles DOCX export successfully', async () => {
      const mockResponse = { data: 'mock-docx-data' }
      api.exportDOCX.mockResolvedValueOnce(mockResponse)
      
      renderWithRouter(<Export />)
      
      // Select DOCX format
      const docxRadio = screen.getByTestId('docx-radio')
      fireEvent.click(docxRadio)
      
      // Click export button
      const exportButton = screen.getByRole('button')
      fireEvent.click(exportButton)
      
      await waitFor(() => {
        expect(api.exportDOCX).toHaveBeenCalledWith(mockSessionId)
        expect(downloadFile).toHaveBeenCalledWith(
          mockResponse.data,
          `use_cases_${mockSessionId}.docx`
        )
        expect(toast.success).toHaveBeenCalledWith('DOCX exported successfully!')
      })
    })

    it('handles Markdown export successfully', async () => {
      const mockResponse = { data: 'mock-markdown-data' }
      api.exportMarkdown.mockResolvedValueOnce(mockResponse)
      
      renderWithRouter(<Export />)
      
      // Select Markdown format
      const markdownRadio = screen.getByTestId('markdown-radio')
      fireEvent.click(markdownRadio)
      
      // Click export button
      const exportButton = screen.getByRole('button')
      fireEvent.click(exportButton)
      
      await waitFor(() => {
        expect(api.exportMarkdown).toHaveBeenCalledWith(mockSessionId)
        expect(downloadFile).toHaveBeenCalledWith(
          mockResponse.data,
          `use_cases_${mockSessionId}.md`
        )
        expect(toast.success).toHaveBeenCalledWith('Markdown exported successfully!')
      })
    })

  

    it('handles export errors', async () => {
      const mockError = new Error('Export failed')
      api.exportDOCX.mockRejectedValueOnce(mockError)
      
      renderWithRouter(<Export />)
      
      const exportButton = screen.getByRole('button')
      fireEvent.click(exportButton)
      
      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('Export failed')
      })
    })

    it('disables export button while exporting', async () => {
      // Mock a delayed response to test loading state
      api.exportDOCX.mockImplementationOnce(() => new Promise(resolve => setTimeout(resolve, 100)))
      
      renderWithRouter(<Export />)
      
      const exportButton = screen.getByText('📥 Export as DOCX')
      fireEvent.click(exportButton)
      
      // Button should be disabled and show loading state
      expect(screen.getByText('⏳ Exporting...')).toBeInTheDocument()
      expect(screen.getByRole('button')).toBeDisabled()
      
      // Wait for export to complete
      await waitFor(() => {
        expect(screen.queryByText('⏳ Exporting...')).not.toBeInTheDocument()
      })
    })

    it('renders session header when session is selected', () => {
      renderWithRouter(<Export />)
      expect(screen.getByText(/Session/)).toBeInTheDocument()
    })

    it('shows info message about export scope', () => {
      renderWithRouter(<Export />)
      expect(screen.getByText(/The export will include all use cases from the current session/)).toBeInTheDocument()
    })

    it('updates format when different option is selected', () => {
      renderWithRouter(<Export />)
      
      // Initially should show DOCX format
      const exportButton = screen.getByRole('button')
      expect(exportButton).toHaveTextContent('📥 Export as DOCX')
      
      // Select Markdown format
      const markdownRadio = screen.getByTestId('markdown-radio')
      fireEvent.click(markdownRadio)
      
      // Button text should update
      expect(exportButton).toHaveTextContent('📥 Export as MARKDOWN')
    })
  })
})