import type { SearchQuery } from '~/types/models'
import { parseSearchQuery, toRouteQuery } from '~/utils/search-query'
import { ROUTES } from '~/constants/routes'

/** Filters live in the URL: shareable, back-button friendly, and read the same way on the server. */
export function useSearch() {
  const route = useRoute()
  const query = computed<SearchQuery>(() => parseSearchQuery(route.query))

  async function apply(patch: Partial<SearchQuery>): Promise<void> {
    const next: SearchQuery = { ...query.value, ...patch, page: patch.page ?? 1 }
    await navigateTo({ path: ROUTES.properties, query: toRouteQuery(next) })
  }

  async function reset(): Promise<void> {
    await navigateTo({ path: ROUTES.properties, query: query.value.sort ? { sort: query.value.sort } : {} })
  }

  return { query, apply, reset }
}
