import { useAuthStore } from '~/stores/auth.store'
import { useFavoritesStore } from '~/stores/favorites.store'

/** Restore the session from the httpOnly refresh cookie, then load the user's favourite ids for the hearts. */
export default defineNuxtPlugin(async () => {
  const auth = useAuthStore()
  await auth.restore()
  if (auth.isAuthenticated) await useFavoritesStore().load()
})
