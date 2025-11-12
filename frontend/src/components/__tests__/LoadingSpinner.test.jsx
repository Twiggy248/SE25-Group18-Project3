import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import LoadingSpinner from '../LoadingSpinner'

describe('LoadingSpinner Component', () => {
  it('renders with default message', () => {
    render(<LoadingSpinner />)
    
    // Check if default loading message is present
    expect(screen.getByText('Loading...')).toBeInTheDocument()
    
    // Check if spinner element exists
    const spinner = screen.getByTestId('loading-spinner')
    expect(spinner).toBeInTheDocument()
    expect(spinner.firstChild).toHaveClass('animate-spin', 'rounded-full', 'border-b-2', 'border-primary')
  })

  it('renders with custom message', () => {
    const customMessage = 'Processing your request...'
    render(<LoadingSpinner message={customMessage} />)
    
    // Check if custom message is present
    expect(screen.getByText(customMessage)).toBeInTheDocument()
  })

  it('maintains proper structure and styling', () => {
    render(<LoadingSpinner />)
    
    // Check container styling
    const container = screen.getByTestId('loading-spinner')
    expect(container).toHaveClass('flex', 'flex-col', 'items-center', 'justify-center', 'p-8')
    
    // Check message styling
    const message = screen.getByText('Loading...')
    expect(message).toHaveClass('mt-4', 'text-gray-600')
  })

  it('renders message in correct position relative to spinner', () => {
    render(<LoadingSpinner />)
    
    const spinner = screen.getByTestId('loading-spinner').querySelector('.animate-spin')
    const message = screen.getByText('Loading...')
    
    // The message should be rendered after the spinner in the DOM
    expect(spinner.compareDocumentPosition(message)).toBe(Node.DOCUMENT_POSITION_FOLLOWING)
  })
})