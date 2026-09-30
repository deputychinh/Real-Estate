/**
 * Same-origin proxy for /api/v1/** to the FastAPI service. The browser never talks to another origin,
 * so the httpOnly refresh cookie works without CORS. On AWS, CloudFront routes /api/* to the API
 * directly and this handler is not used.
 */
export default defineEventHandler((event) => {
  const { apiBaseServer } = useRuntimeConfig(event)
  const upstreamPath = event.path.replace(/^\/api\/v1/, '')
  return proxyRequest(event, `${apiBaseServer}${upstreamPath}`)
})
