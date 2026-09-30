import { defineVitestConfig } from '@nuxt/test-utils/config'

// Runs inside a Nuxt environment, so components get auto-imports, stores and runtime config.
export default defineVitestConfig({
  test: {
    environment: 'nuxt',
    include: ['tests/**/*.test.ts'],
    environmentOptions: { nuxt: { domEnvironment: 'happy-dom' } },
  },
})
