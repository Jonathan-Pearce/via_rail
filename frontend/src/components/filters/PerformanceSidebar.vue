<template>
  <nav class="sidebar-panel" aria-label="Performance filters">
    <!-- Section: Period -->
    <section class="filter-section">
      <h3 class="filter-section__title">Time range</h3>
      <div class="segment-group" role="group" aria-label="Select time period">
        <button
          v-for="opt in periodOptions"
          :key="opt.value"
          class="segment-btn"
          :class="{ 'segment-btn--active': staged.period === opt.value }"
          :aria-pressed="staged.period === opt.value"
          @click="staged.period = opt.value"
        >{{ opt.label }}</button>
      </div>
    </section>

    <!-- Section: Corridor toggle -->
    <section class="filter-section">
      <label class="toggle-row" for="corridor-toggle">
        <span class="toggle-row__text">
          <span class="toggle-row__label">Corridor only</span>
          <span class="toggle-row__hint">Windsor – Québec City</span>
        </span>
        <button
          id="corridor-toggle"
          class="toggle"
          role="switch"
          :aria-checked="staged.corridorOnly"
          :class="{ 'toggle--on': staged.corridorOnly }"
          @click="staged.corridorOnly = !staged.corridorOnly"
        >
          <span class="toggle__thumb" />
        </button>
      </label>
    </section>

    <!-- Section: Station -->
    <section class="filter-section">
      <h3 class="filter-section__title">Station</h3>
      <StationCombobox
        v-model="staged.stationCode"
        :corridor-only="staged.corridorOnly"
      />
    </section>

    <!-- Section: Train number (free text for now) -->
    <section class="filter-section">
      <h3 class="filter-section__title">Train number</h3>
      <div class="select-wrapper">
        <input
          id="train-number-input"
          v-model="trainInput"
          class="filter-input"
          type="text"
          inputmode="numeric"
          pattern="[0-9]*"
          placeholder="e.g. 60"
          aria-label="Train number"
          @blur="commitTrainNumber"
          @keyup.enter="commitTrainNumber"
        />
      </div>
    </section>

    <!-- Spacer pushes apply/reset to bottom -->
    <div class="filter-spacer" aria-hidden="true" />

    <!-- Apply / Reset -->
    <footer class="filter-actions">
      <button
        class="filter-actions__apply"
        :disabled="!isDirty"
        @click="filters.applyFilters()"
      >
        Apply filters
      </button>
      <button
        class="filter-actions__reset"
        @click="filters.resetFilters()"
      >
        Reset
      </button>
    </footer>
  </nav>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { usePerformanceFilters } from '@/stores/performanceFilters'
import StationCombobox from './StationCombobox.vue'
import type { Period } from '@/api/types'

const filters = usePerformanceFilters()
const { staged, isDirty } = storeToRefs(filters)

const periodOptions: { value: Period; label: string }[] = [
  { value: '7d',  label: '7d' },
  { value: '30d', label: '30d' },
  { value: '365d', label: '1yr' },
]

// Train number input — keep as local string, commit on blur/enter
const trainInput = ref(staged.value.trainNumber ?? '')

watch(() => staged.value.trainNumber, (v) => {
  trainInput.value = v ?? ''
})

function commitTrainNumber() {
  const v = trainInput.value.trim()
  staged.value.trainNumber = v !== '' ? v : null
}
</script>

<style scoped>
.sidebar-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: var(--sp-6) 0 0 0;
}

/* ── Sections ─────────────────────────────────────────────────────────── */
.filter-section {
  padding: 0 var(--sp-5) var(--sp-5) var(--sp-5);
  border-bottom: 1px solid var(--surface-3);
  margin-bottom: var(--sp-5);
}
.filter-section:last-of-type { border-bottom: none; }

.filter-section__title {
  font-size: var(--text-xs);
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: var(--sp-3);
  font-family: var(--font-body);
}

