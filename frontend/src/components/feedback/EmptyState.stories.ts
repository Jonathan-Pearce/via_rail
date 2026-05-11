import type { Meta, StoryObj } from '@storybook/vue3'
import EmptyState from './EmptyState.vue'

const meta: Meta<typeof EmptyState> = {
  title: 'Feedback/EmptyState',
  component: EmptyState,
}
export default meta

type Story = StoryObj<typeof EmptyState>

export const Default: Story = {}

export const WithAction: Story = {
  args: {
    title: 'No data found',
    body: 'Try adjusting your filters to see results.',
    onAction: () => alert('Reset clicked'),
    actionLabel: 'Reset filters',
  },
}

export const CustomMessage: Story = {
  args: {
    title: 'No corridor trains',
    body: 'No corridor-only trains had delays recorded in this period.',
    onAction: () => alert('Reset clicked'),
  },
}
