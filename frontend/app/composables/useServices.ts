import type { Services } from '~/services'

export function useServices(): Services {
  return useNuxtApp().$services as Services
}
