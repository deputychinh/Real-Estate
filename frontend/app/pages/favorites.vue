<script setup lang="ts">
import { PAGE_SIZE } from '~/constants/app'
import { ROUTES } from '~/constants/routes'
import { useFavoritesStore } from '~/stores/favorites.store'

definePageMeta({ middleware: 'auth' })
useSeoMeta({ title: 'Saved properties', robots: 'noindex' })

const services = useServices()
const favorites = useFavoritesStore()
const page = ref(1)

const { data, status, error, refresh } = await useAsyncData(
  () => `favorites:${page.value}`,
  () => services.favorites.list(page.value, PAGE_SIZE),
  { watch: [page] },
)

// A heart removed on this page drops the card from the list without a reload.
const items = computed(() => (data.value?.data ?? []).filter((item) => favorites.has(item.id)))
</script>

<template>
  <section class="container section">
    <h1 class="section-title">Saved properties</h1>
    <p class="section-subtitle">Your watchlist. Remove a heart to take a listing off.</p>
    <BaseAlert v-if="error">Could not load your saved listings. <button type="button" @click="() => refresh()">Try again</button></BaseAlert>
    <BaseEmptyState
      v-else-if="status !== 'pending' && !items.length"
      icon="heart"
      title="Nothing saved yet"
      message="Tap the heart on any listing to keep it here."
    >
      <BaseButton :to="ROUTES.properties">Browse properties</BaseButton>
    </BaseEmptyState>
    <template v-else>
      <PropertyGrid :items="items" :loading="status === 'pending'" />
      <BasePagination v-if="data" :page="data.meta.page" :pages="data.meta.pages" @update:page="(value) => (page = value)" />
    </template>
  </section>
</template>
