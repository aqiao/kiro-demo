import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import App from './App.vue'

describe('App', () => {
  it('keeps room creation disabled until privacy is acknowledged', async () => {
    const wrapper = mount(App)
    const button = wrapper.get('button')

    expect(button.attributes('disabled')).toBeDefined()

    await wrapper.get('input').setValue(true)

    expect(button.attributes('disabled')).toBeUndefined()
  })
})
