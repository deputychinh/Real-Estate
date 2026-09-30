import { describe, expect, it } from 'vitest'
import { ClientErrorCode, ErrorCode } from '~/enums'
import { ApiError, toApiError } from '~/utils/api-error'
import { safeRedirect } from '~/utils/navigation'

describe('toApiError', () => {
  it('maps the backend error envelope', () => {
    const error = toApiError({
      statusCode: 422,
      data: {
        error: {
          code: 'VALIDATION_ERROR',
          message: 'Request validation failed',
          details: [{ field: 'price', message: 'must be positive' }],
          request_id: 'abc',
        },
      },
    })
    expect(error).toBeInstanceOf(ApiError)
    expect(error.status).toBe(422)
    expect(error.statusCode).toBe(422)
    expect(error.code).toBe(ErrorCode.VALIDATION_ERROR)
    expect(error.requestId).toBe('abc')
    expect(error.fieldErrors()).toEqual({ price: 'must be positive' })
  })

  it('treats a missing response as a network error', () => {
    const error = toApiError(new TypeError('Failed to fetch'))
    expect(error.status).toBe(0)
    expect(error.code).toBe(ClientErrorCode.NETWORK_ERROR)
  })

  it('falls back to a generic message and keeps an ApiError as is', () => {
    const generic = toApiError({ statusCode: 500 })
    expect(generic.code).toBe(ErrorCode.INTERNAL_ERROR)
    expect(generic.fieldErrors()).toEqual({})
    expect(toApiError(generic)).toBe(generic)
  })
})

describe('safeRedirect', () => {
  it.each([
    ['/properties?city=dubai', '/properties?city=dubai'],
    ['//evil.example.com', '/'],
    ['https://evil.example.com', '/'],
    ['/\\evil.example.com', '/'],
    [undefined, '/'],
  ])('%s → %s', (input, expected) => {
    expect(safeRedirect(input)).toBe(expected)
  })
})
