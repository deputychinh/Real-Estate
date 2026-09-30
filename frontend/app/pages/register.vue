<script setup lang="ts">
import { PASSWORD_MIN_LENGTH } from '~/constants/app'
import { ROUTES } from '~/constants/routes'
import { SignupRole } from '~/enums'
import { useAuthStore } from '~/stores/auth.store'
import { toApiError } from '~/utils/api-error'

useSeoMeta({ title: 'Create an account', robots: 'noindex' })

const auth = useAuthStore()
const form = reactive({ full_name: '', email: '', password: '', phone: '', role: SignupRole.INVESTOR })
const errors = ref<Record<string, string>>({})
const formError = ref<string | null>(null)
const loading = ref(false)

const roles: { value: SignupRole; title: string; text: string }[] = [
  { value: SignupRole.INVESTOR, title: 'Investor', text: 'Save listings and contact agents' },
  { value: SignupRole.AGENT, title: 'Agent', text: 'Publish listings and answer inquiries' },
]

function validate(): boolean {
  const found: Record<string, string> = {}
  if (form.full_name.trim().length < 2) found.full_name = 'Enter your name.'
  if (!/^\S+@\S+\.\S+$/.test(form.email)) found.email = 'Enter a valid email.'
  if (form.password.length < PASSWORD_MIN_LENGTH || !/\d/.test(form.password) || !/[a-z]/i.test(form.password)) {
    found.password = `At least ${PASSWORD_MIN_LENGTH} characters with a letter and a digit.`
  }
  errors.value = found
  return Object.keys(found).length === 0
}

async function submit(): Promise<void> {
  formError.value = null
  if (!validate()) return
  loading.value = true
  try {
    await auth.register({
      full_name: form.full_name.trim(),
      email: form.email.trim(),
      password: form.password,
      phone: form.phone.trim() || null,
      role: form.role,
    })
    await navigateTo(auth.isAgent ? ROUTES.dashboard : ROUTES.properties)
  } catch (error) {
    const apiError = toApiError(error)
    errors.value = apiError.fieldErrors()
    formError.value = apiError.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="container section auth">
    <div class="auth__card">
      <h1>Create an account</h1>
      <form class="auth__form" novalidate @submit.prevent="submit">
        <fieldset class="auth__roles">
          <legend>I am an</legend>
          <label v-for="role in roles" :key="role.value" class="auth__role" :class="{ 'auth__role--active': form.role === role.value }">
            <input v-model="form.role" type="radio" name="role" :value="role.value">
            <strong>{{ role.title }}</strong>
            <span>{{ role.text }}</span>
          </label>
        </fieldset>
        <BaseInput v-model="form.full_name" label="Full name" autocomplete="name" required :error="errors.full_name" />
        <BaseInput v-model="form.email" label="Email" type="email" autocomplete="email" required :error="errors.email" />
        <BaseInput
          v-model="form.password"
          label="Password"
          type="password"
          autocomplete="new-password"
          required
          :hint="`At least ${PASSWORD_MIN_LENGTH} characters, with a letter and a digit.`"
          :error="errors.password"
        />
        <BaseInput v-model="form.phone" label="Phone (optional)" type="tel" autocomplete="tel" :error="errors.phone" />
        <BaseAlert v-if="formError">{{ formError }}</BaseAlert>
        <BaseButton type="submit" block :loading="loading">Create account</BaseButton>
      </form>
      <p class="auth__switch">Already registered? <NuxtLink :to="ROUTES.login">Sign in</NuxtLink></p>
    </div>
  </section>
</template>

<style scoped lang="scss">
.auth {
  display: flex;
  justify-content: center;

  &__card {
    width: 100%;
    max-width: 480px;
    padding: $space-6;
    @include card;
  }

  &__form {
    display: grid;
    gap: $space-4;
  }

  &__roles {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: $space-3;
    margin: 0;
    padding: 0;
    border: 0;

    legend {
      margin-bottom: $space-2;
      font-size: $font-size-sm;
      font-weight: 600;
      color: $color-text-strong;
    }
  }

  &__role {
    display: grid;
    gap: 2px;
    padding: $space-3;
    border: 2px solid $color-border;
    border-radius: $radius-md;
    font-size: $font-size-sm;
    cursor: pointer;

    input {
      position: absolute;
      opacity: 0;
    }

    strong {
      color: $color-text-strong;
    }

    &--active {
      border-color: $color-primary;
      background: $color-primary-soft;
    }

    &:focus-within {
      @include focus-ring;
    }
  }

  &__switch {
    text-align: center;

    a {
      font-weight: 600;
      color: $color-primary;
    }
  }
}
</style>
