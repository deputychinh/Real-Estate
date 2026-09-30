<script setup lang="ts">
import { LISTING_PURPOSE_TONE } from '~/constants/colors'
import { ROUTES } from '~/constants/routes'
import { LISTING_PURPOSE_LABEL, PROPERTY_TYPE_LABEL, PropertyStatus } from '~/enums'
import type { PropertySummary } from '~/types/models'
import { formatArea } from '~/utils/format'

const props = withDefaults(defineProps<{ property: PropertySummary; layout?: 'grid' | 'list' }>(), { layout: 'grid' })

const link = computed(() => ROUTES.property(props.property.slug))
const unavailable = computed(() => props.property.status !== PropertyStatus.PUBLISHED)
</script>

<template>
  <article class="card" :class="`card--${props.layout}`">
    <NuxtLink :to="link" class="card__media" tabindex="-1" aria-hidden="true">
      <img
        v-if="props.property.cover_image_url"
        :src="props.property.cover_image_url"
        :alt="''"
        loading="lazy"
        width="600"
        height="400"
      >
      <span v-else class="card__placeholder"><BaseIcon name="building" :size="36" /></span>
    </NuxtLink>
    <div class="card__badges">
      <BaseBadge :tone="LISTING_PURPOSE_TONE[props.property.purpose]" solid>
        {{ LISTING_PURPOSE_LABEL[props.property.purpose] }}
      </BaseBadge>
      <BaseBadge v-if="props.property.is_featured" tone="warning" solid>Featured</BaseBadge>
      <PropertyStatusBadge v-if="unavailable" :status="props.property.status" />
    </div>
    <FavoriteButton :property-id="props.property.id" :title="props.property.title" />

    <div class="card__body">
      <PropertyPrice :price="props.property.price" :currency="props.property.currency" :purpose="props.property.purpose" />
      <h3 class="card__title">
        <NuxtLink :to="link">{{ props.property.title }}</NuxtLink>
      </h3>
      <p class="card__location">
        <BaseIcon name="pin" :size="14" />
        {{ props.property.city.name }}, {{ props.property.city.country_name }}
      </p>
      <ul class="card__facts">
        <li><span class="visually-hidden">Type: </span>{{ PROPERTY_TYPE_LABEL[props.property.property_type] }}</li>
        <li v-if="props.property.bedrooms">
          <BaseIcon name="bed" :size="16" /> {{ props.property.bedrooms }}<span class="visually-hidden"> bedrooms</span>
        </li>
        <li><BaseIcon name="bath" :size="16" /> {{ props.property.bathrooms }}<span class="visually-hidden"> bathrooms</span></li>
        <li><BaseIcon name="area" :size="16" /> {{ formatArea(props.property.area, props.property.area_unit) }}</li>
      </ul>
    </div>
  </article>
</template>

<style scoped lang="scss">
.card {
  position: relative;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  @include card;
  transition:
    box-shadow $transition,
    transform $transition;

  &:hover {
    box-shadow: $shadow-hover;
    transform: translateY(-2px);
  }

  &__media {
    display: block;
    aspect-ratio: 3 / 2;
    background: $color-bg-soft;
    overflow: hidden;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.4s ease;
    }
  }

  &:hover &__media img {
    transform: scale(1.04);
  }

  &__placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: $color-text-muted;
  }

  &__badges {
    position: absolute;
    top: $space-3;
    left: $space-3;
    display: flex;
    flex-wrap: wrap;
    gap: $space-1;
  }

  &__body {
    display: flex;
    flex-direction: column;
    gap: $space-2;
    padding: $space-4;
  }

  &__title {
    margin: 0;
    font-size: $font-size-base;
    @include ellipsis(2);

    a:hover {
      color: $color-primary;
    }
  }

  &__location {
    display: flex;
    align-items: center;
    gap: $space-1;
    margin: 0;
    font-size: $font-size-sm;
    color: $color-text-muted;
  }

  &__facts {
    display: flex;
    flex-wrap: wrap;
    gap: $space-2 $space-4;
    margin: $space-2 0 0;
    padding: $space-3 0 0;
    list-style: none;
    border-top: 1px solid $color-border;
    font-size: $font-size-sm;

    li {
      display: inline-flex;
      align-items: center;
      gap: $space-1;
    }
  }

  &--list {
    @include up('md') {
      flex-direction: row;

      .card__media {
        flex: 0 0 300px;
        aspect-ratio: auto;
      }

      .card__body {
        flex: 1;
        justify-content: center;
      }
    }
  }
}
</style>
