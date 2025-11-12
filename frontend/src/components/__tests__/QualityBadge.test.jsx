import { describe, it, expect, vi } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'
import QualityBadge from '../QualityBadge'
import { getQualityColor, getQualityLabel } from '../../utils/formatters'

// Mock the formatters module
vi.mock('../../utils/formatters', () => ({
  getQualityColor: vi.fn(),
  getQualityLabel: vi.fn()
}))

describe('QualityBadge Component', () => {
  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks()
  })

  it('renders with high quality score', () => {
    const score = 90
    getQualityColor.mockReturnValue('bg-green-100 text-green-800')
    getQualityLabel.mockReturnValue('Excellent')
    
    render(<QualityBadge score={score} />)
    
    expect(screen.getByText(`Excellent (${score}/100)`)).toBeInTheDocument()
    expect(getQualityColor).toHaveBeenCalledWith(score)
    expect(getQualityLabel).toHaveBeenCalledWith(score)
  })

  it('renders with medium quality score', () => {
    const score = 70
    getQualityColor.mockReturnValue('bg-yellow-100 text-yellow-800')
    getQualityLabel.mockReturnValue('Good')
    
    render(<QualityBadge score={score} />)
    
    expect(screen.getByText(`Good (${score}/100)`)).toBeInTheDocument()
    expect(getQualityColor).toHaveBeenCalledWith(score)
    expect(getQualityLabel).toHaveBeenCalledWith(score)
  })

  it('renders with low quality score', () => {
    const score = 30
    getQualityColor.mockReturnValue('bg-red-100 text-red-800')
    getQualityLabel.mockReturnValue('Poor')
    
    render(<QualityBadge score={score} />)
    
    expect(screen.getByText(`Poor (${score}/100)`)).toBeInTheDocument()
    expect(getQualityColor).toHaveBeenCalledWith(score)
    expect(getQualityLabel).toHaveBeenCalledWith(score)
  })

  it('applies correct styling classes', () => {
    const score = 85
    const colorClass = 'bg-green-100 text-green-800'
    getQualityColor.mockReturnValue(colorClass)
    getQualityLabel.mockReturnValue('Excellent')
    
    render(<QualityBadge score={score} />)
    
    const badge = screen.getByText(`Excellent (${score}/100)`)
    expect(badge).toHaveClass(
      'px-3',
      'py-1',
      'rounded-full',
      'text-sm',
      'font-medium',
      ...colorClass.split(' ')
    )
  })

  it('handles edge case scores', () => {
    // Test score = 0
    getQualityColor.mockReturnValue('bg-red-100 text-red-800')
    getQualityLabel.mockReturnValue('Poor')
    render(<QualityBadge score={0} />)
    expect(screen.getByText('Poor (0/100)')).toBeInTheDocument()
    
    // Clean up previous render
    cleanup()
    
    // Test score = 100
    getQualityColor.mockReturnValue('bg-green-100 text-green-800')
    getQualityLabel.mockReturnValue('Excellent')
    render(<QualityBadge score={100} />)
    expect(screen.getByText('Excellent (100/100)')).toBeInTheDocument()
  })

  it('handles invalid scores gracefully', () => {
    // Test negative score
    const negativeScore = -10
    getQualityColor.mockReturnValue('bg-red-100 text-red-800')
    getQualityLabel.mockReturnValue('Invalid')
    
    render(<QualityBadge score={negativeScore} />)
    expect(screen.getByText(`Invalid (${negativeScore}/100)`)).toBeInTheDocument()
    
    // Clean up previous render
    cleanup()
    
    // Test score > 100
    const highScore = 110
    render(<QualityBadge score={highScore} />)
    expect(screen.getByText(`Invalid (${highScore}/100)`)).toBeInTheDocument()
  })
})