import { InquiryStatus, ListingPurpose, PropertyStatus } from '~/enums'

// Same values as assets/styles/_tokens.scss, for the few places that need a colour in TypeScript.
export const COLORS = {
  primary: '#ff5c41',
  primaryDark: '#e0452b',
  secondary: '#1c2d3a',
  success: '#2e9e4f',
  info: '#2f80ed',
  warning: '#b87306',
  danger: '#d93a2b',
} as const

export type BadgeTone = 'primary' | 'success' | 'info' | 'warning' | 'danger' | 'neutral'

// Status → colour lives here only; components never hard-code it (plan §7.5).
export const PROPERTY_STATUS_TONE: Record<PropertyStatus, BadgeTone> = {
  [PropertyStatus.DRAFT]: 'warning',
  [PropertyStatus.PUBLISHED]: 'success',
  [PropertyStatus.SOLD]: 'danger',
  [PropertyStatus.RENTED]: 'info',
  [PropertyStatus.ARCHIVED]: 'neutral',
}

export const LISTING_PURPOSE_TONE: Record<ListingPurpose, BadgeTone> = {
  [ListingPurpose.SALE]: 'primary',
  [ListingPurpose.RENT]: 'success',
}

export const INQUIRY_STATUS_TONE: Record<InquiryStatus, BadgeTone> = {
  [InquiryStatus.NEW]: 'primary',
  [InquiryStatus.CONTACTED]: 'info',
  [InquiryStatus.CLOSED]: 'neutral',
}
