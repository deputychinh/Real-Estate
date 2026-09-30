import { AreaUnit, Currency, ListingPurpose, PropertyStatus, PropertyType } from '~/enums'
import type { PropertySummary } from '~/types/models'

export function makeSummary(overrides: Partial<PropertySummary> = {}): PropertySummary {
  return {
    id: 7,
    slug: 'sunny-villa-dubai',
    title: 'Sunny villa in Dubai Marina',
    purpose: ListingPurpose.SALE,
    property_type: PropertyType.VILLA,
    status: PropertyStatus.PUBLISHED,
    price: '1000000.00',
    currency: Currency.AED,
    price_usd: '272300.00',
    area: '320.00',
    area_unit: AreaUnit.SQM,
    bedrooms: 4,
    bathrooms: 3,
    city: { id: 1, name: 'Dubai', slug: 'dubai', country_code: 'AE', country_name: 'United Arab Emirates' },
    cover_image_url: 'https://img.example.com/villa.jpg',
    is_featured: true,
    published_at: '2026-09-01T00:00:00Z',
    ...overrides,
  }
}
