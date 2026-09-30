import { AREA_UNIT_LABEL, type AreaUnit, type Currency } from '~/enums'

// Currencies whose minor unit is never shown for property prices.
const WHOLE_UNITS = new Set<string>(['VND'])

export function formatMoney(amount: number, currency: Currency | string, compact = false): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    notation: compact ? 'compact' : 'standard',
    maximumFractionDigits: compact ? 1 : WHOLE_UNITS.has(currency) || amount >= 1000 ? 0 : 2,
  }).format(amount)
}

/** Convert with a table of "USD value of one unit", as returned by /currencies/rates. */
export function convertAmount(
  amount: number,
  from: Currency | string,
  to: Currency | string,
  usdPerUnit: Record<string, string | number>,
): number {
  if (from === to) return amount
  const fromRate = Number(usdPerUnit[from])
  const toRate = Number(usdPerUnit[to])
  if (!fromRate || !toRate) return amount
  return (amount * fromRate) / toRate
}

export function formatArea(area: number | string, unit: AreaUnit): string {
  return `${new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(Number(area))} ${AREA_UNIT_LABEL[unit]}`
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return '—'
  return new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' }).format(
    new Date(value),
  )
}
