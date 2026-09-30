<script setup lang="ts">
import type { IconName } from './BaseIcon.vue'

const props = withDefaults(defineProps<{ title: string; message?: string; icon?: IconName }>(), {
  message: undefined,
  icon: 'search',
})
</script>

<template>
  <div class="empty">
    <span class="empty__icon"><BaseIcon :name="props.icon" :size="28" /></span>
    <h3 class="empty__title">{{ props.title }}</h3>
    <p v-if="props.message" class="empty__message">{{ props.message }}</p>
    <div v-if="$slots.default" class="empty__actions"><slot /></div>
  </div>
</template>

<style scoped lang="scss">
.empty {
  padding: $space-7 $space-4;
  text-align: center;
  background: $color-bg-soft;
  border-radius: $radius-lg;

  &__icon {
    display: inline-flex;
    padding: $space-4;
    border-radius: 50%;
    background: $color-primary-soft;
    color: $color-primary;
    margin-bottom: $space-3;
  }

  &__title {
    font-size: $font-size-lg;
  }

  &__message {
    margin: 0 auto $space-4;
    max-width: 420px;
    color: $color-text-muted;
  }
}
</style>
