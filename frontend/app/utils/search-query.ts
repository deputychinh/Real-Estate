import type { LocationQuery, LocationQueryRaw, LocationQueryValue } from 'vue-router'
import { Currency, ListingPurpose, PropertySort, PropertyType } from '~/enums'
import type { SearchQuery } from '~/types/models'

type QueryValue = LocationQueryValue | LocationQueryValue[] | undefined

// URL ⇄ filters. Unknown or invalid values are dropped, so a hand-edited URL never breaks the page.

function one(value: QueryValue): string | undefined {
  const raw = Array.isArray(value) ? value[0] : value
  return raw === null || raw === undefined || raw === '' ? undefined : String(raw)
}

function positiveNumber(value: QueryValue): number | undefined {
  const raw = one(value)
  if (raw === undefined) return undefined
  const parsed = Number(raw)
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : undefined
}

function member<T extends string>(values: readonly T[], value: QueryValue): T | undefined {
  const raw = one(value)
  return values.includes(raw as T) ? (raw as T) : undefined
}

export function parseSearchQuery(query: LocationQuery): SearchQuery {
  const page = positiveNumber(query.page)
  const bedrooms = positiveNumber(query.bedrooms_min)
  return {
    purpose: member(Object.values(ListingPurpose), query.purpose),
    property_type: member(Object.values(PropertyType), query.property_type),
    country: one(query.country)?.slice(0, 2).toUpperCase(),
    city: one(query.city),
    price_min: positiveNumber(query.price_min),
    price_max: positiveNumber(query.price_max),
    price_currency: member(Object.values(Currency), query.price_currency),
    bedrooms_min: bedrooms === undefined ? undefined : Math.floor(bedrooms),
    q: one(query.q)?.slice(0, 100),
    sort: member(Object.values(PropertySort), query.sort),
    page: page && page >= 1 ? Math.floor(page) : undefined,
  }
}

/** Only set values go into the URL, so links stay short and shareable. */
export function toRouteQuery(search: SearchQuery): LocationQueryRaw {
  return Object.fromEntries(
    Object.entries(search).filter(([key, value]) => {
      if (value === undefined || value === null || value === '') return false
      if (key === 'page' && value === 1) return false
      if (key === 'sort' && value === PropertySort.NEWEST) return false
      return true
    }),
  ) as LocationQueryRaw
}

export function activeFilterCount(search: SearchQuery): number {
  const ignored = new Set(['page', 'size', 'sort', 'price_currency'])
  return Object.entries(search).filter(([key, value]) => !ignored.has(key) && value !== undefined && value !== '')
    .length
}
