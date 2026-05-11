import type { Preview } from '@storybook/vue3'
import '../src/styles/global.css'

const preview: Preview = {
  parameters: {
    backgrounds: {
      default: 'dark',
      values: [
        { name: 'dark', value: '#090e15' },
        { name: 'surface', value: '#0f1923' },
      ],
    },
  },
}

export default preview
