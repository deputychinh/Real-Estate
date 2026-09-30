<template>
  <div class="layout">
    <a href="#main" class="skip-link">Skip to content</a>
    <AppHeader />
    <main id="main" class="layout__main">
      <slot />
    </main>
    <AppFooter />
  </div>
</template>

<style scoped lang="scss">
.layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;

  &__main {
    flex: 1;
  }
}

.skip-link {
  position: absolute;
  left: $space-4;
  top: -48px;
  z-index: 30;
  padding: $space-2 $space-4;
  border-radius: $radius-md;
  background: $color-secondary;
  color: $color-bg;

  &:focus {
    top: $space-2;
  }
}
</style>
