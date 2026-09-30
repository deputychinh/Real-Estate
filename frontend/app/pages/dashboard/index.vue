<script setup lang="ts">
import { DASHBOARD_PAGE_SIZE } from '~/constants/app'
import { ROUTES } from '~/constants/routes'
import { PROPERTY_STATUS_LABEL, PropertyStatus } from '~/enums'
import type { PropertySummary } from '~/types/models'
import { toApiError } from '~/utils/api-error'

definePageMeta({ layout: 'dashboard', middleware: 'agent' })
useSeoMeta({ title: 'My listings', robots: 'noindex' })

const services = useServices()
const notify = useNotify()
const statusFilter = ref<PropertyStatus | undefined>()
const page = ref(1)
const busyId = ref<number | null>(null)

const { data, status, error, refresh } = await useAsyncData(
  () => `dashboard:listings:${statusFilter.value ?? 'all'}:${page.value}`,
  () => services.properties.myListings({ status: statusFilter.value, page: page.value, size: DASHBOARD_PAGE_SIZE }),
  { watch: [statusFilter, page] },
)

watch(statusFilter, () => (page.value = 1))

const tabs = [
  { value: undefined, label: 'All' },
  ...Object.values(PropertyStatus).map((value) => ({ value, label: PROPERTY_STATUS_LABEL[value] })),
]

async function changeStatus(id: number, next: PropertyStatus): Promise<void> {
  busyId.value = id
  try {
    await (next === PropertyStatus.PUBLISHED ? services.properties.publish(id) : services.properties.changeStatus(id, next))
    notify.success(`Listing moved to ${PROPERTY_STATUS_LABEL[next].toLowerCase()}.`)
    await refresh()
  } catch (failure) {
    const apiError = toApiError(failure)
    const missing = (apiError.details as { missing?: string[] } | null)?.missing
    notify.error(missing?.length ? `${apiError.message}: ${missing.join(', ')}.` : apiError.message)
  } finally {
    busyId.value = null
  }
}

async function remove(item: PropertySummary): Promise<void> {
  if (!window.confirm(`Delete "${item.title}"? It will disappear from search.`)) return
  busyId.value = item.id
  try {
    await services.properties.remove(item.id)
    notify.success('Listing deleted.')
    await refresh()
  } catch (failure) {
    notify.error(toApiError(failure).message)
  } finally {
    busyId.value = null
  }
}
</script>

<template>
  <div class="listings">
    <header class="listings__head">
      <div>
        <h1 class="listings__title">My listings</h1>
        <p class="listings__count">{{ data?.meta.total ?? 0 }} listings</p>
      </div>
      <BaseButton :to="ROUTES.newListing">+ New listing</BaseButton>
    </header>

    <div class="listings__tabs" role="tablist" aria-label="Filter by status">
      <button
        v-for="tab in tabs"
        :key="tab.label"
        type="button"
        role="tab"
        :aria-selected="statusFilter === tab.value"
        class="listings__tab"
        @click="statusFilter = tab.value"
      >
        {{ tab.label }}
      </button>
    </div>

    <BaseAlert v-if="error">Could not load your listings. <button type="button" @click="() => refresh()">Try again</button></BaseAlert>
    <BaseSkeleton v-else-if="status === 'pending' && !data" height="320px" />
    <BaseEmptyState v-else-if="!data?.data.length" icon="building" title="No listings here" message="Create a draft, add photos, then publish it.">
      <BaseButton :to="ROUTES.newListing">Create a listing</BaseButton>
    </BaseEmptyState>
    <template v-else>
      <ListingTable :items="data.data" :busy-id="busyId" @status="changeStatus" @remove="remove" />
      <BasePagination :page="data.meta.page" :pages="data.meta.pages" @update:page="(value) => (page = value)" />
    </template>
  </div>
</template>

<style scoped lang="scss">
.listings {
  display: grid;
  gap: $space-5;

  &__head {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: $space-3;
  }

  &__title {
    margin: 0;
  }

  &__count {
    margin: 0;
    color: $color-text-muted;
  }

  &__tabs {
    display: flex;
    flex-wrap: wrap;
    gap: $space-2;
  }

  &__tab {
    padding: $space-2 $space-4;
    border: 1px solid $color-border;
    border-radius: $radius-pill;
    background: $color-bg;
    font: inherit;
    font-size: $font-size-sm;
    font-weight: 600;
    cursor: pointer;

    &[aria-selected='true'] {
      background: $color-secondary;
      border-color: $color-secondary;
      color: $color-bg;
    }
  }
}
</style>
