<script setup lang="ts">
import { PROPERTY_TYPE_LABEL } from '~/enums'
import type { PropertyDetail } from '~/types/models'
import { formatArea } from '~/utils/format'

const props = defineProps<{ property: PropertyDetail }>()

const facts = computed(() => [
  { icon: 'building' as const, label: 'Type', value: PROPERTY_TYPE_LABEL[props.property.property_type] },
  { icon: 'bed' as const, label: 'Bedrooms', value: String(props.property.bedrooms) },
  { icon: 'bath' as const, label: 'Bathrooms', value: String(props.property.bathrooms) },
  { icon: 'area' as const, label: 'Area', value: formatArea(props.property.area, props.property.area_unit) },
  { icon: 'calendar' as const, label: 'Year built', value: props.property.year_built ? String(props.property.year_built) : '—' },
])
</script>

<template>
  <dl class="facts">
    <div v-for="fact in facts" :key="fact.label" class="facts__item">
      <BaseIcon :name="fact.icon" :size="22" />
      <div>
        <dt>{{ fact.label }}</dt>
        <dd>{{ fact.value }}</dd>
      </div>
    </div>
  </dl>
</template>

<style scoped lang="scss">
.facts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: $space-3;
  margin: 0;

  &__item {
    display: flex;
    align-items: center;
    gap: $space-3;
    padding: $space-3 $space-4;
    border-radius: $radius-md;
    background: $color-bg-soft;
    color: $color-primary;
  }

  dt {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: $color-text-muted;
  }

  dd {
    margin: 0;
    font-weight: 700;
    color: $color-text-strong;
  }
}
</style>
