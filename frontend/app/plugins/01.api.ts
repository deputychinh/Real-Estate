import { createServices } from '~/services'
import { createHttpClient } from '~/services/http'
import { useAuthStore } from '~/stores/auth.store'

/** Provides `$services`. Server-side calls go straight to the API; browser calls stay same-origin. */
export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  const auth = useAuthStore()
  const request = createHttpClient({
    baseURL: import.meta.server ? config.apiBaseServer : config.public.apiBase,
    getAccessToken: () => auth.accessToken,
    refreshSession: () => auth.refresh(),
    canRefresh: import.meta.client,
  })
  return { provide: { services: createServices(request) } }
})
