<script setup lang="ts">
const props = withDefaults(defineProps<{ height?: string; width?: string; radius?: string }>(), {
  height: '1rem',
  width: '100%',
  radius: '8px',
})
</script>

<template>
  <span
    class="skeleton"
    :style="{ height: props.height, width: props.width, borderRadius: props.radius }"
    aria-hidden="true"
  />
</template>

<style scoped lang="scss">
.skeleton {
  display: block;
  background: linear-gradient(90deg, $color-bg-soft 25%, $color-border 50%, $color-bg-soft 75%);
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite;
}

@keyframes shimmer {
  to {
    background-position: -200% 0;
  }
}
</style>
