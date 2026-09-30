<script setup lang="ts">
export interface SelectOption {
  value: string | number
  label: string
}

const model = defineModel<string | number | undefined>()

const props = withDefaults(
  defineProps<{
    label: string
    options: SelectOption[]
    placeholder?: string
    error?: string
    required?: boolean
    hideLabel?: boolean
  }>(),
  { placeholder: undefined, error: undefined, required: false, hideLabel: false },
)

const id = useId()

// Native <select> gives strings; keep numeric options numeric.
const selected = computed({
  get: () => (model.value === undefined ? '' : String(model.value)),
  set: (raw: string) => {
    if (raw === '') {
      model.value = undefined
      return
    }
    const option = props.options.find((item) => String(item.value) === raw)
    model.value = option?.value
  },
})
</script>

<template>
  <div class="field" :class="{ 'field--error': props.error }">
    <label :for="id" class="field__label" :class="{ 'visually-hidden': props.hideLabel }">
      {{ props.label }}<span v-if="props.required" class="field__required" aria-hidden="true">*</span>
    </label>
    <select
      :id="id"
      v-model="selected"
      class="field__control"
      :required="props.required"
      :aria-invalid="props.error ? 'true' : undefined"
      :aria-describedby="props.error ? `${id}-error` : undefined"
    >
      <option v-if="props.placeholder !== undefined" value="">{{ props.placeholder }}</option>
      <option v-for="option in props.options" :key="option.value" :value="String(option.value)">
        {{ option.label }}
      </option>
    </select>
    <p v-if="props.error" :id="`${id}-error`" class="field__error" role="alert">{{ props.error }}</p>
  </div>
</template>

<style scoped lang="scss">
.field {
  display: flex;
  flex-direction: column;
  gap: $space-1;

  &__label {
    font-size: $font-size-sm;
    font-weight: 600;
    color: $color-text-strong;
  }

  &__required {
    color: $color-danger;
    margin-left: 2px;
  }

  &__control {
    width: 100%;
    height: $control-height; // matches BaseInput's single-line height exactly
    padding: $space-3;
    border: 1px solid $color-border;
    border-radius: $radius-md;
    font: inherit;
    line-height: 1.5;
    color: $color-text-strong;
    background: $color-bg;
    cursor: pointer;

    &:focus {
      border-color: $color-primary;
      outline: none;
      box-shadow: 0 0 0 3px $color-primary-soft;
    }
  }

  &--error &__control {
    border-color: $color-danger;
  }

  &__error {
    margin: 0;
    font-size: $font-size-sm;
    color: $color-danger;
  }
}
</style>
