// Rendering per route group (plan §7.1): public pages are server-rendered for SEO;
// the dashboard and the watchlist are per-user, so they render in the browser only.
export default defineNuxtConfig({
  compatibilityDate: '2026-09-01',
  devtools: { enabled: false },
  modules: ['@pinia/nuxt', '@nuxt/eslint', '@nuxt/test-utils/module'],
  // Components are named by file name only (AppHeader, not LayoutAppHeader).
  components: [{ path: '~/components', pathPrefix: false }],
  css: ['~/assets/styles/main.scss'],
  vite: {
    css: {
      preprocessorOptions: {
        scss: { additionalData: '@use "~/assets/styles/tokens" as *;\n@use "~/assets/styles/mixins" as *;\n' },
      },
    },
  },
  runtimeConfig: {
    // Server-side calls go straight to the API (inside Docker/VPC); override with NUXT_API_BASE_SERVER.
    apiBaseServer: 'http://127.0.0.1:8000/api/v1',
    public: {
      apiBase: '/api/v1', // browser calls stay same-origin (proxied locally, CloudFront on AWS)
      siteUrl: 'http://localhost:3000',
    },
  },
  routeRules: {
    '/dashboard/**': { ssr: false },
    '/favorites': { ssr: false },
  },
  app: {
    head: {
      htmlAttrs: { lang: 'en' },
      titleTemplate: '%s · Estatia',
      meta: [{ name: 'viewport', content: 'width=device-width, initial-scale=1' }],
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap',
        },
      ],
    },
  },
  typescript: {
    strict: true,
    // Fail the typecheck on a component name that does not resolve (renders as an unknown HTML tag otherwise).
    tsConfig: { vueCompilerOptions: { checkUnknownComponents: true } },
  },
  eslint: { config: { stylistic: false } },
})
