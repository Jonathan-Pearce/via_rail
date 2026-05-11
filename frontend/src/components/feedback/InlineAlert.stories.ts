import type { Meta, StoryObj } from '@storybook/vue3'
import InlineAlert from './InlineAlert.vue'

const meta: Meta<typeof InlineAlert> = {
  title: 'Feedback/InlineAlert',
  component: InlineAlert,
  argTypes: {
    variant: { control: 'select', options: ['error', 'warn', 'info'] },
  },
}
export default meta

type Story = StoryObj<typeof InlineAlert>

export const Error: Story = {
  args: {
    message: 'Failed to load performance data. The backend may be unreachable.',
    variant: 'error',
  },
}

export const ErrorWithRetry: Story = {
  args: {
    message: 'Failed to load performance data.',
    variant: 'error',
    onRetry: () => alert('Retry clicked'),
  },
}

export const Warning: Story = {
  args: {
    message: 'Data may be incomplete. The last scrape was over 24 hours ago.',
    variant: 'warn',
  },
}

export const Info: Story = {
  args: {
    message: 'Showing historical data. Live tracking is not yet enabled.',
    variant: 'info',
  },
}
