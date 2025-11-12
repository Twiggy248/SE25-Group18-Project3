import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import UseCaseRefine from '../UseCaseRefine';
import { api } from '../../api/client';
import { toast } from 'react-toastify';
import useSessionStore from '../../store/useSessionStore';

// Mock dependencies
vi.mock('react-router-dom', () => ({
  useParams: vi.fn(),
  useLocation: vi.fn(),
  useNavigate: vi.fn()
}));

vi.mock('../../api/client', () => ({
  api: {
    getSessionHistory: vi.fn(),
    refineUseCase: vi.fn()
  }
}));

vi.mock('react-toastify', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn(),
    info: vi.fn()
  }
}));

vi.mock('../../store/useSessionStore', () => ({
  default: vi.fn()
}));

vi.mock('../../components/LoadingSpinner', () => ({
  default: ({ message }) => <div data-testid="loading-spinner">{message}</div>
}));

describe('UseCaseRefine Component', () => {
  const mockUseCase = {
    id: 123,
    title: 'Test Use Case',
    preconditions: ['Pre 1', 'Pre 2'],
    main_flow: ['Step 1', 'Step 2'],
    sub_flows: ['Sub 1', 'Sub 2'],
    alternate_flows: ['Alt 1', 'Alt 2'],
    outcomes: ['Outcome 1', 'Outcome 2'],
    stakeholders: ['User', 'Admin']
  };

  const mockRefinedUseCase = {
    ...mockUseCase,
    main_flow: ['Step 1 with more detail', 'Step 2 with more detail', 'Additional step'],
    alternate_flows: ['Alt 1', 'Alt 2', 'New alternative flow']
  };

  const mockSession = {
    currentSessionId: 'test-session-123'
  };

  const mockLocation = {
    state: { useCase: mockUseCase }
  };

  const navigate = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    useParams.mockReturnValue({ id: '123' });
    useLocation.mockReturnValue(mockLocation);
    useNavigate.mockReturnValue(navigate);
    useSessionStore.mockReturnValue(mockSession);
  });

  describe('Initial Rendering', () => {
    it('renders with use case from location state', () => {
      render(<UseCaseRefine />);
      
      expect(screen.getByText('Refine Use Case ✨')).toBeInTheDocument();
      expect(screen.getByText(mockUseCase.title)).toBeInTheDocument();
      expect(screen.getByText('Pre 1')).toBeInTheDocument();
      expect(screen.getByText('Step 1')).toBeInTheDocument();
    });

    it('shows loading state when fetching use case', () => {
      useLocation.mockReturnValue({ state: null });
      api.getSessionHistory.mockImplementationOnce(() => new Promise(() => {}));
      
      render(<UseCaseRefine />);
      
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
      expect(screen.getByText('Loading use case...')).toBeInTheDocument();
    });

    it('handles missing session', () => {
      useSessionStore.mockReturnValue({ currentSessionId: null });
      useLocation.mockReturnValue({ state: null });
      
      render(<UseCaseRefine />);
      
      expect(toast.error).toHaveBeenCalledWith('No active session. Please create or select a session first.');
      expect(navigate).toHaveBeenCalledWith('/');
    });
  });

  describe('Fallback Loading', () => {
    beforeEach(() => {
      useLocation.mockReturnValue({ state: null });
    });

    it('loads use case from session history', async () => {
      api.getSessionHistory.mockResolvedValueOnce({
        data: {
          conversation_history: [
            {
              metadata: {
                use_cases: [mockUseCase]
              }
            }
          ]
        }
      });
      
      render(<UseCaseRefine />);
      
      await waitFor(() => {
        expect(screen.getByText(mockUseCase.title)).toBeInTheDocument();
      });
    });

    it('handles use case not found in history', async () => {
      api.getSessionHistory.mockResolvedValueOnce({
        data: {
          conversation_history: [],
          generated_use_cases: [] // Test empty generated_use_cases as well
        }
      });
      
      render(<UseCaseRefine />);
      
      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('Use case not found in session history');
        expect(navigate).toHaveBeenCalledWith(-1);
      });
    });

    it('finds use case in generated_use_cases if not in conversation history', async () => {
      api.getSessionHistory.mockResolvedValueOnce({
        data: {
          conversation_history: [],
          generated_use_cases: [mockUseCase]
        }
      });
      
      render(<UseCaseRefine />);
      
      await waitFor(() => {
        expect(screen.getByText(mockUseCase.title)).toBeInTheDocument();
      });
    });

    it('handles loading error', async () => {
      api.getSessionHistory.mockRejectedValueOnce(new Error('Failed to load'));
      
      render(<UseCaseRefine />);
      
      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('Failed to load use case. Please try again.');
        expect(navigate).toHaveBeenCalledWith(-1);
      });
    });
  });

  describe('Refinement Options', () => {
    it('handles refinement type selection', async () => {
      render(<UseCaseRefine />);
      
      const addDetailRadio = screen.getByRole('radio', { name: /Add More Detail/i });
      const addAlternatesRadio = screen.getByRole('radio', { name: /Add Alternate Flows/i });
      const addErrorHandlingRadio = screen.getByRole('radio', { name: /Add Error Handling/i });
      
      await userEvent.click(addAlternatesRadio);
      expect(addAlternatesRadio).toBeChecked();
      expect(addDetailRadio).not.toBeChecked();
      
      await userEvent.click(addErrorHandlingRadio);
      expect(addErrorHandlingRadio).toBeChecked();
      expect(addAlternatesRadio).not.toBeChecked();
    });

    it('handles custom instruction input', async () => {
      render(<UseCaseRefine />);
      
      const customRadio = screen.getByRole('radio', { name: /Custom Instruction/i });
      const textarea = screen.getByPlaceholderText(/Example:/);
      
      await userEvent.click(customRadio);
      await userEvent.type(textarea, 'Add security checks');
      
      expect(customRadio).toBeChecked();
      expect(textarea.value).toBe('Add security checks');

      // Verify the refinement call includes custom instruction
      api.refineUseCase.mockResolvedValueOnce({
        data: { refined_use_case: mockRefinedUseCase }
      });

      const refineButton = screen.getByRole('button', { name: /Refine Use Case/i });
      await userEvent.click(refineButton);
      
      expect(api.refineUseCase).toHaveBeenCalledWith({
        use_case_id: 123,
        refinement_type: 'custom',
        custom_instruction: 'Add security checks'
      });
    });

    it('disables refinement button for empty custom instruction', async () => {
      render(<UseCaseRefine />);
      
      const customRadio = screen.getByLabelText('✏ Custom Instruction');
      await userEvent.click(customRadio);
      
      expect(screen.getByText('✨ Refine Use Case')).toBeDisabled();

      // Verify button enables when instruction is added
      const textarea = screen.getByPlaceholderText(/Example:/);
      await userEvent.type(textarea, 'Test instruction');
      expect(screen.getByText('✨ Refine Use Case')).not.toBeDisabled();

      // Verify button disables when instruction is cleared
      await userEvent.clear(textarea);
      expect(screen.getByText('✨ Refine Use Case')).toBeDisabled();
    });

    it('preserves custom instruction when switching between refinement types', async () => {
      render(<UseCaseRefine />);
      
      // Enter custom instruction
      const customRadio = screen.getByRole('radio', { name: /Custom Instruction/i });
      const textarea = screen.getByPlaceholderText(/Example:/);
      await userEvent.click(customRadio);
      await userEvent.type(textarea, 'Test instruction');
      
      // Switch to another type and back
      const addDetailRadio = screen.getByRole('radio', { name: /Add More Detail/i });
      await userEvent.click(addDetailRadio);
      await userEvent.click(customRadio);
      
      // Verify instruction is preserved
      expect(textarea.value).toBe('Test instruction');
    });
  });

  describe('Refinement Process', () => {
    it('handles successful refinement', async () => {
      api.refineUseCase.mockResolvedValueOnce({
        data: { refined_use_case: mockRefinedUseCase }
      });
      
      render(<UseCaseRefine />);
      
      await userEvent.click(screen.getByText('✨ Refine Use Case'));
      
      await waitFor(() => {
        expect(screen.getByText('Step 1 with more detail')).toBeInTheDocument();
        expect(screen.getByText('New alternative flow')).toBeInTheDocument();
        expect(toast.success).toHaveBeenCalledWith('✨ Use case refined successfully!');
      });
    });

    it('shows loading state during refinement', async () => {
      api.refineUseCase.mockImplementationOnce(() => new Promise(() => {}));
      
      render(<UseCaseRefine />);
      
      const refineButton = screen.getByRole('button', { name: /Refine Use Case/i });
      await userEvent.click(refineButton);
      
      expect(screen.getByText('Refining with AI...')).toBeInTheDocument();
      expect(refineButton).toBeDisabled();
    });

    it('handles refinement error', async () => {
      api.refineUseCase.mockRejectedValueOnce({
        response: { data: { detail: 'Refinement failed' } }
      });
      
      render(<UseCaseRefine />);
      
      await userEvent.click(screen.getByText('✨ Refine Use Case'));
      
      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('Refinement failed');
      });
    });
  });

  describe('Refined Use Case Actions', () => {
    beforeEach(async () => {
      api.refineUseCase.mockResolvedValueOnce({
        data: { refined_use_case: mockRefinedUseCase }
      });
      
      render(<UseCaseRefine />);
      await userEvent.click(screen.getByText('✨ Refine Use Case'));
      await waitFor(() => {
        expect(screen.getByText('✅ Refined Use Case')).toBeInTheDocument();
      });
    });

    it('handles accepting changes', async () => {
      await userEvent.click(screen.getByText('✅ Accept & Go Back'));
      
      expect(toast.success).toHaveBeenCalledWith('✅ Changes reviewed! Use case has been refined.');
      expect(toast.info).toHaveBeenCalledWith('💡 Tip: The refined version is now stored in your session.');
      expect(navigate).toHaveBeenCalledWith(-1);
    });

    it('handles refine again', async () => {
      await userEvent.click(screen.getByText('🔄 Refine Again'));
      
      expect(screen.getByText('✨ Refine Use Case')).toBeInTheDocument();
      expect(toast.info).toHaveBeenCalledWith('Select a new refinement option to refine again');
    });
  });

  describe('Navigation', () => {
    it('handles back button click', () => {
      render(<UseCaseRefine />);
      
      fireEvent.click(screen.getByText('Back'));
      expect(navigate).toHaveBeenCalledWith(-1);
    });
  });

  describe('Error States', () => {
    it('handles missing use case ID', async () => {
      const useCaseWithoutId = { ...mockUseCase };
      delete useCaseWithoutId.id;
      useLocation.mockReturnValue({ state: { useCase: useCaseWithoutId } });
      
      render(<UseCaseRefine />);
      
      await userEvent.click(screen.getByText('✨ Refine Use Case'));
      
      expect(toast.error).toHaveBeenCalledWith('Cannot refine: Use case ID is missing');
      expect(api.refineUseCase).not.toHaveBeenCalled();
    });

    it('shows error UI when use case not found', () => {
      useLocation.mockReturnValue({ state: null });
      api.getSessionHistory.mockResolvedValueOnce({
        data: { conversation_history: [] }
      });

      render(<UseCaseRefine />);

      waitFor(() => {
        expect(screen.getByText('❌ Use case not found')).toBeInTheDocument();
        const backButton = screen.getByText('← Go back');
        expect(backButton).toBeInTheDocument();
        
        fireEvent.click(backButton);
        expect(navigate).toHaveBeenCalledWith(-1);
      });
    });

    it('handles refinement error with custom message', async () => {
      api.refineUseCase.mockRejectedValueOnce({
        response: { data: { detail: 'Custom error message' } }
      });
      
      render(<UseCaseRefine />);
      
      await userEvent.click(screen.getByText('✨ Refine Use Case'));
      
      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('Custom error message');
      });
    });

    it('handles refinement error without response data', async () => {
      api.refineUseCase.mockRejectedValueOnce(new Error('Network error'));
      
      render(<UseCaseRefine />);
      
      await userEvent.click(screen.getByText('✨ Refine Use Case'));
      
      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('Refinement failed. Please try again.');
      });
    });
  });
});