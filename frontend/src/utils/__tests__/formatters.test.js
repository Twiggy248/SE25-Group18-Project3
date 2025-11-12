import { describe, it, expect, vi } from 'vitest'
import {
  formatDate,
  getQualityColor,
  getQualityLabel,
  truncateText,
  downloadFile
} from '../formatters'

describe('formatDate', () => {
  it('formats valid date strings correctly', () => {
    const date = new Date('2025-11-04T12:00:00Z')
    const formatted = formatDate(date.toISOString())
    expect(formatted).toMatch(/^Nov 04, 2025 \d{2}:\d{2}$/)
  })

  it('returns N/A for null or undefined dates', () => {
    expect(formatDate(null)).toBe('N/A')
    expect(formatDate(undefined)).toBe('N/A')
  })

  it('returns original string for invalid dates', () => {
    const invalidDate = 'not-a-date'
    expect(formatDate(invalidDate)).toBe(invalidDate)
  })
})

describe('getQualityColor', () => {
  it('returns green for scores >= 80', () => {
    expect(getQualityColor(80)).toBe('text-green-600 bg-green-100')
    expect(getQualityColor(90)).toBe('text-green-600 bg-green-100')
    expect(getQualityColor(100)).toBe('text-green-600 bg-green-100')
  })

  it('returns yellow for scores >= 60 and < 80', () => {
    expect(getQualityColor(60)).toBe('text-yellow-600 bg-yellow-100')
    expect(getQualityColor(70)).toBe('text-yellow-600 bg-yellow-100')
    expect(getQualityColor(79)).toBe('text-yellow-600 bg-yellow-100')
  })

  it('returns red for scores < 60', () => {
    expect(getQualityColor(0)).toBe('text-red-600 bg-red-100')
    expect(getQualityColor(59)).toBe('text-red-600 bg-red-100')
  })
})

describe('getQualityLabel', () => {
  it('returns Excellent for scores >= 80', () => {
    expect(getQualityLabel(80)).toBe('Excellent')
    expect(getQualityLabel(90)).toBe('Excellent')
    expect(getQualityLabel(100)).toBe('Excellent')
  })

  it('returns Good for scores >= 60 and < 80', () => {
    expect(getQualityLabel(60)).toBe('Good')
    expect(getQualityLabel(70)).toBe('Good')
    expect(getQualityLabel(79)).toBe('Good')
  })

  it('returns Needs Improvement for scores < 60', () => {
    expect(getQualityLabel(0)).toBe('Needs Improvement')
    expect(getQualityLabel(59)).toBe('Needs Improvement')
  })
})

describe('truncateText', () => {
  it('truncates text that exceeds maxLength', () => {
    const longText = 'a'.repeat(150)
    expect(truncateText(longText, 100)).toBe('a'.repeat(100) + '...')
  })

  it('returns original text when length is within maxLength', () => {
    const shortText = 'short text'
    expect(truncateText(shortText, 100)).toBe(shortText)
  })

  it('handles null or undefined text', () => {
    expect(truncateText(null)).toBeNull()
    expect(truncateText(undefined)).toBeUndefined()
  })

  it('uses default maxLength when not provided', () => {
    const longText = 'a'.repeat(150)
    expect(truncateText(longText)).toBe('a'.repeat(100) + '...')
  })
})

describe('downloadFile', () => {
  let mockLink
  
  beforeEach(() => {
    mockLink = {
      href: '',
      download: '',
      click: vi.fn()
    }
    
    vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob-url')
    vi.spyOn(URL, 'revokeObjectURL')
    vi.spyOn(document.body, 'appendChild').mockImplementation(() => {})
    vi.spyOn(document.body, 'removeChild').mockImplementation(() => {})
    vi.spyOn(document, 'createElement').mockReturnValue(mockLink)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('creates and clicks download link with correct attributes', () => {
    const blob = new Blob(['test'])
    const filename = 'test.txt'

    downloadFile(blob, filename)

    expect(URL.createObjectURL).toHaveBeenCalledWith(blob)
    expect(mockLink.href).toBe('blob-url')
    expect(mockLink.download).toBe(filename)
    expect(mockLink.click).toHaveBeenCalled()
    expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob-url')
  })
})