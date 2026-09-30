<script setup lang="ts">
import { INQUIRY_MIN_LENGTH } from '~/constants/app'
import { ROUTES } from '~/constants/routes'
import { ErrorCode } from '~/enums'
import { useAuthStore } from '~/stores/auth.store'
import { toApiError } from '~/utils/api-error'

const props = defineProps<{ propertyId: number; title: string }>()

const auth = useAuthStore()
const notify = useNotify()
const route = useRoute()
const services = useServices()

const message = ref(`Hello, I am interested in "${props.title}". Is it still available?`)
const phone = ref('')
const errors = ref<Record<string, string>>({})
const sending = ref(false)
const sent = ref(false)
const formError = ref<string | null>(null)

async function send(): Promise<void> {
  errors.value = {}
  formError.value = null
  if (message.value.trim().length < INQUIRY_MIN_LENGTH) {
    errors.value = { message: `Please write at least ${INQUIRY_MIN_LENGTH} characters.` }
    return
  }
  sending.value = true
  try {
    await services.inquiries.send(props.propertyId, { message: message.value.trim(), phone: phone.value.trim() || null })
    sent.value = true
    notify.success('Your message was sent to the agent.')
  } catch (error) {
    const apiError = toApiError(error)
    errors.value = apiError.fieldErrors()
    formError.value =
      apiError.code === ErrorCode.RATE_LIMITED
        ? 'You have sent many messages recently. Please try again later.'
        : apiError.message
  } finally {
    sending.value = false
  }
}
</script>

<template>
  <section class="inquiry" aria-labelledby="inquiry-title">
    <h2 id="inquiry-title" class="inquiry__title">Contact the agent</h2>
    <ClientOnly>
      <BaseAlert v-if="sent" tone="success">Thanks! The agent will reply to {{ auth.user?.email }}.</BaseAlert>
      <form v-else-if="auth.isInvestor" class="inquiry__form" novalidate @submit.prevent="send">
        <BaseInput v-model="message" label="Message" multiline :rows="5" :error="errors.message" required />
        <BaseInput v-model="phone" label="Phone (optional)" type="tel" autocomplete="tel" :error="errors.phone" />
        <BaseAlert v-if="formError">{{ formError }}</BaseAlert>
        <BaseButton type="submit" block :loading="sending">Send message</BaseButton>
      </form>
      <p v-else-if="auth.isAuthenticated" class="inquiry__note">Inquiries are sent from investor accounts.</p>
      <div v-else class="inquiry__note">
        <p>Sign in as an investor to message the agent.</p>
        <BaseButton block :to="`${ROUTES.login}?redirect=${encodeURIComponent(route.fullPath)}`">Sign in</BaseButton>
      </div>
      <template #fallback><BaseSkeleton height="220px" /></template>
    </ClientOnly>
  </section>
</template>

<style scoped lang="scss">
.inquiry {
  display: grid;
  gap: $space-4;

  &__title {
    margin: 0;
    font-size: $font-size-lg;
  }

  &__form {
    display: grid;
    gap: $space-3;
  }

  &__note {
    margin: 0;
    color: $color-text-muted;

    p {
      margin: 0 0 $space-3;
    }
  }
}
</style>
