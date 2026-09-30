import { mountSuspended } from '@nuxt/test-utils/runtime'
import { describe, expect, it } from 'vitest'
import BasePagination from '~/components/base/BasePagination.vue'

describe('BasePagination', () => {
  it('collapses long ranges and marks the current page', async () => {
    const pagination = await mountSuspended(BasePagination, { props: { page: 6, pages: 20 } })
    const labels = pagination.findAll('.pagination__item, .pagination__gap').map((item) => item.text())
    expect(labels).toEqual(['‹', '1', '…', '4', '5', '6', '7', '8', '…', '20', '›'])
    expect(pagination.find('[aria-current="page"]').text()).toBe('6')
  })

  it('emits the chosen page and disables the edges', async () => {
    const pagination = await mountSuspended(BasePagination, { props: { page: 1, pages: 3 } })
    expect(pagination.find('[aria-label="Previous page"]').attributes('disabled')).toBeDefined()
    await pagination.find('[aria-label="Page 3"]').trigger('click')
    expect(pagination.emitted('update:page')).toEqual([[3]])
  })

  it('renders nothing for a single page', async () => {
    const pagination = await mountSuspended(BasePagination, { props: { page: 1, pages: 1 } })
    expect(pagination.find('nav').exists()).toBe(false)
  })
})
