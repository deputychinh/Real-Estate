import { defineStore } from 'pinia'
import { STORAGE_KEYS } from '~/constants/storage-keys'
import { UserRole } from '~/enums'
import type { AccessTokenResponse, LoginRequest, RegisterRequest, UserRead } from '~/types/models'

/** The access token lives only in memory; the refresh token is an httpOnly cookie the page cannot read. */
export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(null)
  const user = ref<UserRead | null>(null)
  const restored = ref(false)

  const isAuthenticated = computed(() => accessToken.value !== null && user.value !== null)
  const isAgent = computed(() => user.value?.role === UserRole.AGENT || user.value?.role === UserRole.ADMIN)
  const isInvestor = computed(() => user.value?.role === UserRole.INVESTOR)

  function apply(session: AccessTokenResponse): void {
    accessToken.value = session.access_token
    user.value = session.user
  }

  function clear(): void {
    accessToken.value = null
    user.value = null
  }

  async function login(payload: LoginRequest): Promise<void> {
    apply(await useServices().auth.login(payload))
  }

  async function register(payload: RegisterRequest): Promise<void> {
    await useServices().auth.register(payload)
    await login({ email: payload.email, password: payload.password })
  }

  /** True when a new access token was issued. A missing or expired cookie simply means "logged out". */
  async function refresh(): Promise<boolean> {
    try {
      apply(await useServices().auth.refresh())
      return true
    } catch {
      clear()
      return false
    }
  }

  async function restore(): Promise<void> {
    if (restored.value) return
    // No hint cookie = never signed in here: skip the refresh call instead of collecting a 401.
    if (useCookie(STORAGE_KEYS.sessionHint).value) await refresh()
    restored.value = true
  }

  async function logout(): Promise<void> {
    try {
      await useServices().auth.logout()
    } finally {
      clear()
    }
  }

  return { accessToken, user, restored, isAuthenticated, isAgent, isInvestor, login, register, refresh, restore, logout }
})
