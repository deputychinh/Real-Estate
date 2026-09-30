<script setup lang="ts">
import { ROUTES } from '~/constants/routes'
import { useAuthStore } from '~/stores/auth.store'
import { useFavoritesStore } from '~/stores/favorites.store'
import { toApiError } from '~/utils/api-error'

const props = withDefaults(defineProps<{ propertyId: number; title: string; floating?: boolean }>(), { floating: true })

const auth = useAuthStore()
const favorites = useFavoritesStore()
const notify = useNotify()
const route = useRoute()

const active = computed(() => favorites.has(props.propertyId))

async function toggle(): Promise<void> {
  if (!auth.isAuthenticated) {
    await navigateTo({ path: ROUTES.login, query: { redirect: route.fullPath } })
    return
  }
  try {
    await favorites.toggle(props.propertyId)
  } catch (error) {
    notify.error(toApiError(error).message)
  }
}
</script>

<template>
  <ClientOnly>
    <button
      type="button"
      class="favorite"
      :class="{ 'favorite--active': active, 'favorite--floating': props.floating }"
      :aria-pressed="active"
      :aria-label="active ? `Remove ${props.title} from saved` : `Save ${props.title}`"
      :disabled="favorites.isPending(props.propertyId)"
      @click.prevent.stop="toggle"
    >
      <BaseIcon name="heart" :size="18" :filled="active" />
    </button>
  </ClientOnly>
</template>

<style scoped lang="scss">
.favorite {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: 1px solid $color-border;
  border-radius: 50%;
  background: $color-bg;
  color: $color-text-strong;
  cursor: pointer;
  transition:
    color $transition,
    transform $transition;

  &:hover {
    color: $color-primary;
    transform: scale(1.06);
  }

  &--active {
    color: $color-primary;
  }

  &--floating {
    position: absolute;
    top: $space-3;
    right: $space-3;
    border: 0;
    box-shadow: $shadow-card;
  }
}
</style>
