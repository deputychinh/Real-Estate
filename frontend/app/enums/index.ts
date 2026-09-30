// Domain enums come from the backend's OpenAPI schema (npm run gen:api), so the two sides cannot drift.
// This file adds UI labels and the few enums that only exist in the browser.
import {
  AreaUnit,
  Currency,
  ErrorCode,
  InquiryStatus,
  ListingPurpose,
  PropertySort,
  PropertyStatus,
  PropertyType,
  RegisterRequestRole as SignupRole,
  UserRole,
} from '~/types/api.generated'

export {
  AreaUnit,
  Currency,
  ErrorCode,
  InquiryStatus,
  ListingPurpose,
  PropertySort,
  PropertyStatus,
  PropertyType,
  SignupRole,
  UserRole,
}

export enum ViewMode {
  GRID = 'grid',
  LIST = 'list',
}

/** Browser-only error codes (no HTTP response to read a server code from). */
export enum ClientErrorCode {
  NETWORK_ERROR = 'NETWORK_ERROR',
}

export const LISTING_PURPOSE_LABEL: Record<ListingPurpose, string> = {
  [ListingPurpose.SALE]: 'For Sale',
  [ListingPurpose.RENT]: 'For Rent',
}

export const PROPERTY_TYPE_LABEL: Record<PropertyType, string> = {
  [PropertyType.APARTMENT]: 'Apartment',
  [PropertyType.HOUSE]: 'House',
  [PropertyType.VILLA]: 'Villa',
  [PropertyType.OFFICE]: 'Office',
  [PropertyType.LAND]: 'Land',
  [PropertyType.COMMERCIAL]: 'Commercial',
}

export const PROPERTY_STATUS_LABEL: Record<PropertyStatus, string> = {
  [PropertyStatus.DRAFT]: 'Draft',
  [PropertyStatus.PUBLISHED]: 'Published',
  [PropertyStatus.SOLD]: 'Sold',
  [PropertyStatus.RENTED]: 'Rented',
  [PropertyStatus.ARCHIVED]: 'Archived',
}

export const INQUIRY_STATUS_LABEL: Record<InquiryStatus, string> = {
  [InquiryStatus.NEW]: 'New',
  [InquiryStatus.CONTACTED]: 'Contacted',
  [InquiryStatus.CLOSED]: 'Closed',
}

export const PROPERTY_SORT_LABEL: Record<PropertySort, string> = {
  [PropertySort.NEWEST]: 'Newest first',
  [PropertySort.PRICE_ASC]: 'Price: low to high',
  [PropertySort.PRICE_DESC]: 'Price: high to low',
  [PropertySort.AREA_DESC]: 'Largest first',
}

export const AREA_UNIT_LABEL: Record<AreaUnit, string> = {
  [AreaUnit.SQM]: 'm²',
  [AreaUnit.SQFT]: 'ft²',
}

// Next statuses the dashboard offers (same rules as backend properties/state_machine.py).
export const NEXT_PROPERTY_STATUSES: Record<PropertyStatus, PropertyStatus[]> = {
  [PropertyStatus.DRAFT]: [PropertyStatus.PUBLISHED, PropertyStatus.ARCHIVED],
  [PropertyStatus.PUBLISHED]: [PropertyStatus.SOLD, PropertyStatus.RENTED, PropertyStatus.DRAFT, PropertyStatus.ARCHIVED],
  [PropertyStatus.RENTED]: [PropertyStatus.PUBLISHED, PropertyStatus.ARCHIVED],
  [PropertyStatus.SOLD]: [PropertyStatus.ARCHIVED],
  [PropertyStatus.ARCHIVED]: [PropertyStatus.DRAFT],
}

export const NEXT_INQUIRY_STATUSES: Record<InquiryStatus, InquiryStatus[]> = {
  [InquiryStatus.NEW]: [InquiryStatus.CONTACTED, InquiryStatus.CLOSED],
  [InquiryStatus.CONTACTED]: [InquiryStatus.CLOSED],
  [InquiryStatus.CLOSED]: [],
}
