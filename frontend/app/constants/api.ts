// Every backend path in one place; services build URLs only from here.
export const API_ENDPOINTS = {
  auth: {
    register: '/auth/register',
    login: '/auth/login',
    refresh: '/auth/refresh',
    logout: '/auth/logout',
  },
  users: { me: '/users/me' },
  properties: {
    search: '/properties',
    featured: '/properties/featured',
    bySlug: (slug: string) => `/properties/${encodeURIComponent(slug)}`,
    similar: (slug: string) => `/properties/${encodeURIComponent(slug)}/similar`,
    create: '/properties',
    update: (id: number) => `/properties/${id}`,
    publish: (id: number) => `/properties/${id}/publish`,
    status: (id: number) => `/properties/${id}/status`,
    remove: (id: number) => `/properties/${id}`,
    inquiries: (id: number) => `/properties/${id}/inquiries`,
  },
  agent: {
    listings: '/agents/me/properties',
    listing: (id: number) => `/agents/me/properties/${id}`,
    inquiries: '/agents/me/inquiries',
  },
  inquiries: {
    mine: '/inquiries/mine',
    status: (id: number) => `/inquiries/${id}`,
  },
  favorites: {
    list: '/favorites',
    ids: '/favorites/ids',
    toggle: (propertyId: number) => `/favorites/${propertyId}`,
  },
  lookups: {
    countries: '/locations/countries',
    cities: '/locations/cities',
    amenities: '/amenities',
    rates: '/currencies/rates',
  },
} as const
