<script setup lang="ts">
import type { NuxtError } from '#app'
import { ROUTES } from '~/constants/routes'

const props = defineProps<{ error: NuxtError }>()

const copy = computed(() => {
  switch (props.error.statusCode) {
    case 404:
      return { title: 'Page not found', text: 'This listing may have been sold, rented or removed.' }
    case 403:
      return { title: 'Not allowed', text: props.error.statusMessage || 'You do not have access to this page.' }
    default:
      return { title: 'Something went wrong', text: 'Please try again in a moment.' }
  }
})

useSeoMeta({ title: () => copy.value.title, robots: 'noindex' })
</script>

<template>
  <!-- Always the public layout: a 403 on /dashboard must not show the dashboard menu. -->
  <NuxtLayout name="default">
    <section class="container section error">
      <p class="error__code">{{ props.error.statusCode }}</p>
      <h1>{{ copy.title }}</h1>
      <p class="error__text">{{ copy.text }}</p>
      <div class="error__actions">
        <BaseButton @click="clearError({ redirect: ROUTES.properties })">Browse properties</BaseButton>
        <BaseButton variant="outline" @click="clearError({ redirect: ROUTES.home })">Go home</BaseButton>
      </div>
    </section>
  </NuxtLayout>
</template>

<style scoped lang="scss">
.error {
  text-align: center;

  &__code {
    margin: 0;
    font-size: 5rem;
    font-weight: 700;
    color: $color-primary;
  }

  &__text {
    color: $color-text-muted;
  }

  &__actions {
    display: flex;
    justify-content: center;
    gap: $space-3;
    margin-top: $space-5;
  }
}
</style>
