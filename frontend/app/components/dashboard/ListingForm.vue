<script setup lang="ts">
import { MAX_LISTING_IMAGES } from '~/constants/app'
import {
  AreaUnit,
  AREA_UNIT_LABEL,
  Currency,
  LISTING_PURPOSE_LABEL,
  ListingPurpose,
  PROPERTY_TYPE_LABEL,
  PropertyType,
} from '~/enums'
import type { PropertyCreate, PropertyDetail } from '~/types/models'

const props = withDefaults(
  defineProps<{ initial?: PropertyDetail | null; saving?: boolean; serverErrors?: Record<string, string>; submitLabel?: string }>(),
  { initial: null, saving: false, serverErrors: () => ({}), submitLabel: 'Save listing' },
)
const emit = defineEmits<{ submit: [payload: PropertyCreate] }>()

interface FormState {
  title: string
  description: string
  purpose: ListingPurpose
  property_type: PropertyType
  price: string
  currency: Currency
  area: string
  area_unit: AreaUnit
  bedrooms: number
  bathrooms: number
  year_built: string
  address: string
  country: string | undefined
  city_id: number | undefined
  amenity_ids: number[]
  images: string
}

const source = props.initial
const form = reactive<FormState>({
  title: source?.title ?? '',
  description: source?.description ?? '',
  purpose: source?.purpose ?? ListingPurpose.SALE,
  property_type: source?.property_type ?? PropertyType.APARTMENT,
  price: source?.price ?? '',
  currency: source?.currency ?? Currency.USD,
  area: source?.area ?? '',
  area_unit: source?.area_unit ?? AreaUnit.SQM,
  bedrooms: source?.bedrooms ?? 1,
  bathrooms: source?.bathrooms ?? 1,
  year_built: source?.year_built ? String(source.year_built) : '',
  address: source?.address ?? '',
  country: source?.city.country_code,
  city_id: source?.city.id,
  amenity_ids: source?.amenities.map((amenity) => amenity.id) ?? [],
  images: source?.images.map((image) => image.url).join('\n') ?? '',
})

const country = computed(() => form.country)
const { data: countries } = await useCountries()
const { data: cities } = await useCities(country)
const { data: amenities } = await useAmenities()

watch(country, () => {
  if (form.city_id && !cities.value.some((city) => city.id === form.city_id)) form.city_id = undefined
})

const options = {
  purpose: Object.values(ListingPurpose).map((value) => ({ value, label: LISTING_PURPOSE_LABEL[value] })),
  type: Object.values(PropertyType).map((value) => ({ value, label: PROPERTY_TYPE_LABEL[value] })),
  currency: Object.values(Currency).map((value) => ({ value, label: value })),
  unit: Object.values(AreaUnit).map((value) => ({ value, label: AREA_UNIT_LABEL[value] })),
}
const countryOptions = computed(() => countries.value.map((item) => ({ value: item.code, label: item.name })))
const cityOptions = computed(() => cities.value.map((item) => ({ value: item.id, label: item.name })))

const imageUrls = computed(() =>
  form.images
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean),
)

const clientErrors = ref<Record<string, string>>({})
const submitted = ref(false)
const errors = computed(() => ({ ...props.serverErrors, ...clientErrors.value }))

function validate(): boolean {
  const found: Record<string, string> = {}
  if (form.title.trim().length < 5) found.title = 'At least 5 characters.'
  if (form.description.trim().length < 20) found.description = 'At least 20 characters.'
  if (!(Number(form.price) > 0)) found.price = 'Enter a price above 0.'
  if (!(Number(form.area) > 0)) found.area = 'Enter an area above 0.'
  if (!form.city_id) found.city_id = 'Choose a city.'
  if (form.address.trim().length < 3) found.address = 'Enter the address.'
  if (imageUrls.value.length > MAX_LISTING_IMAGES) found.images = `At most ${MAX_LISTING_IMAGES} images.`
  if (imageUrls.value.some((url) => !/^https?:\/\/\S+$/.test(url))) found.images = 'Each line must be an http(s) URL.'
  clientErrors.value = found
  return Object.keys(found).length === 0
}

// After the first submit, errors update as the user types (and disappear once fixed).
watch(form, () => {
  if (submitted.value) validate()
})

