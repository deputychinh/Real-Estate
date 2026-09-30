import { defineStore } from 'pinia'
import { COOKIE_MAX_AGE_SECONDS, DEFAULT_CURRENCY } from '~/constants/app'
import { STORAGE_KEYS } from '~/constants/storage-keys'
import { Currency, ViewMode } from '~/enums'

/** Display preferences in cookies, so the server renders the same currency and view as the browser. */
export const usePreferencesStore = defineStore('preferences', () => {
  const currencyCookie = useCookie<string>(STORAGE_KEYS.currency, {
    default: () => DEFAULT_CURRENCY,
    maxAge: COOKIE_MAX_AGE_SECONDS,
    sameSite: 'lax',
  })
  const viewCookie = useCookie<string>(STORAGE_KEYS.viewMode, {
    default: () => ViewMode.GRID,
    maxAge: COOKIE_MAX_AGE_SECONDS,
    sameSite: 'lax',
  })

  const currency = computed<Currency>({
    get: () => (Object.values(Currency).includes(currencyCookie.value as Currency) ? (currencyCookie.value as Currency) : DEFAULT_CURRENCY),
    set: (value) => {
      currencyCookie.value = value
    },
  })
  const viewMode = computed<ViewMode>({
    get: () => (viewCookie.value === ViewMode.LIST ? ViewMode.LIST : ViewMode.GRID),
    set: (value) => {
      viewCookie.value = value
    },
  })

  return { currency, viewMode }
})
