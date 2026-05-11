<template>
  <div class="chart-card">
    <header class="chart-card__header">
      <div>
        <h2 class="chart-card__title">Average Delay</h2>
        <p class="chart-card__sub">Mean delay in minutes per day</p>
      </div>
    </header>

    <div v-if="loading" class="chart-card__skeleton skeleton" />
    <VChart
      v-else
      class="chart-card__chart"
      :option="option"
      autoresize
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { TooltipComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { DailyPerformance } from '@/api/types'

use([BarChart, TooltipComponent, GridComponent, CanvasRenderer])

const props = withDefaults(defineProps<{
  data:     DailyPerformance[]
  loading?: boolean
}>(), {
  loading: false,
})

const option = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#0f1923',
    borderColor: '#1f2d3f',
    textStyle: { color: '#f0eeea', fontFamily: 'DM Sans' },
    formatter: (params: any[]) => {
      const p = params[0]
      return `
        <div style="font-size:11px;color:#8fa3b8;margin-bottom:4px">${p.axisValue}</div>
        <div style="font-size:22px;font-family:'Bebas Neue';color:#FFD200">${p.value} min</div>
      `
    },
  },
  grid: { left: 40, right: 16, top: 12, bottom: 36, containLabel: false },
  xAxis: {
    type: 'category',
    data: props.data.map(d => d.date),
    axisLine:  { lineStyle: { color: '#1f2d3f' } },
    axisTick:  { show: false },
    axisLabel: {
      color: '#4d6478',
      fontSize: 11,
      fontFamily: 'DM Mono',
      rotate: props.data.length > 30 ? 30 : 0,
      formatter: (v: string) => v.slice(5),
    },
  },
  yAxis: {
    type: 'value',
    minInterval: 1,
    splitLine: { lineStyle: { color: '#1f2d3f', type: 'dashed' } },
    axisLabel: {
      color: '#4d6478',
      fontSize: 11,
      fontFamily: 'DM Mono',
      formatter: (v: number) => `${v}m`,
    },
  },
  series: [{
    type: 'bar',
    name: 'Avg delay (min)',
    data: props.data.map(d => Number(d.avg_delay_minutes.toFixed(1))),
    barMaxWidth: 32,
    itemStyle: {
      color: {
        type: 'linear',
        x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0,   color: '#FFD200' },
          { offset: 1,   color: 'rgba(255,210,0,0.4)' },
        ],
      },
      borderRadius: [4, 4, 0, 0],
    },
    emphasis: {
      itemStyle: { color: '#FFD200' },
    },
    animationDuration: 1000,
    animationEasing: 'cubicOut',
  }],
}))
</script>

<style scoped>
.chart-card {
  background: var(--surface-1);
  border: 1px solid var(--surface-3);
  border-radius: var(--radius-lg);
  padding: var(--sp-5) var(--sp-5) var(--sp-4);
  box-shadow: var(--shadow-sm);
}
.chart-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: var(--sp-4);
}
.chart-card__title {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  color: var(--text-primary);
  letter-spacing: 0.04em;
}
.chart-card__sub {
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin-top: var(--sp-1);
}
.chart-card__chart {
  width: 100%;
  height: 240px;
}
.chart-card__skeleton {
  width: 100%;
  height: 240px;
}
</style>
