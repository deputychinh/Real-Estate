<script setup lang="ts">
import { INQUIRY_STATUS_TONE } from '~/constants/colors'
import { ROUTES } from '~/constants/routes'
import { INQUIRY_STATUS_LABEL, NEXT_INQUIRY_STATUSES, type InquiryStatus } from '~/enums'
import type { InquiryRead } from '~/types/models'
import { formatDate } from '~/utils/format'

const props = defineProps<{ items: InquiryRead[]; busyId?: number | null }>()
const emit = defineEmits<{ status: [id: number, status: InquiryStatus] }>()
</script>

<template>
  <ul class="inquiries">
    <li v-for="item in props.items" :key="item.id" class="inquiry">
      <div class="inquiry__head">
        <div>
          <p class="inquiry__from">{{ item.investor.full_name }} · <a :href="`mailto:${item.investor.email}`">{{ item.investor.email }}</a></p>
          <NuxtLink :to="ROUTES.property(item.property.slug)" class="inquiry__listing">{{ item.property.title }}</NuxtLink>
        </div>
        <div class="inquiry__meta">
          <BaseBadge :tone="INQUIRY_STATUS_TONE[item.status]">{{ INQUIRY_STATUS_LABEL[item.status] }}</BaseBadge>
          <span>{{ formatDate(item.created_at) }}</span>
        </div>
      </div>
      <p class="inquiry__message">{{ item.message }}</p>
      <div class="inquiry__actions">
        <span v-if="item.phone" class="inquiry__phone"><BaseIcon name="phone" :size="14" /> {{ item.phone }}</span>
        <BaseButton
          v-for="next in NEXT_INQUIRY_STATUSES[item.status]"
          :key="next"
          size="sm"
          variant="outline"
          :loading="props.busyId === item.id"
          @click="emit('status', item.id, next)"
        >
          Mark {{ INQUIRY_STATUS_LABEL[next].toLowerCase() }}
        </BaseButton>
      </div>
    </li>
  </ul>
</template>

<style scoped lang="scss">
.inquiries {
  display: grid;
  gap: $space-4;
  margin: 0;
  padding: 0;
  list-style: none;
}

.inquiry {
  padding: $space-5;
  @include card;

  &__head {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: $space-3;
  }

  &__from {
    margin: 0;
    font-weight: 600;
    color: $color-text-strong;

    a {
      color: $color-primary;
    }
  }

  &__listing {
    font-size: $font-size-sm;
    color: $color-text-muted;

    &:hover {
      color: $color-primary;
    }
  }

  &__meta {
    display: flex;
    align-items: center;
    gap: $space-3;
    font-size: $font-size-sm;
    color: $color-text-muted;
  }

  &__message {
    margin: $space-3 0;
    white-space: pre-line;
  }

  &__actions {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: $space-2;
  }

  &__phone {
    display: inline-flex;
    align-items: center;
    gap: $space-1;
    margin-right: auto;
    font-size: $font-size-sm;
  }
}
</style>