function submit(): void {
  submitted.value = true
  if (!validate() || !form.city_id) return
  emit('submit', {
    title: form.title.trim(),
    description: form.description.trim(),
    purpose: form.purpose,
    property_type: form.property_type,
    price: String(form.price),
    currency: form.currency,
    area: String(form.area),
    area_unit: form.area_unit,
    bedrooms: Number(form.bedrooms),
    bathrooms: Number(form.bathrooms),
    year_built: form.year_built ? Number(form.year_built) : null,
    address: form.address.trim(),
    city_id: form.city_id,
    amenity_ids: form.amenity_ids,
    images: imageUrls.value.map((url, index) => ({ url, is_cover: index === 0 })),
  })
}
</script>

<template>
  <form class="listing-form" novalidate @submit.prevent="submit">
    <fieldset class="listing-form__group">
      <legend>Basics</legend>
      <BaseInput v-model="form.title" label="Title" required :error="errors.title" />
      <BaseInput v-model="form.description" label="Description" multiline :rows="6" required :error="errors.description" />
      <div class="listing-form__grid">
        <BaseSelect v-model="form.purpose" label="Purpose" :options="options.purpose" required />
        <BaseSelect v-model="form.property_type" label="Property type" :options="options.type" required />
      </div>
    </fieldset>

    <fieldset class="listing-form__group">
      <legend>Price and size</legend>
      <div class="listing-form__grid">
        <BaseInput v-model="form.price" label="Price" type="number" :min="0" step="0.01" required :error="errors.price" />
        <BaseSelect v-model="form.currency" label="Currency" :options="options.currency" required />
        <BaseInput v-model="form.area" label="Area" type="number" :min="0" step="0.01" required :error="errors.area" />
        <BaseSelect v-model="form.area_unit" label="Unit" :options="options.unit" required />
        <BaseInput v-model.number="form.bedrooms" label="Bedrooms" type="number" :min="0" :max="50" />
        <BaseInput v-model.number="form.bathrooms" label="Bathrooms" type="number" :min="0" :max="50" />
        <BaseInput v-model="form.year_built" label="Year built" type="number" :min="1800" :error="errors.year_built" />
      </div>
    </fieldset>

    <fieldset class="listing-form__group">
      <legend>Location</legend>
      <div class="listing-form__grid">
        <BaseSelect v-model="form.country" label="Country" :options="countryOptions" placeholder="Choose a country" required />
        <BaseSelect v-model="form.city_id" label="City" :options="cityOptions" placeholder="Choose a city" required :error="errors.city_id" />
      </div>
      <BaseInput v-model="form.address" label="Address" required :error="errors.address" />
    </fieldset>

    <fieldset class="listing-form__group">
      <legend>Amenities</legend>
      <div class="listing-form__amenities">
        <label v-for="amenity in amenities" :key="amenity.id" class="listing-form__check">
          <input v-model="form.amenity_ids" type="checkbox" :value="amenity.id">
          {{ amenity.name }}
        </label>
      </div>
    </fieldset>

    <fieldset class="listing-form__group">
      <legend>Photos</legend>
      <BaseInput
        v-model="form.images"
        label="Image URLs"
        multiline
        :rows="4"
        hint="One URL per line. The first photo is the cover. At least one is needed to publish."
        :error="errors.images"
      />
    </fieldset>

    <div class="listing-form__actions">
      <BaseButton type="submit" size="lg" :loading="props.saving">{{ props.submitLabel }}</BaseButton>
    </div>
  </form>
</template>

<style scoped lang="scss">
.listing-form {
  display: grid;
  gap: $space-5;

  &__group {
    display: grid;
    gap: $space-4;
    margin: 0;
    padding: $space-5;
    border: 0;
    @include card;

    legend {
      float: left;
      width: 100%;
      margin-bottom: $space-2;
      font-weight: 700;
      font-size: $font-size-lg;
      color: $color-text-strong;
    }
  }

  &__grid {
    display: grid;
    gap: $space-3;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  }

  &__amenities {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: $space-2;
  }

  &__check {
    display: flex;
    align-items: center;
    gap: $space-2;
    cursor: pointer;
  }

  &__actions {
    display: flex;
    justify-content: flex-end;
  }
}
</style>
