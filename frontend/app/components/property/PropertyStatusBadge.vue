<script setup lang="ts">
import { PROPERTY_STATUS_TONE } from '~/constants/colors'
import { PROPERTY_STATUS_LABEL, type PropertyStatus } from '~/enums'

const props = defineProps<{ status: PropertyStatus }>()
</script>

<template>
  <BaseBadge :tone="PROPERTY_STATUS_TONE[props.status]">{{ PROPERTY_STATUS_LABEL[props.status] }}</BaseBadge>
</template>
