import { ClientErrorCode, ErrorCode } from '~/enums'

export interface FieldError {
  field: string
  message: string
}

/** Every failed API call becomes an ApiError, so components handle one shape (the backend error envelope). */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: ErrorCode | ClientErrorCode,
    message: string,
    readonly details: unknown = null,
    readonly requestId: string | null = null,
  ) {
    super(message)
    this.name = 'ApiError'
  }

  /** Read by Nuxt/h3 createError, so an API 404 becomes a real 404 page. */
  get statusCode(): number {
    return this.status
  }

  /** Field errors from a 422 response, keyed by field name. */
  fieldErrors(): Record<string, string> {
    if (!Array.isArray(this.details)) return {}
    return Object.fromEntries(
      (this.details as FieldError[])
        .filter((item) => typeof item?.field === 'string')
        .map((item) => [item.field, item.message]),
    )
  }
}

interface ErrorEnvelope {
  error?: { code?: ErrorCode; message?: string; details?: unknown; request_id?: string | null }
}

interface FetchLikeError {
  statusCode?: number
  status?: number
  data?: ErrorEnvelope
  message?: string
}

export function toApiError(error: unknown): ApiError {
  if (error instanceof ApiError) return error
  const failure = (error ?? {}) as FetchLikeError
  const status = failure.statusCode ?? failure.status ?? 0
  const body = failure.data?.error
  if (!status) {
    return new ApiError(0, ClientErrorCode.NETWORK_ERROR, 'Cannot reach the server. Check your connection.')
  }
  return new ApiError(
    status,
    body?.code ?? ErrorCode.INTERNAL_ERROR,
    body?.message ?? 'Something went wrong. Please try again.',
    body?.details ?? null,
    body?.request_id ?? null,
  )
}
