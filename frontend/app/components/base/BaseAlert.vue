<script setup lang="ts">
const props = withDefaults(defineProps<{ tone?: 'danger' | 'success' | 'info' }>(), { tone: 'danger' })
</script>

<template>
  <div class="alert" :class="`alert--${props.tone}`" :role="props.tone === 'danger' ? 'alert' : 'status'">
    <slot />
  </div>
</template>

<style scoped lang="scss">
@use 'sass:color';

.alert {
  padding: $space-3 $space-4;
  border-radius: $radius-md;
  font-size: $font-size-sm;
  border-left: 4px solid currentColor;

  &--danger {
    color: $color-danger;
    background: color.mix($color-danger, $color-bg, 8%);
  }

  &--success {
    color: $color-success;
    background: color.mix($color-success, $color-bg, 8%);
  }

  &--info {
    color: $color-info;
    background: color.mix($color-info, $color-bg, 8%);
  }
}
</style>