/* ── Period segmented control ─────────────────────────────────────────── */
.segment-group {
  display: flex;
  gap: 2px;
  background: var(--surface-0);
  padding: 3px;
  border-radius: var(--radius-md);
  border: 1px solid var(--surface-3);
}

.segment-btn {
  flex: 1;
  padding: var(--sp-2) var(--sp-1);
  border: none;
  border-radius: 5px;
  background: transparent;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: 500;
  font-family: var(--font-body);
  cursor: pointer;
  transition: background var(--dur-fast) var(--ease-out),
              color var(--dur-fast) var(--ease-out);
}
.segment-btn:hover:not(.segment-btn--active) {
  background: var(--surface-2);
  color: var(--text-primary);
}
.segment-btn--active {
  background: var(--via-yellow);
  color: var(--text-inverse);
  font-weight: 600;
  box-shadow: 0 1px 4px rgba(255, 210, 0, 0.3);
}

/* ── Toggle switch ────────────────────────────────────────────────────── */
.toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--sp-3);
  cursor: pointer;
}

.toggle-row__text { flex: 1; min-width: 0; }
.toggle-row__label {
  display: block;
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: 500;
}
.toggle-row__hint {
  display: block;
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin-top: 2px;
}

.toggle {
  position: relative;
  width: 42px;
  height: 24px;
  border-radius: var(--radius-pill);
  background: var(--surface-3);
  border: none;
  cursor: pointer;
  flex-shrink: 0;
  transition: background var(--dur-base) var(--ease-out),
              box-shadow var(--dur-base) var(--ease-out);
}
.toggle--on {
  background: var(--via-yellow);
  box-shadow: 0 0 0 1px var(--via-yellow-dim), 0 2px 8px rgba(255,210,0,0.3);
}

.toggle__thumb {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--text-primary);
  box-shadow: 0 1px 3px rgba(0,0,0,0.4);
  transition: transform var(--dur-base) var(--ease-out),
              background var(--dur-base) var(--ease-out);
}
.toggle--on .toggle__thumb {
  transform: translateX(18px);
  background: var(--text-inverse);
}

/* ── Shared input ─────────────────────────────────────────────────────── */
.filter-input {
  width: 100%;
  padding: var(--sp-2) var(--sp-3);
  background: var(--surface-0);
  border: 1px solid var(--surface-3);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-family: var(--font-body);
  transition: border-color var(--dur-fast) var(--ease-out);
}
.filter-input::placeholder { color: var(--text-muted); }
.filter-input:focus {
  outline: none;
  border-color: var(--via-yellow-dim);
  box-shadow: 0 0 0 2px var(--via-yellow-glow);
}

/* ── Spacer ───────────────────────────────────────────────────────────── */
.filter-spacer { flex: 1; }

/* ── Apply / Reset footer ─────────────────────────────────────────────── */
.filter-actions {
  display: flex;
  flex-direction: column;
  gap: var(--sp-2);
  padding: var(--sp-5);
  border-top: 1px solid var(--surface-3);
  position: sticky;
  bottom: 0;
  background: var(--surface-1);
}

.filter-actions__apply {
  width: 100%;
  padding: var(--sp-3);
  background: var(--via-yellow);
  border: none;
  border-radius: var(--radius-md);
  color: var(--text-inverse);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
  transition: opacity var(--dur-fast) var(--ease-out),
              transform var(--dur-fast) var(--ease-out),
              box-shadow var(--dur-fast) var(--ease-out);
}
.filter-actions__apply:not(:disabled):hover {
  box-shadow: 0 4px 16px rgba(255,210,0,0.35);
  transform: translateY(-1px);
}
.filter-actions__apply:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.filter-actions__reset {
  width: 100%;
  padding: var(--sp-2) var(--sp-3);
  background: transparent;
  border: 1px solid var(--surface-3);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: color var(--dur-fast) var(--ease-out),
              border-color var(--dur-fast) var(--ease-out),
              background var(--dur-fast) var(--ease-out);
}
.filter-actions__reset:hover {
  color: var(--text-primary);
  border-color: var(--surface-4);
  background: var(--surface-2);
}
</style>
