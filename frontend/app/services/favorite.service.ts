import { API_ENDPOINTS } from '~/constants/api'
import type { ApiResponse, FavoriteStatus, Page, PropertySummary } from '~/types/models'
import type { ApiRequest } from './http'

export function createFavoriteService(request: ApiRequest) {
  const endpoints = API_ENDPOINTS.favorites
  return {
    list: (page: number, size: number) => request<Page<PropertySummary>>(endpoints.list, { query: { page, size } }),
    async ids(): Promise<number[]> {
      return (await request<ApiResponse<number[]>>(endpoints.ids)).data
    },
    async add(propertyId: number): Promise<FavoriteStatus> {
      return (await request<ApiResponse<FavoriteStatus>>(endpoints.toggle(propertyId), { method: 'POST' })).data
    },
    async remove(propertyId: number): Promise<FavoriteStatus> {
      return (await request<ApiResponse<FavoriteStatus>>(endpoints.toggle(propertyId), { method: 'DELETE' })).data
    },
  }
}

export type FavoriteService = ReturnType<typeof createFavoriteService>
