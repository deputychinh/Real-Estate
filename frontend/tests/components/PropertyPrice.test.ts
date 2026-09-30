import { mountSuspended } from '@nuxt/test-utils/runtime'
import { describe, expect, it } from 'vitest'
import PropertyPrice from '~/components/property/PropertyPrice.vue'
import { Currency, ListingPurpose } from '~/enums'
import { usePreferencesStore } from '~/stores/preferences.store'

describe('PropertyPrice', () => {
  it('converts to the viewer currency and keeps the original price visible', async () => {
    useExchangeRates().value = { base: Currency.USD, usd_per_unit: { USD: '1', AED: '0.2723' } as never, as_of: '2026-09-01', source: 'static' }
    usePreferencesStore().currency = Currency.USD
    const price = await mountSuspended(PropertyPrice, {
      props: { price: '1000000.00', currency: Currency.AED, purpose: ListingPurpose.SALE },
    })
    expect(price.find('.price__amount').text()).toBe('$272,300')
    // Intl puts a no-break space between the currency code and the amount.
    expect(price.find('.price__original').text().replace(/\s/g, ' ')).toBe('≈ AED 1,000,000')
  })
})
