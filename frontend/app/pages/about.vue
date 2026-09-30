<script setup lang="ts">
import { ROUTES } from '~/constants/routes'

useSeoMeta({ title: 'About', description: 'How the Estatia demo portal is built.' })

const points = [
  { title: 'Search across markets', text: 'Filter by country, city, price, size and type. Prices are compared in one currency, so a villa in Dubai and a flat in London sort correctly.' },
  { title: 'Built for search engines', text: 'Listing pages are server-rendered with structured data, so they can be found and shared.' },
  { title: 'Tools for agents', text: 'Agents create drafts, publish when ready and answer inquiries from one dashboard.' },
]
</script>

<template>
  <section class="container section about">
    <h1>About Estatia</h1>
    <p class="about__lead">
      A demo international property portal: FastAPI, MySQL and Redis on the backend, Nuxt and Vue on the frontend,
      designed to run on AWS.
    </p>
    <div class="about__grid">
      <div v-for="point in points" :key="point.title" class="about__card">
        <h2>{{ point.title }}</h2>
        <p>{{ point.text }}</p>
      </div>
    </div>
    <BaseButton :to="ROUTES.properties">Start searching</BaseButton>
  </section>
</template>

<style scoped lang="scss">
.about {
  &__lead {
    max-width: 680px;
    font-size: $font-size-lg;
    color: $color-text-muted;
  }

  &__grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: $space-4;
    margin: $space-6 0;
  }

  &__card {
    padding: $space-5;
    @include card;

    h2 {
      font-size: $font-size-lg;
    }

    p {
      margin: 0;
    }
  }
}
</style>
