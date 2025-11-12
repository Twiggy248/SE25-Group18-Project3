import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import UseCaseCard from '../UseCaseCard'
import { api } from '../../api/client'
import { toast } from 'react-toastify'

// Mock dependencies
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => vi.fn()
  }
})

vi.mock('../../api/client', () => ({
  api: {
    refineUseCase: vi.fn()
  }
}))

vi.mock('react-toastify', () => ({
  toast: {
    info: vi.fn(),
    success: vi.fn(),
    error: vi.fn()
  }
}))

// Sample use case data
const mockUseCase = {
  id: '123',
  title: 'Test Use Case',
  stakeholders: ['User', 'Admin'],
  preconditions: ['System is running', 'User is logged in'],
  main_flow: ['User opens app', 'User performs action'],
  sub_flows: ['Optional step 1', 'Optional step 2'],
  alternate_flows: ['Error handling 1', 'Error handling 2'],
  outcomes: ['Action completed', 'Data updated'],
  quality_score: 85
}

// Helper function to render with router
const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

describe('UseCaseCard Component', () => {
  const mockOnDelete = vi.fn()
  const mockOnRefined = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    api.refineUseCase.mockResolvedValue({ data: { success: true } })
  })

  it('renders basic use case information', () => {
    renderWithRouter(<UseCaseCard useCase={mockUseCase} />)
    
    expect(screen.getByText(mockUseCase.title)).toBeInTheDocument()
    expect(screen.getByText(mockUseCase.stakeholders.join(', '))).toBeInTheDocument()
    expect(screen.getByText('▶ Show Details')).toBeInTheDocument()
  })

  it('shows and hides details when toggled', () => {
    renderWithRouter(<UseCaseCard useCase={mockUseCase} />)
    
    // Initially details are hidden
    expect(screen.queryByText('Preconditions:')).not.toBeInTheDocument()
    
    // Click to show details
    fireEvent.click(screen.getByText('▶ Show Details'))
    
    // Details should be visible
    expect(screen.getByText('Preconditions:')).toBeInTheDocument()
    expect(screen.getByText(mockUseCase.preconditions[0])).toBeInTheDocument()
    
    // Click to hide details
    fireEvent.click(screen.getByText('▼ Hide Details'))
    
    // Details should be hidden again
    expect(screen.queryByText('Preconditions:')).not.toBeInTheDocument()
  })

  it('handles refinement process', async () => {
    api.refineUseCase.mockResolvedValueOnce({ data: { success: true } });
    
    renderWithRouter(
      <UseCaseCard
        useCase={mockUseCase}
        onRefined={mockOnRefined}
      />
    );
    
    // Click refine button
    fireEvent.click(screen.getByText('✨ Refine'));
    
    // Check if modal appears
    expect(screen.getByText('Refine Use Case')).toBeInTheDocument();
    
    // Select refinement type
    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: 'more_sub_flows' } });
    
    // Click refine in modal
    const refineButton = screen.getAllByRole('button').find(btn => 
      btn.textContent.includes('✨') && btn.textContent.includes('Refine')
    );
    fireEvent.click(refineButton);
    
    // Verify API call and notifications
    expect(api.refineUseCase).toHaveBeenCalledWith({
      use_case_id: mockUseCase.id,
      refinement_type: 'more_sub_flows'
    });
    
    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith('✨ Use case refined successfully!');
      expect(mockOnRefined).toHaveBeenCalled();
    });
  })

  it('handles refinement errors', async () => {
    const error = new Error('API Error');
    error.response = { data: { detail: 'Refinement failed' } };
    api.refineUseCase.mockRejectedValueOnce(error);
    
    renderWithRouter(
      <UseCaseCard
        useCase={mockUseCase}
        onRefined={mockOnRefined}
      />
    );
    
    // Click refine button to open modal
    fireEvent.click(screen.getByText('✨ Refine'));
    
    // Click the refine button in modal
    const modalRefineButton = screen.getAllByRole('button').find(btn => 
      btn.textContent.includes('✨') && btn.textContent.includes('Refine')
    );
    fireEvent.click(modalRefineButton);
    
    // Wait for error handling
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Refinement failed');
      expect(mockOnRefined).not.toHaveBeenCalled();
    });
  })

  it('handles deletion', () => {
    renderWithRouter(
      <UseCaseCard
        useCase={mockUseCase}
        onDelete={mockOnDelete}
      />
    )
    
    fireEvent.click(screen.getByText('Delete'))
    expect(mockOnDelete).toHaveBeenCalledWith(mockUseCase.id)
  })

  it('displays refined status correctly', () => {
    const refinedUseCase = { ...mockUseCase, _refined: true }
    renderWithRouter(<UseCaseCard useCase={refinedUseCase} />)
    
    expect(screen.getByText('✨ Refined')).toBeInTheDocument()
    expect(screen.getByTestId('use-case-card')).toHaveClass('border-green-400', 'bg-green-50')
  })

  it('handles missing optional data gracefully', () => {
    const minimalUseCase = {
      id: '123',
      title: 'Minimal Use Case'
    }
    
    renderWithRouter(<UseCaseCard useCase={minimalUseCase} />)
    
    expect(screen.getByText('Minimal Use Case')).toBeInTheDocument()
    expect(screen.getByText('N/A')).toBeInTheDocument() // For stakeholders
  })

  it('handles different flow formats', () => {
    const useCaseWithDifferentFlows = {
      ...mockUseCase,
      main_flows: [
        ['Step 1', 'Step 2'],
        { steps: ['Step 3', 'Step 4'] },
        'Single step flow'
      ]
    };
    
    renderWithRouter(<UseCaseCard useCase={useCaseWithDifferentFlows} />);
    
    // Show details
    fireEvent.click(screen.getByText('▶ Show Details'));
    
    // Check if all flow formats are rendered
    expect(screen.getByText('Step 1')).toBeInTheDocument();
    expect(screen.getByText('Step 3')).toBeInTheDocument();
    expect(screen.getByText('• Single step flow')).toBeInTheDocument();
  });

  it('disables refinement button while processing', async () => {
    // Create a promise that we can resolve manually
    let resolveRefine;
    const refinePromise = new Promise(resolve => {
      resolveRefine = () => resolve({ data: { success: true } });
    });

    api.refineUseCase.mockImplementationOnce(() => refinePromise);
    
    renderWithRouter(
      <UseCaseCard
        useCase={mockUseCase}
        onRefined={mockOnRefined}
      />
    );
    
    // Click refine button to open modal
    fireEvent.click(screen.getByText('✨ Refine'));
    
    // Click the refine button in modal
    const modalRefineButton = screen.getAllByRole('button').find(btn => 
      btn.textContent.includes('✨') && btn.textContent.includes('Refine')
    );
    fireEvent.click(modalRefineButton);
    
    // Button should be disabled and show loading state
    expect(modalRefineButton.disabled).toBe(true);
    expect(screen.getByText('⏳')).toBeInTheDocument();
    expect(screen.getByText('Refining')).toBeInTheDocument();

    // Resolve the refinement promise
    resolveRefine();

    // Wait for refinement to complete
    await waitFor(() => {
      expect(mockOnRefined).toHaveBeenCalled();
      expect(screen.queryByText('Refining...')).not.toBeInTheDocument();
    });
  })

  it('cancels refinement process correctly', () => {
    renderWithRouter(<UseCaseCard useCase={mockUseCase} />)
    
    // Open refinement modal
    fireEvent.click(screen.getByText('✨ Refine'))
    
    // Click cancel
    fireEvent.click(screen.getByText('Cancel'))
    
    // Modal should be closed
    expect(screen.queryByText('Refine Use Case')).not.toBeInTheDocument()
  })
})