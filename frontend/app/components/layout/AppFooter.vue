<script setup lang="ts">
import { APP_NAME } from '~/constants/app'
import { ROUTES } from '~/constants/routes'
</script>

<template>
  <footer class="footer">
    <div class="container footer__inner">
      <div>
        <p class="footer__brand">{{ APP_NAME }}</p>
        <p class="footer__text">International property, one search. Listings in six markets, prices in your currency.</p>
      </div>
      <nav class="footer__links" aria-label="Footer">
        <NuxtLink :to="ROUTES.properties">All properties</NuxtLink>
        <NuxtLink :to="{ path: ROUTES.properties, query: { purpose: 'SALE' } }">For sale</NuxtLink>
        <NuxtLink :to="{ path: ROUTES.properties, query: { purpose: 'RENT' } }">For rent</NuxtLink>
        <NuxtLink :to="ROUTES.about">About</NuxtLink>
      </nav>
    </div>
    <p class="footer__legal container">Demo project · data is fictional · prices use static exchange rates</p>
  </footer>
</template>

<style scoped lang="scss">
.footer {
  margin-top: $space-8;
  padding: $space-7 0 $space-5;
  background: $color-secondary;
  color: rgba(255, 255, 255, 0.75);

  &__inner {
    display: grid;
    gap: $space-5;

    @include up('md') {
      grid-template-columns: 2fr 1fr;
    }
  }

  &__brand {
    margin: 0 0 $space-2;
    font-size: $font-size-xl;
    font-weight: 700;
    color: $color-bg;
  }

  &__text {
    margin: 0;
    max-width: 420px;
  }

  &__links {
    display: grid;
    gap: $space-2;

    a:hover {
      color: $color-bg;
    }
  }

  &__legal {
    margin-top: $space-6;
    font-size: $font-size-sm;
    opacity: 0.7;
  }
}
</style>
