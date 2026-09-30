import { API_ENDPOINTS } from '~/constants/api'
import type { AccessTokenResponse, ApiResponse, LoginRequest, RegisterRequest, UserRead } from '~/types/models'
import type { ApiRequest } from './http'

export function createAuthService(request: ApiRequest) {
  return {
    async register(payload: RegisterRequest): Promise<UserRead> {
      const { data } = await request<ApiResponse<UserRead>>(API_ENDPOINTS.auth.register, { method: 'POST', body: payload })
      return data
    },
    async login(payload: LoginRequest): Promise<AccessTokenResponse> {
      const { data } = await request<ApiResponse<AccessTokenResponse>>(API_ENDPOINTS.auth.login, {
        method: 'POST',
        body: payload,
      })
      return data
    },
    async refresh(): Promise<AccessTokenResponse> {
      const { data } = await request<ApiResponse<AccessTokenResponse>>(API_ENDPOINTS.auth.refresh, { method: 'POST' })
      return data
    },
    async logout(): Promise<void> {
      await request<unknown>(API_ENDPOINTS.auth.logout, { method: 'POST' })
    },
  }
}

export type AuthService = ReturnType<typeof createAuthService>
