<script setup lang="ts">
import type { BadgeTone } from '~/constants/colors'

const props = withDefaults(defineProps<{ tone?: BadgeTone; solid?: boolean }>(), { tone: 'neutral', solid: false })
</script>

<template>
  <span class="badge" :class="[`badge--${props.tone}`, { 'badge--solid': props.solid }]"><slot /></span>
</template>

<style scoped lang="scss">
@use 'sass:color';

$tones: (
  'primary': $color-primary,
  'success': $color-success,
  'info': $color-info,
  'warning': $color-warning,
  'danger': $color-danger,
  'neutral': $color-text-muted,
);

.badge {
  display: inline-flex;
  align-items: center;
  padding: 2px $space-3;
  border-radius: $radius-pill;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  white-space: nowrap;

  @each $name, $tone in $tones {
    &--#{$name} {
      color: $tone;
      background: color.mix($tone, $color-bg, 12%);
    }

    &--#{$name}.badge--solid {
      color: $color-bg;
      background: $tone;
    }
  }
}
</style>
