<template>
  <div class="chart-card">
    <header class="chart-card__header">
      <h2 class="chart-card__title">On-Time Performance</h2>
      <p class="chart-card__sub">% of stops arriving within 5 minutes of schedule</p>
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
import { LineChart } from 'echarts/charts'
import { TooltipComponent, GridComponent, LegendComponent, MarkLineComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { DailyPerformance } from '@/api/types'

use([LineChart, TooltipComponent, GridComponent, LegendComponent, MarkLineComponent, CanvasRenderer])

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
      const dp = props.data[p.dataIndex]
      return `
        <div style="font-size:11px;color:#8fa3b8;margin-bottom:4px">${p.axisValue}</div>
        <div style="font-size:22px;font-family:'Bebas Neue';color:#FFD200">${p.value}%</div>
        <div style="font-size:11px;color:#8fa3b8">${dp?.total_stops ?? 0} stops sampled</div>
      `
    },
  },
  grid: { left: 40, right: 24, top: 12, bottom: 36, containLabel: false },
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
      formatter: (v: string) => v.slice(5), // MM-DD
    },
  },
  yAxis: {
    type: 'value',
    min: 0,
    max: 100,
    splitLine: { lineStyle: { color: '#1f2d3f', type: 'dashed' } },
    axisLabel: {
      color: '#4d6478',
      fontSize: 11,
      fontFamily: 'DM Mono',
      formatter: (v: number) => `${v}%`,
    },
  },
  series: [{
    type: 'line',
    name: 'On-time %',
    data: props.data.map(d => Number(d.on_time_pct.toFixed(1))),
    smooth: 0.3,
    symbol: 'none',
    lineStyle: { color: '#FFD200', width: 2.5 },
    areaStyle: {
      color: {
        type: 'linear',
        x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0,   color: 'rgba(255,210,0,0.28)' },
          { offset: 0.8, color: 'rgba(255,210,0,0.02)' },
        ],
      },
    },
    markLine: {
      silent: true,
      symbol: 'none',
      lineStyle: { color: 'rgba(0,200,150,0.35)', type: 'dashed' },
      data: [{ yAxis: 80, label: { formatter: '80%', color: '#00c896', fontSize: 11 } }],
    },
    animationDuration: 1200,
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
.chart-card__header { margin-bottom: var(--sp-4); }

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
  height: 260px;
}
.chart-card__skeleton {
  width: 100%;
  height: 260px;
}
</style>
