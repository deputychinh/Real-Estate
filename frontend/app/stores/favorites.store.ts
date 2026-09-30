import { defineStore } from 'pinia'

/** Favourite ids for the hearts on cards. Toggle is optimistic: the UI changes first, and reverts on error. */
export const useFavoritesStore = defineStore('favorites', () => {
  const ids = ref<number[]>([])
  const pending = ref<number[]>([])

  const has = (propertyId: number): boolean => ids.value.includes(propertyId)
  const isPending = (propertyId: number): boolean => pending.value.includes(propertyId)

  async function load(): Promise<void> {
    ids.value = await useServices().favorites.ids()
  }

  function set(propertyId: number, favorite: boolean): void {
    ids.value = favorite ? [...new Set([...ids.value, propertyId])] : ids.value.filter((id) => id !== propertyId)
  }

  async function toggle(propertyId: number): Promise<void> {
    if (isPending(propertyId)) return
    const wasFavorite = has(propertyId)
    set(propertyId, !wasFavorite)
    pending.value = [...pending.value, propertyId]
    try {
      const { favorites } = useServices()
      await (wasFavorite ? favorites.remove(propertyId) : favorites.add(propertyId))
    } catch (error) {
      set(propertyId, wasFavorite)
      throw error
    } finally {
      pending.value = pending.value.filter((id) => id !== propertyId)
    }
  }

  function reset(): void {
    ids.value = []
  }

  return { ids, has, isPending, load, toggle, reset }
})
