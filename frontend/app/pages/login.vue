<script setup lang="ts">
import { ROUTES } from '~/constants/routes'
import { ErrorCode } from '~/enums'
import { useAuthStore } from '~/stores/auth.store'
import { useFavoritesStore } from '~/stores/favorites.store'
import { toApiError } from '~/utils/api-error'
import { safeRedirect } from '~/utils/navigation'

useSeoMeta({ title: 'Sign in', robots: 'noindex' })

const auth = useAuthStore()
const route = useRoute()
const email = ref('')
const password = ref('')
const loading = ref(false)
const formError = ref<string | null>(null)

const demoAccounts = [
  { label: 'Investor', email: 'investor@demo.com' },
  { label: 'Agent', email: 'agent@demo.com' },
]

function useDemo(address: string): void {
  email.value = address
  password.value = 'Demo@1234'
}

async function submit(): Promise<void> {
  formError.value = null
  loading.value = true
  try {
    await auth.login({ email: email.value.trim(), password: password.value })
    await useFavoritesStore().load()
    await navigateTo(safeRedirect(route.query.redirect, auth.isAgent ? ROUTES.dashboard : ROUTES.properties))
  } catch (error) {
    const apiError = toApiError(error)
    formError.value =
      apiError.code === ErrorCode.RATE_LIMITED ? 'Too many attempts. Wait a minute and try again.' : apiError.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="container section auth">
    <div class="auth__card">
      <h1>Sign in</h1>
      <p class="auth__lead">Welcome back. Save listings and message agents.</p>
      <form class="auth__form" novalidate @submit.prevent="submit">
        <BaseInput v-model="email" label="Email" type="email" autocomplete="email" required />
        <BaseInput v-model="password" label="Password" type="password" autocomplete="current-password" required />
        <BaseAlert v-if="formError">{{ formError }}</BaseAlert>
        <BaseButton type="submit" block :loading="loading" :disabled="!email || !password">Sign in</BaseButton>
      </form>
      <p class="auth__switch">New here? <NuxtLink :to="ROUTES.register">Create an account</NuxtLink></p>
      <div class="auth__demo">
        <p>Demo accounts (password <code>Demo@1234</code>):</p>
        <div class="auth__demo-buttons">
          <BaseButton v-for="account in demoAccounts" :key="account.email" size="sm" variant="outline" @click="useDemo(account.email)">
            {{ account.label }}
          </BaseButton>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped lang="scss">
.auth {
  display: flex;
  justify-content: center;

  &__card {
    width: 100%;
    max-width: 440px;
    padding: $space-6;
    @include card;
  }

  &__lead {
    margin-top: 0;
    color: $color-text-muted;
  }

  &__form {
    display: grid;
    gap: $space-4;
  }

  &__switch {
    text-align: center;

    a {
      font-weight: 600;
      color: $color-primary;
    }
  }

  &__demo {
    padding: $space-4;
    border-radius: $radius-md;
    background: $color-bg-soft;
    font-size: $font-size-sm;

    p {
      margin: 0 0 $space-2;
    }
  }

  &__demo-buttons {
    display: flex;
    gap: $space-2;
  }
}
</style>
