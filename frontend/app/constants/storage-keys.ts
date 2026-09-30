// Cookies (not localStorage), so SSR renders the same currency and view as the browser: no hydration mismatch.
export const STORAGE_KEYS = {
  currency: 'pref_currency',
  viewMode: 'pref_view_mode',
  sessionHint: 'session_hint', // set/cleared by the API with the refresh cookie; holds no secret
} as const
