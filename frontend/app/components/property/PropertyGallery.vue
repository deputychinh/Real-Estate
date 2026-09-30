<script setup lang="ts">
const props = defineProps<{ images: { url: string; is_cover: boolean }[]; title: string }>()

const active = ref(Math.max(props.images.findIndex((image) => image.is_cover), 0))
const current = computed(() => props.images[active.value])
</script>

<template>
  <div class="gallery">
    <div class="gallery__main">
      <img v-if="current" :src="current.url" :alt="`${props.title}, photo ${active + 1} of ${props.images.length}`" width="1200" height="800">
    </div>
    <div v-if="props.images.length > 1" class="gallery__thumbs" role="list">
      <button
        v-for="(image, index) in props.images"
        :key="image.url"
        type="button"
        role="listitem"
        class="gallery__thumb"
        :class="{ 'gallery__thumb--active': index === active }"
        :aria-label="`Show photo ${index + 1}`"
        :aria-current="index === active ? 'true' : undefined"
        @click="active = index"
      >
        <img :src="image.url" alt="" loading="lazy" width="160" height="110">
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.gallery {
  display: grid;
  gap: $space-3;

  &__main {
    aspect-ratio: 3 / 2;
    overflow: hidden;
    border-radius: $radius-lg;
    background: $color-bg-soft;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  &__thumbs {
    display: flex;
    gap: $space-2;
    overflow-x: auto;
  }

  &__thumb {
    flex: 0 0 110px;
    padding: 0;
    border: 2px solid transparent;
    border-radius: $radius-md;
    overflow: hidden;
    cursor: pointer;
    background: none;

    img {
      width: 100%;
      aspect-ratio: 3 / 2;
      object-fit: cover;
    }

    &--active {
      border-color: $color-primary;
    }
  }
}
</style>
