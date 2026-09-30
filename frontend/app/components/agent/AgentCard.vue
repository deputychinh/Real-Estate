<script setup lang="ts">
import type { PropertyDetail } from '~/types/models'

const props = defineProps<{ agent: PropertyDetail['agent'] }>()
const initials = computed(() =>
  props.agent.full_name
    .split(' ')
    .map((part) => part[0])
    .slice(0, 2)
    .join(''),
)
</script>

<template>
  <section class="agent" aria-label="Listing agent">
    <img v-if="props.agent.avatar_url" :src="props.agent.avatar_url" :alt="props.agent.full_name" class="agent__avatar" width="64" height="64">
    <span v-else class="agent__avatar agent__avatar--initials" aria-hidden="true">{{ initials }}</span>
    <div>
      <p class="agent__role">Listing agent</p>
      <p class="agent__name">{{ props.agent.full_name }}</p>
      <p class="agent__contact"><BaseIcon name="mail" :size="14" /> {{ props.agent.email }}</p>
      <p v-if="props.agent.phone" class="agent__contact"><BaseIcon name="phone" :size="14" /> {{ props.agent.phone }}</p>
    </div>
  </section>
</template>

<style scoped lang="scss">
.agent {
  display: flex;
  gap: $space-4;
  align-items: center;

  &__avatar {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    object-fit: cover;

    &--initials {
      display: flex;
      align-items: center;
      justify-content: center;
      background: $color-primary-soft;
      color: $color-primary;
      font-weight: 700;
    }
  }

  &__role {
    margin: 0;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: $color-text-muted;
  }

  &__name {
    margin: 0;
    font-weight: 700;
    color: $color-text-strong;
  }

  &__contact {
    display: flex;
    align-items: center;
    gap: $space-1;
    margin: 0;
    font-size: $font-size-sm;
  }
}
</style>
