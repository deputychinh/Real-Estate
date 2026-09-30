export const ROUTES = {
  home: '/',
  properties: '/properties',
  property: (slug: string) => `/properties/${slug}`,
  login: '/login',
  register: '/register',
  favorites: '/favorites',
  dashboard: '/dashboard',
  newListing: '/dashboard/properties/new',
  editListing: (id: number) => `/dashboard/properties/${id}/edit`,
  inquiries: '/dashboard/inquiries',
  about: '/about',
} as const
