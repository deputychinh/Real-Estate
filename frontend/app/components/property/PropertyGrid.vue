<script setup lang="ts">
import type { PropertySummary } from '~/types/models'

const props = withDefaults(
  defineProps<{ items: PropertySummary[]; loading?: boolean; layout?: 'grid' | 'list'; skeletons?: number }>(),
  { loading: false, layout: 'grid', skeletons: 6 },
)
</script>

<template>
  <div class="grid" :class="`grid--${props.layout}`" :aria-busy="props.loading">
    <template v-if="props.loading">
      <div v-for="index in props.skeletons" :key="index" class="grid__skeleton">
        <BaseSkeleton height="200px" radius="16px" />
        <BaseSkeleton height="1.2rem" width="40%" />
        <BaseSkeleton height="1rem" width="80%" />
      </div>
    </template>
    <PropertyCard v-for="item in props.items" v-else :key="item.id" :property="item" :layout="props.layout" />
  </div>
</template>

<style scoped lang="scss">
.grid {
  display: grid;
  gap: $space-5;

  &--grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }

  &--list {
    grid-template-columns: 1fr;
  }

  &__skeleton {
    display: grid;
    gap: $space-2;
  }
}
</style>
