import { usePreferencesStore } from '~/stores/preferences.store'
import type { Currency } from '~/enums'
import type { RatesRead } from '~/types/models'
import { convertAmount, formatMoney } from '~/utils/format'

/** Rates are loaded once per request (app.vue) and shared through useState, so SSR and client agree. */
export function useExchangeRates() {
  return useState<RatesRead | null>('fx-rates', () => null)
}

export function useCurrency() {
  const preferences = usePreferencesStore()
  const rates = useExchangeRates()

  /** Price in the viewer's currency when rates are known; otherwise in the listing's own currency. */
  function display(amount: number | string, currency: Currency | string, compact = false): string {
    const value = Number(amount)
    const target = preferences.currency
    if (!rates.value || currency === target) return formatMoney(value, currency, compact)
    return formatMoney(convertAmount(value, currency, target, rates.value.usd_per_unit), target, compact)
  }

  function original(amount: number | string, currency: Currency | string): string {
    return formatMoney(Number(amount), currency)
  }

  return { currency: computed(() => preferences.currency), display, original }
}
