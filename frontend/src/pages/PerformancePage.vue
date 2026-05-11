<template>
  <div class="perf-page">
    <!-- ── Page header ───────────────────────────────────────────────── -->
    <header class="perf-page__header animate-fade-up" style="animation-delay:0ms">
      <div>
        <h1 class="perf-page__title">Performance</h1>
        <p class="perf-page__period-label">
          Showing <strong>{{ periodLabel }}</strong>
          <template v-if="appliedFilters.corridorOnly">
            · <span class="tag">Corridor only</span>
          </template>
          <template v-if="appliedFilters.stationCode">
            · <span class="tag">{{ appliedFilters.stationCode }}</span>
          </template>
          <template v-if="appliedFilters.trainNumber">
            · <span class="tag">Train {{ appliedFilters.trainNumber }}</span>
          </template>
        </p>
      </div>
      <div class="perf-page__meta" v-if="summaryData">
        <span class="perf-page__stops">{{ summaryData.total_stops.toLocaleString() }} stops sampled</span>
      </div>
    </header>

    <!-- ── Error state ────────────────────────────────────────────────── -->
    <InlineAlert
      v-if="summaryError || performanceError"
      :message="(summaryError || performanceError)?.message ?? 'Failed to load data.'"
      variant="error"
      :on-retry="() => { refetchSummary(); refetchPerformance() }"
      class="animate-fade-up"
      style="animation-delay:80ms;margin-bottom:var(--sp-6)"
    />

    <!-- ── KPI cards ──────────────────────────────────────────────────── -->
    <section class="stat-grid" aria-label="Key metrics">
      <StatCard
        label="On-Time Rate"
        :raw-value="summaryData?.on_time_pct ?? null"
        suffix="%"
        accent="yellow"
        :loading="summaryLoading"
        :sub="summaryData ? `Target: 80%` : undefined"
        class="animate-fade-up"
        style="animation-delay:60ms"
      />
      <StatCard
        label="Avg Delay"
        :raw-value="summaryData?.avg_delay_minutes ?? null"
        suffix=" min"
        accent="default"
        :loading="summaryLoading"
        :decimals="1"
        class="animate-fade-up"
        style="animation-delay:100ms"
      />
      <StatCard
        label="Late 15+ min"
        :raw-value="summaryData?.late_15_pct ?? null"
        suffix="%"
        :accent="(summaryData?.late_15_pct ?? 0) >= 20 ? 'bad' : 'med'"
        :loading="summaryLoading"
        class="animate-fade-up"
        style="animation-delay:140ms"
      />
      <StatCard
        label="Late 60+ min"
        :raw-value="summaryData?.late_60_pct ?? null"
        suffix="%"
        :accent="(summaryData?.late_60_pct ?? 0) >= 5 ? 'bad' : 'default'"
        :loading="summaryLoading"
        class="animate-fade-up"
        style="animation-delay:180ms"
      />
    </section>

    <!-- ── Empty state ────────────────────────────────────────────────── -->
    <EmptyState
      v-if="!performanceLoading && !performanceError && performanceData?.length === 0"
      class="animate-fade-up"
      style="animation-delay:200ms"
      :on-action="() => filters.resetFilters()"
    />

    <!-- ── Charts ─────────────────────────────────────────────────────── -->
    <template v-else>
      <div class="chart-grid animate-fade-up" style="animation-delay:220ms">
        <OnTimeTrendChart
          :data="performanceData ?? []"
          :loading="performanceLoading"
        />
      </div>

      <div class="chart-grid chart-grid--two animate-fade-up" style="animation-delay:300ms">
        <AverageDelayChart
          :data="performanceData ?? []"
          :loading="performanceLoading"
        />
        <DelayDistributionChart
          :data="performanceData ?? []"
          :loading="performanceLoading"
        />
      </div>
    </template>

    <!-- ── UTC footnote ───────────────────────────────────────────────── -->
    <p class="perf-page__footnote animate-fade-up" style="animation-delay:380ms">
      All dates reflect the EST calendar day of the scrape. Timestamps stored internally as UTC.
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { usePerformanceFilters } from '@/stores/performanceFilters'
import { usePerformanceQuery, useSummaryQuery } from '@/composables/usePerformanceQuery'
import StatCard from '@/components/stats/StatCard.vue'
import InlineAlert from '@/components/feedback/InlineAlert.vue'
import EmptyState from '@/components/feedback/EmptyState.vue'
import OnTimeTrendChart from '@/components/charts/OnTimeTrendChart.vue'
import AverageDelayChart from '@/components/charts/AverageDelayChart.vue'
import DelayDistributionChart from '@/components/charts/DelayDistributionChart.vue'

const filters = usePerformanceFilters()
const { applied: appliedFilters } = storeToRefs(filters)

const {
  data: summaryData,
  isLoading: summaryLoading,
  error: summaryError,
  refetch: refetchSummary,
} = useSummaryQuery(appliedFilters)

const {
  data: performanceData,
  isLoading: performanceLoading,
  error: performanceError,
  refetch: refetchPerformance,
} = usePerformanceQuery(appliedFilters)

const periodLabel = computed(() => {
  const p = appliedFilters.value.period
  return p === '7d' ? 'Last 7 days' : p === '30d' ? 'Last 30 days' : 'Last 12 months'
})
</script>

<style scoped>
.perf-page {
  max-width: 900px;
}

/* ── Header ──────────────────────────────────────────────────────────── */
.perf-page__header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--sp-4);
  margin-bottom: var(--sp-8);
  flex-wrap: wrap;
}

.perf-page__title {
  font-family: var(--font-display);
  font-size: var(--text-4xl);
  color: var(--text-primary);
  letter-spacing: 0.04em;
  line-height: 1;
}

.perf-page__period-label {
  margin-top: var(--sp-2);
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.tag {
  display: inline-block;
  padding: 0 var(--sp-2);
  background: var(--via-yellow-glow);
  border: 1px solid var(--via-yellow-dim);
  border-radius: var(--radius-pill);
  color: var(--via-yellow);
  font-size: var(--text-xs);
  font-weight: 600;
  letter-spacing: 0.04em;
  vertical-align: middle;
}

.perf-page__meta {
  text-align: right;
  flex-shrink: 0;
}
.perf-page__stops {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--text-muted);
}

/* ── KPI grid ────────────────────────────────────────────────────────── */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--sp-4);
  margin-bottom: var(--sp-6);
}

/* ── Chart grids ─────────────────────────────────────────────────────── */
.chart-grid {
  margin-bottom: var(--sp-6);
}
.chart-grid--two {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--sp-4);
}

/* ── Footnote ────────────────────────────────────────────────────────── */
.perf-page__footnote {
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin-top: var(--sp-8);
  padding-top: var(--sp-4);
  border-top: 1px solid var(--surface-3);
}

/* ── Responsive ──────────────────────────────────────────────────────── */
@media (max-width: 900px) {
  .stat-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 700px) {
  .chart-grid--two { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
  .stat-grid { grid-template-columns: 1fr 1fr; }
}
</style>
