<script setup lang="ts">
import { ROUTES } from '~/constants/routes'
import { ListingPurpose, PROPERTY_TYPE_LABEL, PropertyType } from '~/enums'
import { toRouteQuery } from '~/utils/search-query'

const purpose = ref<ListingPurpose>(ListingPurpose.SALE)
const city = ref<string | number | undefined>()
const propertyType = ref<string | number | undefined>()

const { data: cities } = await useCities(ref(undefined))
const cityOptions = computed(() => cities.value.map((item) => ({ value: item.slug, label: `${item.name}, ${item.country_code}` })))
const typeOptions = Object.values(PropertyType).map((value) => ({ value, label: PROPERTY_TYPE_LABEL[value] }))

async function search(): Promise<void> {
  await navigateTo({
    path: ROUTES.properties,
    query: toRouteQuery({
      purpose: purpose.value,
      city: city.value ? String(city.value) : undefined,
      property_type: propertyType.value as PropertyType | undefined,
    }),
  })
}
</script>

<template>
  <form class="hero-search" role="search" @submit.prevent="search">
    <div class="hero-search__tabs" role="radiogroup" aria-label="Buy or rent">
      <button
        v-for="option in [ListingPurpose.SALE, ListingPurpose.RENT]"
        :key="option"
        type="button"
        role="radio"
        class="hero-search__tab"
        :class="{ 'hero-search__tab--active': purpose === option }"
        :aria-checked="purpose === option"
        @click="purpose = option"
      >
        {{ option === ListingPurpose.SALE ? 'Buy' : 'Rent' }}
      </button>
    </div>
    <div class="hero-search__fields">
      <BaseSelect v-model="city" label="Location" :options="cityOptions" placeholder="All locations" />
      <BaseSelect v-model="propertyType" label="Property type" :options="typeOptions" placeholder="Any type" />
      <BaseButton type="submit" size="lg"><BaseIcon name="search" /> Search</BaseButton>
    </div>
  </form>
</template>

<style scoped lang="scss">
.hero-search {
  width: 100%;
  max-width: 880px;

  &__tabs {
    display: inline-flex;
    gap: $space-1;
    padding: $space-1;
    border-radius: $radius-md $radius-md 0 0;
    background: rgba(255, 255, 255, 0.92);
  }

  &__tab {
    padding: $space-2 $space-5;
    border: 0;
    border-radius: $radius-sm;
    background: transparent;
    font: inherit;
    font-weight: 600;
    color: $color-text-strong;
    cursor: pointer;

    &--active {
      background: $color-primary;
      color: $color-bg;
    }
  }

  &__fields {
    display: grid;
    gap: $space-3;
    padding: $space-5;
    border-radius: 0 $radius-lg $radius-lg $radius-lg;
    background: $color-bg;
    box-shadow: $shadow-hover;

    @include up('md') {
      grid-template-columns: 1fr 1fr auto;
      align-items: end;
    }
  }
}
</style>
