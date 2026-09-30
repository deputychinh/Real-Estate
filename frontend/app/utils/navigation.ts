import type { LocationQueryValue } from 'vue-router'

/** Only same-site paths are allowed after login ("/x", not "//evil.com" or "https://…"): no open redirect. */
export function safeRedirect(value: LocationQueryValue | LocationQueryValue[] | undefined, fallback = '/'): string {
  const raw = Array.isArray(value) ? value[0] : value
  if (typeof raw !== 'string' || !raw.startsWith('/') || raw.startsWith('//') || raw.includes('\\')) return fallback
  return raw
}
