<script setup lang="ts">
import { ListingPurpose, LISTING_PURPOSE_LABEL, PROPERTY_TYPE_LABEL, PropertyType } from '~/enums'
import { usePreferencesStore } from '~/stores/preferences.store'
import type { SearchQuery } from '~/types/models'

const props = defineProps<{ query: SearchQuery }>()
const emit = defineEmits<{ apply: [filters: Partial<SearchQuery>]; reset: [] }>()

const preferences = usePreferencesStore()

// Local draft: nothing is fetched until the user presses "Apply".
const draft = reactive<Partial<SearchQuery>>({})
function load(): void {
  Object.assign(draft, {
    purpose: props.query.purpose,
    property_type: props.query.property_type,
    country: props.query.country,
    city: props.query.city,
    price_min: props.query.price_min,
    price_max: props.query.price_max,
    bedrooms_min: props.query.bedrooms_min,
    q: props.query.q,
  })
}
watch(() => props.query, load, { immediate: true })

const country = computed(() => draft.country)
const { data: countries } = await useCountries()
const { data: cities } = await useCities(country)
watch(country, () => {
  if (draft.city && !cities.value.some((city) => city.slug === draft.city)) draft.city = undefined
})

const purposeOptions = Object.values(ListingPurpose).map((value) => ({ value, label: LISTING_PURPOSE_LABEL[value] }))
const typeOptions = Object.values(PropertyType).map((value) => ({ value, label: PROPERTY_TYPE_LABEL[value] }))
const countryOptions = computed(() => countries.value.map((item) => ({ value: item.code, label: item.name })))
const cityOptions = computed(() => cities.value.map((item) => ({ value: item.slug, label: item.name })))
const bedroomOptions = [1, 2, 3, 4, 5].map((value) => ({ value, label: `${value}+` }))

const priceError = computed(() =>
  draft.price_min !== undefined && draft.price_max !== undefined && Number(draft.price_min) > Number(draft.price_max)
    ? 'Minimum price is higher than maximum'
    : undefined,
)

function toNumber(value: unknown): number | undefined {
  return value === '' || value === null || value === undefined ? undefined : Number(value)
}

function submit(): void {
  if (priceError.value) return
  const priceMin = toNumber(draft.price_min)
  const priceMax = toNumber(draft.price_max)
  emit('apply', {
    ...draft,
    q: draft.q?.trim() || undefined,
    price_min: priceMin,
    price_max: priceMax,
    price_currency: priceMin !== undefined || priceMax !== undefined ? preferences.currency : undefined,
  })
}
</script>

<template>
  <form class="filters" aria-label="Search filters" @submit.prevent="submit">
    <BaseInput v-model="draft.q" label="Keyword" placeholder="e.g. villa, Marina" />
    <BaseSelect v-model="draft.purpose" label="Purpose" :options="purposeOptions" placeholder="Buy or rent" />
    <BaseSelect v-model="draft.property_type" label="Property type" :options="typeOptions" placeholder="Any type" />
    <BaseSelect v-model="draft.country" label="Country" :options="countryOptions" placeholder="Any country" />
    <BaseSelect v-model="draft.city" label="City" :options="cityOptions" placeholder="Any city" />
    <div class="filters__row">
      <BaseInput v-model="draft.price_min" type="number" :min="0" :label="`Min price (${preferences.currency})`" />
      <BaseInput v-model="draft.price_max" type="number" :min="0" :label="`Max price (${preferences.currency})`" />
    </div>
    <BaseAlert v-if="priceError">{{ priceError }}</BaseAlert>
    <BaseSelect v-model="draft.bedrooms_min" label="Bedrooms" :options="bedroomOptions" placeholder="Any" />
    <div class="filters__actions">
      <BaseButton type="submit" block>Apply filters</BaseButton>
      <BaseButton variant="ghost" block @click="emit('reset')">Clear all</BaseButton>
    </div>
  </form>
</template>

<style scoped lang="scss">
.filters {
  display: grid;
  gap: $space-4;
  padding: $space-5;
  @include card;

  &__row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: $space-3;
  }

  &__actions {
    display: grid;
    gap: $space-2;
  }
}
</style>
