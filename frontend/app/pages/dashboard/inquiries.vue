<script setup lang="ts">
import { DASHBOARD_PAGE_SIZE } from '~/constants/app'
import { INQUIRY_STATUS_LABEL, InquiryStatus } from '~/enums'
import { toApiError } from '~/utils/api-error'

definePageMeta({ layout: 'dashboard', middleware: 'agent' })
useSeoMeta({ title: 'Inquiries', robots: 'noindex' })

const services = useServices()
const notify = useNotify()
const statusFilter = ref<InquiryStatus | undefined>(InquiryStatus.NEW)
const page = ref(1)
const busyId = ref<number | null>(null)

const { data, status, error, refresh } = await useAsyncData(
  () => `dashboard:inquiries:${statusFilter.value ?? 'all'}:${page.value}`,
  () => services.inquiries.forAgent({ status: statusFilter.value, page: page.value, size: DASHBOARD_PAGE_SIZE }),
  { watch: [statusFilter, page] },
)
watch(statusFilter, () => (page.value = 1))

const tabs = [
  ...Object.values(InquiryStatus).map((value) => ({ value, label: INQUIRY_STATUS_LABEL[value] })),
  { value: undefined, label: 'All' },
]

async function changeStatus(id: number, next: InquiryStatus): Promise<void> {
  busyId.value = id
  try {
    await services.inquiries.changeStatus(id, next)
    notify.success(`Marked as ${INQUIRY_STATUS_LABEL[next].toLowerCase()}.`)
    await refresh()
  } catch (failure) {
    notify.error(toApiError(failure).message)
  } finally {
    busyId.value = null
  }
}
</script>

<template>
  <div class="inquiries-page">
    <h1>Inquiries</h1>
    <div class="inquiries-page__tabs" role="tablist" aria-label="Filter by status">
      <button
        v-for="tab in tabs"
        :key="tab.label"
        type="button"
        role="tab"
        :aria-selected="statusFilter === tab.value"
        class="inquiries-page__tab"
        @click="statusFilter = tab.value"
      >
        {{ tab.label }}
      </button>
    </div>
    <BaseAlert v-if="error">Could not load inquiries. <button type="button" @click="() => refresh()">Try again</button></BaseAlert>
    <BaseSkeleton v-else-if="status === 'pending' && !data" height="240px" />
    <BaseEmptyState v-else-if="!data?.data.length" icon="mail" title="No inquiries here" message="Messages from investors about your listings appear here." />
    <template v-else>
      <InquiryTable :items="data.data" :busy-id="busyId" @status="changeStatus" />
      <BasePagination :page="data.meta.page" :pages="data.meta.pages" @update:page="(value) => (page = value)" />
    </template>
  </div>
</template>

<style scoped lang="scss">
.inquiries-page {
  display: grid;
  gap: $space-5;

  h1 {
    margin: 0;
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
