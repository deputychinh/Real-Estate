// Friendly names over the generated OpenAPI types. Never edit api.generated.ts by hand.
import type { components } from './api.generated'
import type { ListingPurpose, PropertySort, PropertyType, Currency, PropertyStatus, InquiryStatus } from '~/enums'

type Schemas = components['schemas']

export type PropertySummary = Schemas['PropertySummary']
export type PropertyDetail = Schemas['PropertyDetail']
export type PropertyCreate = Schemas['PropertyCreate']
export type PropertyUpdate = Schemas['PropertyUpdate']
export type ImageIn = Schemas['ImageIn']
export type CityRead = Schemas['CityRead']
export type CountryRead = Schemas['CountryRead']
export type AmenityRead = Schemas['AmenityRead']
export type UserRead = Schemas['UserRead']
export type AccessTokenResponse = Schemas['AccessTokenResponse']
export type RegisterRequest = Schemas['RegisterRequest']
export type LoginRequest = Schemas['LoginRequest']
export type InquiryRead = Schemas['InquiryRead']
export type InquiryCreate = Schemas['InquiryCreate']
export type FavoriteStatus = Schemas['FavoriteStatus']
export type RatesRead = Schemas['RatesRead']
export type PageMeta = Schemas['PageMeta']

/** `{"data": {...}}` */
export interface ApiResponse<T> {
  data: T
}

/** `{"data": [...], "meta": {...}}` */
export interface Page<T> {
  data: T[]
  meta: PageMeta
}

/** Search filters as they appear in the URL (plan: filters are shareable, FR-04). */
export interface SearchQuery {
  purpose?: ListingPurpose
  property_type?: PropertyType
  country?: string
  city?: string
  price_min?: number
  price_max?: number
  price_currency?: Currency
  bedrooms_min?: number
  q?: string
  sort?: PropertySort
  page?: number
  size?: number
}

export interface AgentListingQuery {
  status?: PropertyStatus
  page?: number
  size?: number
}

export interface InquiryQuery {
  status?: InquiryStatus
  page?: number
  size?: number
}
