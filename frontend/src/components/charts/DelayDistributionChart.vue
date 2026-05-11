<template>
  <div class="chart-card">
    <header class="chart-card__header">
      <h2 class="chart-card__title">Delay Distribution</h2>
      <p class="chart-card__sub">Share of stops in each delay band</p>
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
import { TooltipComponent, GridComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { DailyPerformance } from '@/api/types'

use([BarChart, TooltipComponent, GridComponent, LegendComponent, CanvasRenderer])

const props = withDefaults(defineProps<{
  data:     DailyPerformance[]
  loading?: boolean
}>(), {
  loading: false,
})

/**
 * Derive distribution totals from the daily data.
 * on_time_pct, late_15_pct, late_60_pct are daily averages (0–100).
 * "medium" bucket = not on time and not late_15 → late_15_pct - late_60_pct
 */
const distribution = computed(() => {
  if (!props.data.length) return null

  const avg = (key: keyof Pick<DailyPerformance, 'on_time_pct' | 'late_15_pct' | 'late_60_pct'>) =>
    props.data.reduce((s, d) => s + d[key], 0) / props.data.length

  const onTime  = avg('on_time_pct')
  const late15  = avg('late_15_pct')
  const late60  = avg('late_60_pct')
  const medLate = Math.max(0, late15 - late60)
  /* 1–15 min bucket: the gap between on_time and late_15 */
  const slight  = Math.max(0, 100 - onTime - medLate - late60)

  return [
    { label: 'On time\n(≤5 min)',    value: Number(onTime.toFixed(1)),  color: '#00c896' },
    { label: 'Slight\n(1–15 min)',   value: Number(slight.toFixed(1)),  color: '#f59e0b' },
    { label: 'Moderate\n(15–60m)',   value: Number(medLate.toFixed(1)), color: '#f97316' },
    { label: 'Major\n(60+ min)',     value: Number(late60.toFixed(1)),  color: '#ef4444' },
  ]
})

const option = computed(() => {
  const dist = distribution.value
  if (!dist) return {}
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#0f1923',
      borderColor: '#1f2d3f',
      textStyle: { color: '#f0eeea', fontFamily: 'DM Sans' },
      formatter: (p: any) =>
        `<div style="font-size:11px;color:#8fa3b8">${p.name.replace('\n', ' ')}</div>
         <div style="font-size:22px;font-family:'Bebas Neue';color:${p.color}">${p.value}%</div>`,
    },
    grid: { left: 8, right: 8, top: 20, bottom: 56, containLabel: true },
    xAxis: {
      type: 'category',
      data: dist.map(d => d.label),
      axisLine:  { lineStyle: { color: '#1f2d3f' } },
      axisTick:  { show: false },
      axisLabel: {
        color: '#8fa3b8',
        fontSize: 11,
        fontFamily: 'DM Sans',
        lineHeight: 16,
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
      type: 'bar',
      data: dist.map(d => ({
        value: d.value,
        itemStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: d.color },
              { offset: 1, color: d.color + '66' },
            ],
          },
          borderRadius: [6, 6, 0, 0],
        },
        label: {
          show: true,
          position: 'top',
          color: d.color,
          fontFamily: 'DM Mono',
          fontSize: 12,
          formatter: `${d.value}%`,
        },
      })),
      barMaxWidth: 60,
      animationDuration: 900,
      animationEasing: 'cubicOut',
    }],
  }
})
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
