/** Reference data for selects. Cached by key, shared across components, fetched during SSR. */
export function useCountries() {
  const services = useServices()
  return useAsyncData('lookup:countries', () => services.lookups.countries(), { default: () => [] })
}

export function useCities(country: Ref<string | undefined>) {
  const services = useServices()
  return useAsyncData(
    () => `lookup:cities:${country.value ?? 'all'}`,
    () => services.lookups.cities(country.value),
    { default: () => [], watch: [country] },
  )
}

export function useAmenities() {
  const services = useServices()
  return useAsyncData('lookup:amenities', () => services.lookups.amenities(), { default: () => [] })
}
