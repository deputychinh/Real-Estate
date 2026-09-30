<script setup lang="ts">
import { ROUTES } from '~/constants/routes'
import { LISTING_PURPOSE_LABEL, PropertyStatus, PROPERTY_TYPE_LABEL } from '~/enums'

const route = useRoute()
const services = useServices()
const slug = computed(() => String(route.params.slug))

const { data: listing, error } = await useAsyncData(
  () => `property:${slug.value}`,
  () => services.properties.bySlug(slug.value),
)
if (error.value || !listing.value) {
  throw createError({
    statusCode: error.value?.statusCode === 404 ? 404 : (error.value?.statusCode ?? 404),
    statusMessage: 'Listing not found',
    fatal: true,
  })
}

// Below the fold and not needed for the first paint: load without blocking navigation.
const { data: similar } = useLazyAsyncData(`similar:${slug.value}`, () => services.properties.similar(slug.value), {
  default: () => [],
})

useListingSeo(listing)
</script>

<template>
  <article v-if="listing" class="container section detail">
    <nav class="detail__crumbs" aria-label="Breadcrumb">
      <NuxtLink :to="ROUTES.properties">Properties</NuxtLink>
      <span aria-hidden="true">/</span>
      <NuxtLink :to="{ path: ROUTES.properties, query: { city: listing.city.slug } }">{{ listing.city.name }}</NuxtLink>
      <span aria-hidden="true">/</span>
      <span aria-current="page">{{ PROPERTY_TYPE_LABEL[listing.property_type] }}</span>
    </nav>

    <header class="detail__head">
      <div>
        <div class="detail__badges">
          <BaseBadge tone="primary" solid>{{ LISTING_PURPOSE_LABEL[listing.purpose] }}</BaseBadge>
          <PropertyStatusBadge v-if="listing.status !== PropertyStatus.PUBLISHED" :status="listing.status" />
        </div>
        <h1 class="detail__title">{{ listing.title }}</h1>
        <p class="detail__address"><BaseIcon name="pin" /> {{ listing.address }}, {{ listing.city.name }}, {{ listing.city.country_name }}</p>
      </div>
      <div class="detail__price">
        <PropertyPrice :price="listing.price" :currency="listing.currency" :purpose="listing.purpose" size="lg" />
        <FavoriteButton :property-id="listing.id" :title="listing.title" :floating="false" />
      </div>
    </header>

    <div class="detail__layout">
      <div class="detail__main">
        <PropertyGallery :images="listing.images" :title="listing.title" />
        <PropertyFacts :property="listing" />
        <section>
          <h2 class="detail__section-title">Description</h2>
          <p class="detail__description">{{ listing.description }}</p>
        </section>
        <section v-if="listing.amenities.length">
          <h2 class="detail__section-title">Amenities</h2>
          <ul class="detail__amenities">
            <li v-for="amenity in listing.amenities" :key="amenity.id"><BaseIcon name="check" /> {{ amenity.name }}</li>
          </ul>
        </section>
      </div>
      <aside class="detail__aside">
        <div class="detail__panel">
          <AgentCard :agent="listing.agent" />
          <hr>
          <InquiryForm :property-id="listing.id" :title="listing.title" />
        </div>
      </aside>
    </div>

    <section v-if="similar.length" class="detail__similar">
      <h2 class="section-title">Similar properties</h2>
      <PropertyGrid :items="similar" />
    </section>
  </article>
</template>

<style scoped lang="scss">
.detail {
  &__crumbs {
    display: flex;
    flex-wrap: wrap;
    gap: $space-2;
    margin-bottom: $space-4;
    font-size: $font-size-sm;
    color: $color-text-muted;

    a:hover {
      color: $color-primary;
    }
  }

  &__head {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-end;
    justify-content: space-between;
    gap: $space-4;
    margin-bottom: $space-5;
  }

  &__badges {
    display: flex;
    gap: $space-2;
    margin-bottom: $space-2;
  }

  &__title {
    font-size: $font-size-xl;

    @include up('md') {
      font-size: $font-size-2xl;
    }
  }

  &__address {
    display: flex;
    align-items: center;
    gap: $space-1;
    margin: 0;
    color: $color-text-muted;
  }

  &__price {
    display: flex;
    align-items: center;
    gap: $space-3;
  }

  &__layout {
    display: grid;
    gap: $space-6;

    @include up('lg') {
      grid-template-columns: 1fr 360px;
      align-items: start;
    }
  }

  &__main {
    display: grid;
    gap: $space-6;
    min-width: 0;
  }

  &__section-title {
    font-size: $font-size-lg;
  }

  &__description {
    margin: 0;
    white-space: pre-line;
  }

  &__amenities {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: $space-2;
    margin: 0;
    padding: 0;
    list-style: none;

    li {
      display: flex;
      align-items: center;
      gap: $space-2;
      color: $color-text-strong;

      svg {
        color: $color-success;
      }
    }
  }

  &__aside {
    @include up('lg') {
      position: sticky;
      top: 90px;
    }
  }

  &__panel {
    display: grid;
    gap: $space-4;
    padding: $space-5;
    @include card;

    hr {
      width: 100%;
      border: 0;
      border-top: 1px solid $color-border;
    }
  }

  &__similar {
    margin-top: $space-8;
  }
}
</style>
