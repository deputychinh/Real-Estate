<script setup lang="ts">
import { ROUTES } from '~/constants/routes'
import type { PropertyCreate } from '~/types/models'
import { toApiError } from '~/utils/api-error'

definePageMeta({ layout: 'dashboard', middleware: 'agent' })
useSeoMeta({ title: 'New listing', robots: 'noindex' })

const services = useServices()
const notify = useNotify()
const saving = ref(false)
const serverErrors = ref<Record<string, string>>({})
const formError = ref<string | null>(null)

async function create(payload: PropertyCreate): Promise<void> {
  saving.value = true
  serverErrors.value = {}
  formError.value = null
  try {
    const listing = await services.properties.create(payload)
    notify.success('Draft saved. Publish it when you are ready.')
    await navigateTo(ROUTES.editListing(listing.id))
  } catch (error) {
    const apiError = toApiError(error)
    serverErrors.value = apiError.fieldErrors()
    formError.value = apiError.message
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="page">
    <h1>New listing</h1>
    <p class="page__lead">New listings start as drafts. Nobody sees them until you publish.</p>
    <BaseAlert v-if="formError" class="page__error">{{ formError }}</BaseAlert>
    <ListingForm :saving="saving" :server-errors="serverErrors" submit-label="Save draft" @submit="create" />
  </div>
</template>

<style scoped lang="scss">
.page__lead {
  color: $color-text-muted;
}

.page__error {
  margin-bottom: $space-4;
}
</style>
