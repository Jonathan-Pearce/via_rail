import type { Meta, StoryObj } from '@storybook/vue3'
import StatCard from './StatCard.vue'

const meta: Meta<typeof StatCard> = {
  title: 'Stats/StatCard',
  component: StatCard,
  argTypes: {
    accent: {
      control: 'select',
      options: ['default', 'yellow', 'good', 'med', 'bad'],
    },
  },
}
export default meta

type Story = StoryObj<typeof StatCard>

export const OnTime: Story = {
  args: {
    label: 'On-Time Rate',
    rawValue: 72.4,
    suffix: '%',
    accent: 'yellow',
    sub: 'Target: 80%',
  },
}

export const AverageDelay: Story = {
  args: {
    label: 'Avg Delay',
    rawValue: 11.3,
    suffix: ' min',
    accent: 'default',
    decimals: 1,
  },
}

export const Late15: Story = {
  args: {
    label: 'Late 15+ min',
    rawValue: 23.1,
    suffix: '%',
    accent: 'med',
  },
}

export const Late60: Story = {
  args: {
    label: 'Late 60+ min',
    rawValue: 6.8,
    suffix: '%',
    accent: 'bad',
  },
}

export const Loading: Story = {
  args: {
    label: 'On-Time Rate',
    loading: true,
  },
}

export const NoData: Story = {
  args: {
    label: 'On-Time Rate',
    rawValue: null,
    suffix: '%',
    accent: 'yellow',
  },
}
