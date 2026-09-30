<script setup lang="ts">
import { FEATURED_ON_HOME, LATEST_ON_HOME } from '~/constants/app'
import { ROUTES } from '~/constants/routes'
import { Currency } from '~/enums'

useSeoMeta({
  title: 'International property search',
  description: 'Buy or rent homes, villas and offices in six markets, with prices shown in your currency.',
  ogTitle: 'Estatia · International property search',
})

const services = useServices()
const [{ data: featured }, { data: latest }, { data: countries }] = await Promise.all([
  useAsyncData('home:featured', () => services.properties.featured(), { default: () => [] }),
  useAsyncData('home:latest', () => services.properties.search({ size: LATEST_ON_HOME })),
  useCountries(),
])

const stats = computed(() => [
  { value: latest.value?.meta.total ?? 0, label: 'Listings' },
  { value: countries.value.length, label: 'Countries' },
  { value: Object.values(Currency).length, label: 'Currencies' },
])
</script>

<template>
  <div>
    <section class="hero">
      <div class="container hero__inner">
        <p class="hero__eyebrow">International real estate</p>
        <h1 class="hero__title">Find your next investment, anywhere.</h1>
        <p class="hero__text">Homes, villas and offices in Vietnam, Singapore, Dubai, London, New York and Lisbon.</p>
        <HeroSearch />
      </div>
    </section>

    <section class="container stats" aria-label="Portal in numbers">
      <div v-for="stat in stats" :key="stat.label" class="stats__item">
        <span class="stats__value">{{ stat.value }}</span>
        <span class="stats__label">{{ stat.label }}</span>
      </div>
    </section>

    <section v-if="featured.length" class="container section">
      <h2 class="section-title">Featured properties</h2>
      <p class="section-subtitle">Hand-picked listings from our agents.</p>
      <PropertyGrid :items="featured.slice(0, FEATURED_ON_HOME)" />
    </section>

    <section class="section markets">
      <div class="container">
        <h2 class="section-title">Explore by market</h2>
        <p class="section-subtitle">Every price is also shown in the currency you choose.</p>
        <ul class="markets__list">
          <li v-for="country in countries" :key="country.code">
            <NuxtLink :to="{ path: ROUTES.properties, query: { country: country.code } }" class="markets__item">
              <span class="markets__code">{{ country.code }}</span>
              <span>{{ country.name }}</span>
            </NuxtLink>
          </li>
        </ul>
      </div>
    </section>

    <section v-if="latest?.data.length" class="container section">
      <div class="latest__head">
        <div>
          <h2 class="section-title">Latest listings</h2>
          <p class="section-subtitle">New on the market this week.</p>
        </div>
        <BaseButton variant="outline" :to="ROUTES.properties">View all</BaseButton>
      </div>
      <PropertyGrid :items="latest.data" />
    </section>
  </div>
</template>

<style scoped lang="scss">
.hero {
  position: relative;
  padding: $space-8 0;
  background:
    linear-gradient(120deg, rgba(28, 45, 58, 0.85), rgba(28, 45, 58, 0.35)),
    url('https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=1920&q=80&auto=format&fit=crop') center / cover;
  color: $color-bg;

  @include up('md') {
    padding: 120px 0;
  }

  &__eyebrow {
    margin: 0 0 $space-2;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: $color-accent;
  }

  &__title {
    max-width: 720px;
    font-size: $font-size-2xl;
    color: $color-bg;

    @include up('md') {
      font-size: $font-size-3xl;
    }
  }

  &__text {
    max-width: 560px;
    margin: 0 0 $space-6;
    font-size: $font-size-lg;
    opacity: 0.9;
  }
}

.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: $space-3;
  margin-top: -$space-6;
  position: relative;

  &__item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: $space-4;
    @include card;
  }

  &__value {
    font-size: $font-size-2xl;
    font-weight: 700;
    color: $color-primary;
  }

  &__label {
    font-size: $font-size-sm;
    color: $color-text-muted;
  }
}

.markets {
  background: $color-bg-soft;

  &__list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: $space-3;
    margin: 0;
    padding: 0;
    list-style: none;
  }

  &__item {
    display: flex;
    align-items: center;
    gap: $space-3;
    padding: $space-4;
    font-weight: 600;
    color: $color-text-strong;
    @include card;
    transition: transform $transition;

    &:hover {
      transform: translateY(-2px);
      color: $color-primary;
    }
  }

  &__code {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: $radius-md;
    background: $color-primary-soft;
    color: $color-primary;
  }
}

.latest__head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: $space-3;
  margin-bottom: $space-2;
}
</style>
