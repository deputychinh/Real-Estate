import { toApiError } from '~/utils/api-error'

export type HttpMethod = 'GET' | 'POST' | 'PATCH' | 'DELETE'

export interface RequestOptions {
  method?: HttpMethod
  query?: object
  body?: object
}

/** The one function every service uses. Rejects only with ApiError. */
export type ApiRequest = <T>(url: string, options?: RequestOptions) => Promise<T>

export interface HttpClientOptions {
  baseURL: string
  getAccessToken: () => string | null
  /** Called once on a 401; resolves true when a new access token is in place. */
  refreshSession: () => Promise<boolean>
  canRefresh: boolean
}

export function createHttpClient(options: HttpClientOptions): ApiRequest {
  const client = $fetch.create({
    baseURL: options.baseURL,
    credentials: 'include',
    retry: 0,
    onRequest({ options: request }) {
      const token = options.getAccessToken()
      if (!token) return
      const headers = new Headers(request.headers)
      headers.set('Authorization', `Bearer ${token}`)
      request.headers = headers
    },
  })

  let refreshing: Promise<boolean> | null = null

  const send = async <T>(url: string, request: RequestOptions): Promise<T> => {
    try {
      return (await client(url, request as Parameters<typeof client>[1])) as T
    } catch (error) {
      throw toApiError(error)
    }
  }

  return async <T>(url: string, request: RequestOptions = {}): Promise<T> => {
    try {
      return await send<T>(url, request)
    } catch (error) {
      const apiError = toApiError(error)
      const canRetry =
        apiError.status === 401 && options.canRefresh && options.getAccessToken() !== null && !url.startsWith('/auth/')
      if (!canRetry) throw apiError
      // Parallel 401s share one refresh request.
      refreshing ??= options.refreshSession().finally(() => {
        refreshing = null
      })
      if (!(await refreshing)) throw apiError
      return send<T>(url, request)
    }
  }
}
