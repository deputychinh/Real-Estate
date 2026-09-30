<script setup lang="ts">
import { PAGE_SIZE } from '~/constants/app'
import { PROPERTY_SORT_LABEL, PropertySort, ViewMode } from '~/enums'
import { usePreferencesStore } from '~/stores/preferences.store'
import { activeFilterCount } from '~/utils/search-query'

const services = useServices()
const preferences = usePreferencesStore()
const { query, apply, reset } = useSearch()

const { data: page, status, error, refresh } = await useAsyncData(
  () => `search:${JSON.stringify(query.value)}`,
  () => services.properties.search({ ...query.value, size: PAGE_SIZE }),
  { watch: [query] },
)

const filtersOpen = ref(false)
const loading = computed(() => status.value === 'pending')
const total = computed(() => page.value?.meta.total ?? 0)
const filterCount = computed(() => activeFilterCount(query.value))
const sortOptions = Object.values(PropertySort).map((value) => ({ value, label: PROPERTY_SORT_LABEL[value] }))
const sort = computed({
  get: () => query.value.sort ?? PropertySort.NEWEST,
  set: (value) => apply({ sort: value as PropertySort }),
})

useSeoMeta({
  title: () => (query.value.purpose === 'RENT' ? 'Properties for rent' : 'Properties for sale and rent'),
  description: 'Search international listings by country, city, price, type and size.',
})

async function onApply(filters: Parameters<typeof apply>[0]): Promise<void> {
  filtersOpen.value = false
  await apply(filters)
}
</script>

<template>
  <div class="container section search">
    <header class="search__head">
      <div>
        <h1 class="search__title">Properties</h1>
        <p class="search__count" aria-live="polite">
          <template v-if="!loading">{{ total }} {{ total === 1 ? 'listing' : 'listings' }} found</template>
          <template v-else>Searching…</template>
        </p>
      </div>
      <div class="search__tools">
        <BaseButton class="search__filters-toggle" variant="outline" size="sm" @click="filtersOpen = !filtersOpen">
          Filters<span v-if="filterCount"> ({{ filterCount }})</span>
        </BaseButton>
        <BaseSelect v-model="sort" label="Sort by" hide-label :options="sortOptions" />
        <div class="search__view" role="group" aria-label="Layout">
          <button
            v-for="mode in [ViewMode.GRID, ViewMode.LIST]"
            :key="mode"
            type="button"
            :aria-pressed="preferences.viewMode === mode"
            :aria-label="mode === ViewMode.GRID ? 'Grid view' : 'List view'"
            @click="preferences.viewMode = mode"
          >
            <BaseIcon :name="mode === ViewMode.GRID ? 'grid' : 'list'" />
          </button>
        </div>
      </div>
    </header>

    <div class="search__layout">
      <aside class="search__sidebar" :class="{ 'search__sidebar--open': filtersOpen }">
        <PropertyFilters :query="query" @apply="onApply" @reset="reset" />
      </aside>

      <section class="search__results" aria-label="Results">
        <BaseAlert v-if="error">
          Could not load listings. <button type="button" class="search__retry" @click="() => refresh()">Try again</button>
        </BaseAlert>
        <BaseEmptyState
          v-else-if="!loading && !page?.data.length"
          title="No listings match these filters"
          message="Try a wider price range or another city."
        >
          <BaseButton variant="outline" @click="reset">Clear filters</BaseButton>
        </BaseEmptyState>
        <template v-else>
          <PropertyGrid :items="page?.data ?? []" :loading="loading" :layout="preferences.viewMode" />
          <BasePagination
            v-if="page"
            :page="page.meta.page"
            :pages="page.meta.pages"
            @update:page="(value) => apply({ page: value })"
          />
        </template>
      </section>
    </div>
  </div>
</template>

<style scoped lang="scss">
.search {
  &__head {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-end;
    justify-content: space-between;
    gap: $space-4;
    margin-bottom: $space-5;
  }

  &__title {
    margin: 0;
    font-size: $font-size-2xl;
  }

  &__count {
    margin: 0;
    color: $color-text-muted;
  }

  &__tools {
    display: flex;
    align-items: center;
    gap: $space-2;
  }

  &__filters-toggle {
    @include up('lg') {
      display: none;
    }
  }

  &__view {
    display: flex;
    border: 1px solid $color-border;
    border-radius: $radius-md;
    overflow: hidden;

    button {
      display: inline-flex;
      padding: 10px;
      border: 0;
      background: $color-bg;
      color: $color-text-muted;
      cursor: pointer;

      &[aria-pressed='true'] {
        background: $color-primary;
        color: $color-bg;
      }
    }
  }

  &__layout {
    display: grid;
    gap: $space-5;

    @include up('lg') {
      grid-template-columns: 300px 1fr;
      align-items: start;
    }
  }

  &__sidebar {
    display: none;

    &--open {
      display: block;
    }

    @include up('lg') {
      display: block;
      position: sticky;
      top: 90px;
    }
  }

  &__results {
    min-width: 0;
  }

  &__retry {
    border: 0;
    background: none;
    font: inherit;
    font-weight: 700;
    color: inherit;
    text-decoration: underline;
    cursor: pointer;
  }
}
</style>
