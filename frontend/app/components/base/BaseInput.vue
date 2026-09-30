<script setup lang="ts">
const model = defineModel<string | number | null>({ default: '' })

const props = withDefaults(
  defineProps<{
    label: string
    type?: string
    error?: string
    hint?: string
    placeholder?: string
    required?: boolean
    autocomplete?: string
    multiline?: boolean
    rows?: number
    hideLabel?: boolean
    min?: number
    max?: number
    step?: string
  }>(),
  {
    type: 'text',
    error: undefined,
    hint: undefined,
    placeholder: undefined,
    required: false,
    autocomplete: undefined,
    multiline: false,
    rows: 4,
    hideLabel: false,
    min: undefined,
    max: undefined,
    step: undefined,
  },
)

const id = useId()
const describedBy = computed(() => (props.error ? `${id}-error` : props.hint ? `${id}-hint` : undefined))
</script>

<template>
  <div class="field" :class="{ 'field--error': props.error }">
    <label :for="id" class="field__label" :class="{ 'visually-hidden': props.hideLabel }">
      {{ props.label }}<span v-if="props.required" class="field__required" aria-hidden="true">*</span>
    </label>
    <textarea
      v-if="props.multiline"
      :id="id"
      v-model="model"
      class="field__control"
      :rows="props.rows"
      :placeholder="props.placeholder"
      :required="props.required"
      :aria-invalid="props.error ? 'true' : undefined"
      :aria-describedby="describedBy"
    />
    <input
      v-else
      :id="id"
      v-model="model"
      class="field__control"
      :type="props.type"
      :placeholder="props.placeholder"
      :required="props.required"
      :autocomplete="props.autocomplete"
      :min="props.min"
      :max="props.max"
      :step="props.step"
      :aria-invalid="props.error ? 'true' : undefined"
      :aria-describedby="describedBy"
    >
    <p v-if="props.error" :id="`${id}-error`" class="field__error" role="alert">{{ props.error }}</p>
    <p v-else-if="props.hint" :id="`${id}-hint`" class="field__hint">{{ props.hint }}</p>
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
    padding: $space-3;
    border: 1px solid $color-border;
    border-radius: $radius-md;
    font: inherit;
    line-height: 1.5;
    color: $color-text-strong;
    background: $color-bg;
    transition: border-color $transition;

    // Fixed height on the single-line control only, so it matches BaseSelect exactly; textarea
    // keeps its height from `rows` (multiline notes/descriptions must not be clamped to one line).
    &:not(textarea) {
      height: $control-height;
    }

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

  &__hint {
    margin: 0;
    font-size: $font-size-sm;
    color: $color-text-muted;
  }
}
</style>
