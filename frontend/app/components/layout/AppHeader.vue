<script setup lang="ts">
import { APP_NAME } from '~/constants/app'
import { ROUTES } from '~/constants/routes'
import { Currency } from '~/enums'
import { useAuthStore } from '~/stores/auth.store'
import { useFavoritesStore } from '~/stores/favorites.store'
import { usePreferencesStore } from '~/stores/preferences.store'

const auth = useAuthStore()
const favorites = useFavoritesStore()
const preferences = usePreferencesStore()
const notify = useNotify()
const menuOpen = ref(false)
const route = useRoute()

watch(() => route.fullPath, () => (menuOpen.value = false))

const currencyOptions = Object.values(Currency).map((code) => ({ value: code, label: code }))

async function logout(): Promise<void> {
  await auth.logout()
  favorites.reset()
  notify.info('You are signed out.')
  await navigateTo(ROUTES.home)
}
</script>

<template>
  <header class="header">
    <div class="container header__inner">
      <NuxtLink :to="ROUTES.home" class="header__logo" :aria-label="`${APP_NAME} home`">
        <span class="header__mark"><BaseIcon name="home" :size="18" /></span>{{ APP_NAME }}
      </NuxtLink>

      <button
        type="button"
        class="header__toggle"
        :aria-expanded="menuOpen"
        aria-controls="main-nav"
        aria-label="Menu"
        @click="menuOpen = !menuOpen"
      >
        <span /><span /><span />
      </button>

      <nav id="main-nav" class="header__nav" :class="{ 'header__nav--open': menuOpen }" aria-label="Main">
        <NuxtLink :to="ROUTES.properties" class="header__link">Properties</NuxtLink>
        <NuxtLink :to="{ path: ROUTES.properties, query: { purpose: 'RENT' } }" class="header__link">Rent</NuxtLink>
        <NuxtLink :to="ROUTES.about" class="header__link">About</NuxtLink>
        <ClientOnly>
          <NuxtLink v-if="auth.isAuthenticated" :to="ROUTES.favorites" class="header__link">
            Saved <span v-if="favorites.ids.length" class="header__count">{{ favorites.ids.length }}</span>
          </NuxtLink>
          <NuxtLink v-if="auth.isAgent" :to="ROUTES.dashboard" class="header__link">Dashboard</NuxtLink>
        </ClientOnly>

        <div class="header__actions">
          <label class="header__currency">
            <span class="visually-hidden">Display currency</span>
            <select v-model="preferences.currency" name="currency">
              <option v-for="option in currencyOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </label>
          <ClientOnly>
            <template v-if="auth.isAuthenticated">
              <span class="header__user" :title="auth.user?.email">{{ auth.user?.full_name }}</span>
              <BaseButton variant="outline" size="sm" @click="logout">Sign out</BaseButton>
            </template>
            <template v-else>
              <BaseButton variant="ghost" size="sm" :to="ROUTES.login">Sign in</BaseButton>
              <BaseButton size="sm" :to="ROUTES.register">Get started</BaseButton>
            </template>
          </ClientOnly>
        </div>
      </nav>
    </div>
  </header>
</template>

<style scoped lang="scss">
.header {
  position: sticky;
  top: 0;
  z-index: 20;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid $color-border;

  &__inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: 68px;
    gap: $space-4;
  }

  &__logo {
    display: inline-flex;
    align-items: center;
    gap: $space-2;
    font-size: $font-size-xl;
    font-weight: 700;
    color: $color-text-strong;
  }

  &__mark {
    display: inline-flex;
    padding: 6px;
    border-radius: $radius-md;
    background: $color-primary;
    color: $color-bg;
  }

  &__toggle {
    display: inline-flex;
    flex-direction: column;
    gap: 4px;
    padding: $space-2;
    border: 0;
    background: none;
    cursor: pointer;

    span {
      width: 22px;
      height: 2px;
      background: $color-text-strong;
    }

    @include up('lg') {
      display: none;
    }
  }

  &__nav {
    display: none;
    position: absolute;
    top: 68px;
    left: 0;
    right: 0;
    flex-direction: column;
    gap: $space-3;
    padding: $space-4;
    background: $color-bg;
    border-bottom: 1px solid $color-border;

    &--open {
      display: flex;
    }

    @include up('lg') {
      display: flex;
      position: static;
      flex-direction: row;
      align-items: center;
      padding: 0;
      border: 0;
      background: none;
    }
  }

  &__link {
    font-weight: 600;
    color: $color-text-strong;

    &:hover,
    &.router-link-exact-active {
      color: $color-primary;
    }
  }

  &__count {
    display: inline-flex;
    justify-content: center;
    min-width: 20px;
    padding: 0 6px;
    border-radius: $radius-pill;
    background: $color-primary;
    color: $color-bg;
    font-size: 0.75rem;
  }

  &__actions {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: $space-2;

    @include up('lg') {
      margin-left: $space-4;
    }
  }

  &__currency select {
    padding: 6px $space-2;
    border: 1px solid $color-border;
    border-radius: $radius-md;
    font: inherit;
    font-weight: 600;
    background: $color-bg;
    cursor: pointer;
  }

  &__user {
    max-width: 160px;
    font-size: $font-size-sm;
    font-weight: 600;
    @include ellipsis;
  }
}
</style>
