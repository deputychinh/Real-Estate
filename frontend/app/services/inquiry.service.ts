import { API_ENDPOINTS } from '~/constants/api'
import type { InquiryStatus } from '~/enums'
import type { ApiResponse, InquiryCreate, InquiryQuery, InquiryRead, Page } from '~/types/models'
import type { ApiRequest } from './http'

export function createInquiryService(request: ApiRequest) {
  return {
    async send(propertyId: number, payload: InquiryCreate): Promise<InquiryRead> {
      const url = API_ENDPOINTS.properties.inquiries(propertyId)
      return (await request<ApiResponse<InquiryRead>>(url, { method: 'POST', body: payload })).data
    },
    forAgent: (query: InquiryQuery) => request<Page<InquiryRead>>(API_ENDPOINTS.agent.inquiries, { query }),
    mine: (query: InquiryQuery) => request<Page<InquiryRead>>(API_ENDPOINTS.inquiries.mine, { query }),
    async changeStatus(id: number, status: InquiryStatus): Promise<InquiryRead> {
      const url = API_ENDPOINTS.inquiries.status(id)
      return (await request<ApiResponse<InquiryRead>>(url, { method: 'PATCH', body: { status } })).data
    },
  }
}

export type InquiryService = ReturnType<typeof createInquiryService>
