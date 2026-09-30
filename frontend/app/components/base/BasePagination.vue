<script setup lang="ts">
const props = defineProps<{ page: number; pages: number }>()
const emit = defineEmits<{ 'update:page': [page: number] }>()

const WINDOW = 2

// 1 … 4 5 [6] 7 8 … 20
const items = computed<(number | 'gap')[]>(() => {
  const result: (number | 'gap')[] = []
  for (let page = 1; page <= props.pages; page += 1) {
    const edge = page === 1 || page === props.pages
    const near = Math.abs(page - props.page) <= WINDOW
    if (edge || near) result.push(page)
    else if (result.at(-1) !== 'gap') result.push('gap')
  }
  return result
})

function go(page: number): void {
  if (page >= 1 && page <= props.pages && page !== props.page) emit('update:page', page)
}
</script>

<template>
  <nav v-if="props.pages > 1" class="pagination" aria-label="Pagination">
    <button type="button" class="pagination__item" :disabled="props.page <= 1" aria-label="Previous page" @click="go(props.page - 1)">
      ‹
    </button>
    <template v-for="(item, index) in items" :key="`${item}-${index}`">
      <span v-if="item === 'gap'" class="pagination__gap" aria-hidden="true">…</span>
      <button
        v-else
        type="button"
        class="pagination__item"
        :class="{ 'pagination__item--active': item === props.page }"
        :aria-current="item === props.page ? 'page' : undefined"
        :aria-label="`Page ${item}`"
        @click="go(item)"
      >
        {{ item }}
      </button>
    </template>
    <button type="button" class="pagination__item" :disabled="props.page >= props.pages" aria-label="Next page" @click="go(props.page + 1)">
      ›
    </button>
  </nav>
</template>

<style scoped lang="scss">
.pagination {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: $space-2;
  margin-top: $space-6;

  &__item {
    min-width: 40px;
    height: 40px;
    padding: 0 $space-2;
    border: 1px solid $color-border;
    border-radius: $radius-md;
    background: $color-bg;
    font: inherit;
    font-weight: 600;
    color: $color-text-strong;
    cursor: pointer;

    &:hover:not(:disabled) {
      border-color: $color-primary;
      color: $color-primary;
    }

    &:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }

    &--active {
      background: $color-primary;
      border-color: $color-primary;
      color: $color-bg;

      &:hover:not(:disabled) {
        color: $color-bg;
      }
    }
  }

  &__gap {
    align-self: center;
    color: $color-text-muted;
  }
}
</style>
