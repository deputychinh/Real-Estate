<script setup lang="ts">
import { ListingPurpose, type Currency } from '~/enums'

const props = withDefaults(
  defineProps<{ price: string | number; currency: Currency; purpose: ListingPurpose; size?: 'md' | 'lg' }>(),
  { size: 'md' },
)

const { display, original, currency: viewerCurrency } = useCurrency()
const converted = computed(() => props.currency !== viewerCurrency.value)
</script>

<template>
  <p class="price" :class="`price--${props.size}`">
    <span class="price__amount">{{ display(props.price, props.currency) }}</span>
    <span v-if="props.purpose === ListingPurpose.RENT" class="price__period">/ month</span>
    <span v-if="converted" class="price__original">≈ {{ original(props.price, props.currency) }}</span>
  </p>
</template>

<style scoped lang="scss">
.price {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0 $space-2;
  margin: 0;

  &__amount {
    font-weight: 700;
    color: $color-primary;
  }

  &--md &__amount {
    font-size: $font-size-lg;
  }

  &--lg &__amount {
    font-size: $font-size-2xl;
  }

  &__period {
    font-size: $font-size-sm;
    color: $color-text-muted;
  }

  &__original {
    width: 100%;
    font-size: 0.8rem;
    color: $color-text-muted;
  }
}
</style>
