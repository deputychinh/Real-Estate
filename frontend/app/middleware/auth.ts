import { ROUTES } from '~/constants/routes'
import { useAuthStore } from '~/stores/auth.store'

/** Pages that need a signed-in user. They render client-side (routeRules), where the session is known. */
export default defineNuxtRouteMiddleware(async (to) => {
  if (import.meta.server) return
  const auth = useAuthStore()
  await auth.restore()
  if (!auth.isAuthenticated) {
    return navigateTo({ path: ROUTES.login, query: { redirect: to.fullPath } })
  }
})
