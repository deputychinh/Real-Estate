<script setup lang="ts">
// Exchange rates are loaded once on the server and reused by every price on the page.
// If the call fails, prices show in each listing's own currency (useCurrency falls back).
const services = useServices()
const rates = useExchangeRates()
await callOnce('fx-rates', async () => {
  rates.value = await services.lookups.rates().catch(() => null)
})
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
  <AppToasts />
</template>
