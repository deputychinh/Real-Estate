import { mockNuxtImport } from '@nuxt/test-utils/runtime'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useFavoritesStore } from '~/stores/favorites.store'
import { ApiError } from '~/utils/api-error'
import { ErrorCode } from '~/enums'

const favorites = vi.hoisted(() => ({ add: vi.fn(), remove: vi.fn(), ids: vi.fn() }))

mockNuxtImport('useServices', () => () => ({ favorites }))

describe('favorites store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.resetAllMocks()
  })

  it('updates the heart before the server answers', async () => {
    let resolve!: () => void
    favorites.add.mockReturnValue(new Promise<void>((done) => (resolve = done)))
    const store = useFavoritesStore()

    const pending = store.toggle(5)
    expect(store.has(5)).toBe(true)
    expect(store.isPending(5)).toBe(true)
    resolve()
    await pending
    expect(favorites.add).toHaveBeenCalledWith(5)
    expect(store.isPending(5)).toBe(false)
  })

  it('reverts when the request fails', async () => {
    favorites.ids.mockResolvedValue([5])
    favorites.remove.mockRejectedValue(new ApiError(500, ErrorCode.INTERNAL_ERROR, 'boom'))
    const store = useFavoritesStore()
    await store.load()

    await expect(store.toggle(5)).rejects.toThrow('boom')
    expect(store.has(5)).toBe(true)
  })
})
