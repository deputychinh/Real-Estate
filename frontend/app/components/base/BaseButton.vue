<script setup lang="ts">
type Variant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
type Size = 'sm' | 'md' | 'lg'

const props = withDefaults(
  defineProps<{
    variant?: Variant
    size?: Size
    to?: string
    type?: 'button' | 'submit' | 'reset'
    loading?: boolean
    disabled?: boolean
    block?: boolean
  }>(),
  { variant: 'primary', size: 'md', to: undefined, type: 'button', loading: false, disabled: false, block: false },
)

const classes = computed(() => ['btn', `btn--${props.variant}`, `btn--${props.size}`, { 'btn--block': props.block }])
</script>

<template>
  <NuxtLink v-if="props.to && !props.disabled" :to="props.to" :class="classes">
    <slot />
  </NuxtLink>
  <button
    v-else
    :type="props.type"
    :class="classes"
    :disabled="props.disabled || props.loading"
    :aria-busy="props.loading || undefined"
  >
    <span v-if="props.loading" class="btn__spinner" aria-hidden="true" />
    <slot />
  </button>
</template>

<style scoped lang="scss">
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: $space-2;
  border: 1px solid transparent;
  border-radius: $radius-md;
  font-family: inherit;
  font-weight: 600;
  line-height: 1;
  cursor: pointer;
  transition:
    background $transition,
    color $transition,
    border-color $transition,
    box-shadow $transition;
  white-space: nowrap;

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  &--sm {
    padding: $space-2 $space-3;
    font-size: $font-size-sm;
  }

  &--md {
    padding: $space-3 $space-5;
    font-size: $font-size-base;
  }

  &--lg {
    padding: $space-4 $space-6;
    font-size: $font-size-lg;
  }

  &--block {
    width: 100%;
  }

  &--primary {
    background: $color-primary;
    color: $color-bg;

    &:hover:not(:disabled) {
      background: $color-primary-dark;
    }
  }

  &--secondary {
    background: $color-secondary;
    color: $color-bg;

    &:hover:not(:disabled) {
      box-shadow: $shadow-hover;
    }
  }

  &--outline {
    background: transparent;
    border-color: $color-border;
    color: $color-text-strong;

    &:hover:not(:disabled) {
      border-color: $color-primary;
      color: $color-primary;
    }
  }

  &--ghost {
    background: transparent;
    color: $color-text-strong;

    &:hover:not(:disabled) {
      color: $color-primary;
    }
  }

  &--danger {
    background: $color-danger;
    color: $color-bg;
  }

  &__spinner {
    width: 14px;
    height: 14px;
    border: 2px solid currentColor;
    border-right-color: transparent;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
