import { createAuthService } from './auth.service'
import { createFavoriteService } from './favorite.service'
import type { ApiRequest } from './http'
import { createInquiryService } from './inquiry.service'
import { createLookupService } from './lookup.service'
import { createPropertyService } from './property.service'

export function createServices(request: ApiRequest) {
  return {
    auth: createAuthService(request),
    properties: createPropertyService(request),
    favorites: createFavoriteService(request),
    inquiries: createInquiryService(request),
    lookups: createLookupService(request),
  }
}

export type Services = ReturnType<typeof createServices>
