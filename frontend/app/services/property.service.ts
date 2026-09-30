import { API_ENDPOINTS } from '~/constants/api'
import type { PropertyStatus } from '~/enums'
import type {
  AgentListingQuery,
  ApiResponse,
  Page,
  PropertyCreate,
  PropertyDetail,
  PropertySummary,
  PropertyUpdate,
  SearchQuery,
} from '~/types/models'
import type { ApiRequest } from './http'

export function createPropertyService(request: ApiRequest) {
  const unwrap = async <T>(response: Promise<ApiResponse<T>>): Promise<T> => (await response).data
  const endpoints = API_ENDPOINTS.properties

  return {
    search: (query: SearchQuery) => request<Page<PropertySummary>>(endpoints.search, { query }),
    featured: () => unwrap(request<ApiResponse<PropertySummary[]>>(endpoints.featured)),
    bySlug: (slug: string) => unwrap(request<ApiResponse<PropertyDetail>>(endpoints.bySlug(slug))),
    similar: (slug: string) => unwrap(request<ApiResponse<PropertySummary[]>>(endpoints.similar(slug))),

    create: (payload: PropertyCreate) =>
      unwrap(request<ApiResponse<PropertyDetail>>(endpoints.create, { method: 'POST', body: payload })),
    update: (id: number, payload: PropertyUpdate) =>
      unwrap(request<ApiResponse<PropertyDetail>>(endpoints.update(id), { method: 'PATCH', body: payload })),
    publish: (id: number) => unwrap(request<ApiResponse<PropertyDetail>>(endpoints.publish(id), { method: 'POST' })),
    changeStatus: (id: number, status: PropertyStatus) =>
      unwrap(request<ApiResponse<PropertyDetail>>(endpoints.status(id), { method: 'PATCH', body: { status } })),
    async remove(id: number): Promise<void> {
      await request<unknown>(endpoints.remove(id), { method: 'DELETE' })
    },

    myListings: (query: AgentListingQuery) => request<Page<PropertySummary>>(API_ENDPOINTS.agent.listings, { query }),
    myListing: (id: number) => unwrap(request<ApiResponse<PropertyDetail>>(API_ENDPOINTS.agent.listing(id))),
  }
}

export type PropertyService = ReturnType<typeof createPropertyService>
