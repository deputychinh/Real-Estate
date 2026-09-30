<script setup lang="ts">
import { ROUTES } from '~/constants/routes'

const links = [
  { to: ROUTES.dashboard, label: 'My listings', icon: 'building' as const },
  { to: ROUTES.newListing, label: 'New listing', icon: 'home' as const },
  { to: ROUTES.inquiries, label: 'Inquiries', icon: 'mail' as const },
]
</script>

<template>
  <div class="dashboard">
    <AppHeader />
    <div class="container dashboard__body">
      <nav class="dashboard__nav" aria-label="Dashboard">
        <NuxtLink v-for="link in links" :key="link.to" :to="link.to" class="dashboard__link">
          <BaseIcon :name="link.icon" /> {{ link.label }}
        </NuxtLink>
      </nav>
      <main id="main" class="dashboard__main">
        <slot />
      </main>
    </div>
  </div>
</template>

<style scoped lang="scss">
.dashboard {
  min-height: 100vh;
  background: $color-bg-soft;

  &__body {
    display: grid;
    gap: $space-5;
    padding-top: $space-6;
    padding-bottom: $space-7;

    @include up('lg') {
      grid-template-columns: 220px 1fr;
      align-items: start;
    }
  }

  &__nav {
    display: flex;
    gap: $space-2;
    overflow-x: auto;

    @include up('lg') {
      flex-direction: column;
      position: sticky;
      top: 90px;
    }
  }

  &__link {
    display: flex;
    align-items: center;
    gap: $space-2;
    padding: $space-3 $space-4;
    border-radius: $radius-md;
    font-weight: 600;
    white-space: nowrap;
    color: $color-text-strong;

    &:hover {
      color: $color-primary;
    }

    &.router-link-exact-active {
      background: $color-bg;
      color: $color-primary;
      box-shadow: $shadow-card;
    }
  }

  &__main {
    min-width: 0;
  }
}
</style>
