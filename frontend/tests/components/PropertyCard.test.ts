import { mountSuspended } from '@nuxt/test-utils/runtime'
import { beforeEach, describe, expect, it } from 'vitest'
import PropertyCard from '~/components/property/PropertyCard.vue'
import { ListingPurpose, PropertyStatus } from '~/enums'
import { makeSummary } from './fixtures'

describe('PropertyCard', () => {
  beforeEach(() => {
    useExchangeRates().value = null // show prices in the listing currency
  })

  it('shows the key facts of a listing', async () => {
    const card = await mountSuspended(PropertyCard, { props: { property: makeSummary() } })
    const text = card.text()
    expect(text).toContain('Sunny villa in Dubai Marina')
    expect(text).toContain('For Sale')
    expect(text).toContain('Featured')
    expect(text).toContain('Dubai, United Arab Emirates')
    expect(text).toContain('320 m²')
    expect(text).toContain('AED')
    expect(card.find('a[href="/properties/sunny-villa-dubai"]').exists()).toBe(true)
  })

  it('marks rentals per month and flags listings that are no longer available', async () => {
    const card = await mountSuspended(PropertyCard, {
      props: { property: makeSummary({ purpose: ListingPurpose.RENT, status: PropertyStatus.RENTED, is_featured: false }) },
    })
    expect(card.text()).toContain('/ month')
    expect(card.text()).toContain('Rented')
    expect(card.text()).not.toContain('Featured')
  })
})
