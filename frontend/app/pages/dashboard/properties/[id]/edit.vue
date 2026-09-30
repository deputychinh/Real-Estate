<script setup lang="ts">
import { ROUTES } from '~/constants/routes'
import { PropertyStatus } from '~/enums'
import type { PropertyCreate } from '~/types/models'
import { toApiError } from '~/utils/api-error'

definePageMeta({ layout: 'dashboard', middleware: 'agent' })
useSeoMeta({ title: 'Edit listing', robots: 'noindex' })

const route = useRoute()
const services = useServices()
const notify = useNotify()
const id = Number(route.params.id)

const { data: listing, error, refresh } = await useAsyncData(`dashboard:listing:${id}`, () => services.properties.myListing(id))
if (error.value) {
  throw createError({ statusCode: error.value.statusCode ?? 404, statusMessage: 'Listing not found', fatal: true })
}

const saving = ref(false)
const publishing = ref(false)
const serverErrors = ref<Record<string, string>>({})
const formError = ref<string | null>(null)

async function save(payload: PropertyCreate): Promise<void> {
  saving.value = true
  serverErrors.value = {}
  formError.value = null
  try {
    listing.value = await services.properties.update(id, payload)
    notify.success('Changes saved.')
  } catch (failure) {
    const apiError = toApiError(failure)
    serverErrors.value = apiError.fieldErrors()
    formError.value = apiError.message
  } finally {
    saving.value = false
  }
}

async function publish(): Promise<void> {
  publishing.value = true
  try {
    listing.value = await services.properties.publish(id)
    notify.success('Published. The listing is now live.')
  } catch (failure) {
    const apiError = toApiError(failure)
    const missing = (apiError.details as { missing?: string[] } | null)?.missing
    formError.value = missing?.length ? `${apiError.message}: ${missing.join(', ')}.` : apiError.message
    await refresh()
  } finally {
    publishing.value = false
  }
}
</script>

<template>
  <div v-if="listing" class="page">
    <header class="page__head">
      <div>
        <h1>Edit listing</h1>
        <PropertyStatusBadge :status="listing.status" />
      </div>
      <div class="page__actions">
        <BaseButton v-if="listing.status === PropertyStatus.PUBLISHED" variant="outline" :to="ROUTES.property(listing.slug)">
          View live
        </BaseButton>
        <BaseButton v-if="listing.status === PropertyStatus.DRAFT" :loading="publishing" @click="publish">Publish</BaseButton>
      </div>
    </header>
    <BaseAlert v-if="formError" class="page__error">{{ formError }}</BaseAlert>
    <ListingForm :key="listing.updated_at" :initial="listing" :saving="saving" :server-errors="serverErrors" submit-label="Save changes" @submit="save" />
  </div>
</template>

<style scoped lang="scss">
.page {
  &__head {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: $space-3;
    margin-bottom: $space-5;

    h1 {
      margin-bottom: $space-2;
    }
  }

  &__actions {
    display: flex;
    gap: $space-2;
  }

  &__error {
    margin-bottom: $space-4;
  }
}
</style>
