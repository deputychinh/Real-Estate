import { describe, expect, it } from 'vitest'
import { AreaUnit, Currency } from '~/enums'
import { convertAmount, formatArea, formatDate, formatMoney } from '~/utils/format'

const RATES = { USD: '1', EUR: '1.08', VND: '0.0000395', AED: '0.2723' }

describe('formatMoney', () => {
  it('formats by currency without cents for property prices', () => {
    expect(formatMoney(250000, Currency.USD)).toBe('$250,000')
    expect(formatMoney(9_000_000_000, Currency.VND)).toBe('₫9,000,000,000')
    expect(formatMoney(12.5, Currency.EUR)).toBe('€12.50')
  })

  it('supports a compact form', () => {
    expect(formatMoney(2_500_000, Currency.USD, true)).toBe('$2.5M')
  })
})

describe('convertAmount', () => {
  it('converts through USD', () => {
    expect(convertAmount(1_000_000, Currency.AED, Currency.USD, RATES)).toBeCloseTo(272_300)
    expect(convertAmount(108, Currency.USD, Currency.EUR, RATES)).toBeCloseTo(100)
  })

  it('returns the amount unchanged when a rate is missing', () => {
    expect(convertAmount(100, Currency.GBP, Currency.USD, RATES)).toBe(100)
    expect(convertAmount(100, Currency.USD, Currency.USD, RATES)).toBe(100)
  })
})

describe('formatArea / formatDate', () => {
  it('formats area with its unit', () => {
    expect(formatArea('95.50', AreaUnit.SQM)).toBe('96 m²')
    expect(formatArea(1200, AreaUnit.SQFT)).toBe('1,200 ft²')
  })

  it('formats dates in UTC and handles missing values', () => {
    expect(formatDate('2026-09-01T23:30:00Z')).toBe('1 Sept 2026')
    expect(formatDate(null)).toBe('—')
  })
})
