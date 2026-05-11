<template>
  <article class="stat-card" :class="`stat-card--${accent}`" role="region" :aria-label="label">
    <!-- Loading skeleton -->
    <template v-if="loading">
      <div class="stat-card__skeleton-label skeleton" />
      <div class="stat-card__skeleton-value skeleton" />
      <div class="stat-card__skeleton-sub skeleton" />
    </template>

    <template v-else>
      <p class="stat-card__label">{{ label }}</p>
      <p class="stat-card__value" :title="rawValue !== undefined ? String(rawValue) : undefined">
        <span v-if="prefix" class="stat-card__prefix">{{ prefix }}</span>
        {{ displayValue }}
        <span v-if="suffix" class="stat-card__suffix">{{ suffix }}</span>
      </p>
      <p v-if="sub" class="stat-card__sub">{{ sub }}</p>
    </template>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type Accent = 'default' | 'good' | 'med' | 'bad' | 'yellow'

const props = withDefaults(defineProps<{
  label:      string
  rawValue?:  number | null
  displayValue?: string
  prefix?:    string
  suffix?:    string
  sub?:       string
  loading?:   boolean
  accent?:    Accent
  decimals?:  number
}>(), {
  accent:   'default',
  decimals: 1,
  loading:  false,
})

const displayValue = computed(() => {
  if (props.displayValue !== undefined) return props.displayValue
  if (props.rawValue === null || props.rawValue === undefined) return '—'
  return props.rawValue.toFixed(props.decimals)
})
</script>

<style scoped>
.stat-card {
  position: relative;
  background: var(--surface-1);
  border: 1px solid var(--surface-3);
  border-radius: var(--radius-lg);
  padding: var(--sp-5) var(--sp-6);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: transform var(--dur-base) var(--ease-out),
              box-shadow var(--dur-base) var(--ease-out);
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* Left accent stripe */
.stat-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--accent-color, var(--surface-4));
  border-radius: var(--radius-sm) 0 0 var(--radius-sm);
}
.stat-card--yellow { --accent-color: var(--via-yellow); }
.stat-card--good   { --accent-color: var(--status-good); }
.stat-card--med    { --accent-color: var(--status-med); }
.stat-card--bad    { --accent-color: var(--status-bad); }

.stat-card__label {
  font-size: var(--text-xs);
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-secondary);
  margin-bottom: var(--sp-2);
}

.stat-card__value {
  font-family: var(--font-display);
  font-size: var(--text-4xl);
  color: var(--text-primary);
  line-height: 1;
  letter-spacing: 0.02em;
  margin-bottom: var(--sp-1);
}

.stat-card__prefix,
.stat-card__suffix {
  font-family: var(--font-body);
  font-size: var(--text-lg);
  font-weight: 500;
  color: var(--text-secondary);
  vertical-align: super;
}
.stat-card__prefix { margin-right: 2px; }
.stat-card__suffix { margin-left: 2px; font-size: var(--text-xl); vertical-align: baseline; }

.stat-card__sub {
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin-top: var(--sp-2);
}

/* Skeletons */
.stat-card__skeleton-label {
  height: 10px;
  width: 80px;
  margin-bottom: var(--sp-3);
}
.stat-card__skeleton-value {
  height: 44px;
  width: 120px;
  margin-bottom: var(--sp-2);
}
.stat-card__skeleton-sub {
  height: 10px;
  width: 100px;
}
</style>
