import { describe, expect, it } from 'vitest'
import { Currency, ListingPurpose, PropertySort, PropertyType } from '~/enums'
import { activeFilterCount, parseSearchQuery, toRouteQuery } from '~/utils/search-query'

describe('parseSearchQuery', () => {
  it('reads valid filters from the URL', () => {
    const query = parseSearchQuery({
      purpose: 'RENT',
      property_type: 'VILLA',
      country: 'ae',
      price_min: '1000',
      price_currency: 'AED',
      bedrooms_min: '2.7',
      sort: 'PRICE_DESC',
      page: '3',
    })
    expect(query).toMatchObject({
      purpose: ListingPurpose.RENT,
      property_type: PropertyType.VILLA,
      country: 'AE',
      price_min: 1000,
      price_currency: Currency.AED,
      bedrooms_min: 2,
      sort: PropertySort.PRICE_DESC,
      page: 3,
    })
  })

  it('drops unknown or invalid values instead of breaking the page', () => {
    const query = parseSearchQuery({ purpose: 'LEASE', price_min: '-5', page: 'abc', sort: 'RANDOM', q: '' })
    expect(query.purpose).toBeUndefined()
    expect(query.price_min).toBeUndefined()
    expect(query.page).toBeUndefined()
    expect(query.sort).toBeUndefined()
    expect(query.q).toBeUndefined()
  })

  it('uses the first value when a key repeats', () => {
    expect(parseSearchQuery({ city: ['dubai', 'london'] }).city).toBe('dubai')
  })
})

describe('toRouteQuery', () => {
  it('keeps URLs short: no empty values, no default page or sort', () => {
    expect(
      toRouteQuery({ purpose: ListingPurpose.SALE, city: undefined, q: '', page: 1, sort: PropertySort.NEWEST }),
    ).toEqual({ purpose: 'SALE' })
    expect(toRouteQuery({ page: 2, sort: PropertySort.PRICE_ASC })).toEqual({ page: 2, sort: 'PRICE_ASC' })
  })
})

describe('activeFilterCount', () => {
  it('counts real filters only', () => {
    expect(activeFilterCount({ purpose: ListingPurpose.SALE, city: 'dubai', page: 2, sort: PropertySort.PRICE_ASC })).toBe(2)
  })
})
