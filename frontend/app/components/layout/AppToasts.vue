<script setup lang="ts">
const { toasts, dismiss } = useNotify()
</script>

<template>
  <div class="toasts" aria-live="polite" aria-atomic="false">
    <TransitionGroup name="toast">
      <div v-for="toast in toasts" :key="toast.id" class="toast" :class="`toast--${toast.tone}`" role="status">
        <span>{{ toast.message }}</span>
        <button type="button" class="toast__close" aria-label="Dismiss" @click="dismiss(toast.id)">
          <BaseIcon name="close" :size="14" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped lang="scss">
.toasts {
  position: fixed;
  right: $space-4;
  bottom: $space-4;
  z-index: 50;
  display: grid;
  gap: $space-2;
  max-width: min(360px, calc(100vw - 32px));
}

.toast {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: $space-3;
  padding: $space-3 $space-4;
  border-radius: $radius-md;
  background: $color-secondary;
  color: $color-bg;
  box-shadow: $shadow-hover;
  border-left: 4px solid $color-info;

  &--success {
    border-left-color: $color-success;
  }

  &--danger {
    border-left-color: $color-danger;
  }

  &__close {
    display: inline-flex;
    border: 0;
    background: none;
    color: inherit;
    cursor: pointer;
  }
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
