import { LISTING_PURPOSE_LABEL, PROPERTY_TYPE_LABEL } from '~/enums'
import type { PropertyDetail } from '~/types/models'
import { ROUTES } from '~/constants/routes'

/** Title, description, Open Graph and schema.org JSON-LD for a listing page (FR-12). */
export function useListingSeo(listing: Ref<PropertyDetail | null | undefined>) {
  const { public: config } = useRuntimeConfig()

  useSeoMeta({
    title: () => listing.value?.title ?? 'Listing',
    description: () => (listing.value ? listing.value.description.slice(0, 160) : undefined),
    ogTitle: () => listing.value?.title,
    ogDescription: () => listing.value?.description.slice(0, 160),
    ogImage: () => listing.value?.cover_image_url ?? undefined,
    ogType: 'website',
  })

  useHead(() => {
    const item = listing.value
    if (!item) return {}
    const url = `${config.siteUrl}${ROUTES.property(item.slug)}`
    const jsonLd = {
      '@context': 'https://schema.org',
      '@type': 'RealEstateListing',
      name: item.title,
      description: item.description,
      url,
      image: item.images.map((image) => image.url),
      datePosted: item.published_at,
      offers: { '@type': 'Offer', price: item.price, priceCurrency: item.currency },
      about: {
        '@type': 'Accommodation',
        name: `${PROPERTY_TYPE_LABEL[item.property_type]} ${LISTING_PURPOSE_LABEL[item.purpose].toLowerCase()}`,
        numberOfRooms: item.bedrooms,
        floorSize: { '@type': 'QuantitativeValue', value: item.area, unitCode: item.area_unit === 'SQM' ? 'MTK' : 'FTK' },
        address: { '@type': 'PostalAddress', streetAddress: item.address, addressLocality: item.city.name, addressCountry: item.city.country_code },
      },
    }
    return {
      link: [{ rel: 'canonical', href: url }],
      script: [{ type: 'application/ld+json', innerHTML: JSON.stringify(jsonLd) }],
    }
  })
}
