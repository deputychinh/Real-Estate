import { API_ENDPOINTS } from '~/constants/api'
import type { AmenityRead, ApiResponse, CityRead, CountryRead, RatesRead } from '~/types/models'
import type { ApiRequest } from './http'

export function createLookupService(request: ApiRequest) {
  const endpoints = API_ENDPOINTS.lookups
  return {
    async countries(): Promise<CountryRead[]> {
      return (await request<ApiResponse<CountryRead[]>>(endpoints.countries)).data
    },
    async cities(country?: string): Promise<CityRead[]> {
      return (await request<ApiResponse<CityRead[]>>(endpoints.cities, { query: country ? { country } : {} })).data
    },
    async amenities(): Promise<AmenityRead[]> {
      return (await request<ApiResponse<AmenityRead[]>>(endpoints.amenities)).data
    },
    async rates(): Promise<RatesRead> {
      return (await request<ApiResponse<RatesRead>>(endpoints.rates)).data
    },
  }
}

export type LookupService = ReturnType<typeof createLookupService>
