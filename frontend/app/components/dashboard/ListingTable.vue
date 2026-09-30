<script setup lang="ts">
import { ROUTES } from '~/constants/routes'
import { ListingPurpose, NEXT_PROPERTY_STATUSES, PROPERTY_STATUS_LABEL, PropertyStatus } from '~/enums'
import type { PropertySummary } from '~/types/models'
import { formatDate } from '~/utils/format'

const props = defineProps<{ items: PropertySummary[]; busyId?: number | null }>()
const emit = defineEmits<{ status: [id: number, status: PropertyStatus]; remove: [item: PropertySummary] }>()

const { display } = useCurrency()

function onStatus(item: PropertySummary, event: Event): void {
  const value = (event.target as HTMLSelectElement).value as PropertyStatus
  if (value) emit('status', item.id, value)
  ;(event.target as HTMLSelectElement).value = ''
}
</script>

<template>
  <div class="table-wrap">
    <table class="table">
      <caption class="visually-hidden">My listings</caption>
      <thead>
        <tr>
          <th scope="col">Listing</th>
          <th scope="col">Price</th>
          <th scope="col">Status</th>
          <th scope="col">Published</th>
          <th scope="col"><span class="visually-hidden">Actions</span></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in props.items" :key="item.id" :aria-busy="props.busyId === item.id">
          <td>
            <div class="table__listing">
              <img v-if="item.cover_image_url" :src="item.cover_image_url" alt="" width="72" height="48">
              <div>
                <NuxtLink v-if="item.status === PropertyStatus.PUBLISHED" :to="ROUTES.property(item.slug)" class="table__title">
                  {{ item.title }}
                </NuxtLink>
                <span v-else class="table__title">{{ item.title }}</span>
                <span class="table__muted">{{ item.city.name }}</span>
              </div>
            </div>
          </td>
          <td>
            {{ display(item.price, item.currency) }}
            <span v-if="item.purpose === ListingPurpose.RENT" class="table__muted">/ month</span>
          </td>
          <td><PropertyStatusBadge :status="item.status" /></td>
          <td class="table__muted">{{ formatDate(item.published_at) }}</td>
          <td>
            <div class="table__actions">
              <label>
                <span class="visually-hidden">Change status of {{ item.title }}</span>
                <select :disabled="props.busyId === item.id" @change="onStatus(item, $event)">
                  <option value="">Move to…</option>
                  <option v-for="next in NEXT_PROPERTY_STATUSES[item.status]" :key="next" :value="next">
                    {{ PROPERTY_STATUS_LABEL[next] }}
                  </option>
                </select>
              </label>
              <BaseButton variant="outline" size="sm" :to="ROUTES.editListing(item.id)">Edit</BaseButton>
              <BaseButton variant="ghost" size="sm" :disabled="props.busyId === item.id" @click="emit('remove', item)">
                Delete
              </BaseButton>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped lang="scss">
.table-wrap {
  overflow-x: auto;
  @include card;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: $font-size-sm;

  th,
  td {
    padding: $space-3 $space-4;
    text-align: left;
    border-bottom: 1px solid $color-border;
    vertical-align: middle;
  }

  th {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: $color-text-muted;
  }

  &__listing {
    display: flex;
    align-items: center;
    gap: $space-3;
    min-width: 260px;

    img {
      border-radius: $radius-sm;
      object-fit: cover;
    }
  }

  &__title {
    display: block;
    font-weight: 600;
    color: $color-text-strong;
  }

  &__muted {
    color: $color-text-muted;
  }

  &__actions {
    display: flex;
    align-items: center;
    gap: $space-2;

    select {
      padding: 6px $space-2;
      border: 1px solid $color-border;
      border-radius: $radius-md;
      font: inherit;
    }
  }
}
</style>
