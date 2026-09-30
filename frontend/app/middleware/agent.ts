import { ROUTES } from '~/constants/routes'
import { useAuthStore } from '~/stores/auth.store'

/** Agent dashboard: signed in (401 → login) and agent/admin role (403). */
export default defineNuxtRouteMiddleware(async (to) => {
  if (import.meta.server) return
  const auth = useAuthStore()
  await auth.restore()
  if (!auth.isAuthenticated) {
    return navigateTo({ path: ROUTES.login, query: { redirect: to.fullPath } })
  }
  if (!auth.isAgent) {
    return abortNavigation(createError({ statusCode: 403, statusMessage: 'The dashboard is for agents only.' }))
  }
})
