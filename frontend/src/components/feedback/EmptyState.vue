<template>
  <div class="empty-state" role="status" aria-live="polite">
    <!-- Stylised SVG: idle train on a track -->
    <svg class="empty-state__graphic" viewBox="0 0 160 100" fill="none" aria-hidden="true">
      <!-- Track -->
      <line x1="10" y1="82" x2="150" y2="82" stroke="#1f2d3f" stroke-width="3" stroke-linecap="round"/>
      <line x1="10" y1="88" x2="150" y2="88" stroke="#1f2d3f" stroke-width="3" stroke-linecap="round"/>
      <!-- Sleepers -->
      <line v-for="x in [20,40,60,80,100,120,140]" :key="x" :x1="x" y1="78" :x2="x" y2="92" stroke="#1f2d3f" stroke-width="2"/>
      <!-- Train body -->
      <rect x="40" y="54" width="80" height="28" rx="6" fill="#172030"/>
      <rect x="48" y="44" width="56" height="14" rx="4" fill="#172030"/>
      <!-- Windows -->
      <rect x="56" y="48" width="12" height="8" rx="2" fill="#FFD200" opacity=".3"/>
      <rect x="74" y="48" width="12" height="8" rx="2" fill="#FFD200" opacity=".3"/>
      <rect x="92" y="48" width="10" height="8" rx="2" fill="#FFD200" opacity=".3"/>
      <!-- Wheel sets -->
      <circle cx="60" cy="82" r="8" fill="#0f1923" stroke="#1f2d3f" stroke-width="2"/>
      <circle cx="100" cy="82" r="8" fill="#0f1923" stroke="#1f2d3f" stroke-width="2"/>
      <!-- Yellow stripe -->
      <rect x="40" y="62" width="80" height="3" rx="1" fill="#FFD200" opacity=".6"/>
    </svg>

    <p class="empty-state__title">{{ title }}</p>
    <p v-if="body" class="empty-state__body">{{ body }}</p>
    <button v-if="onAction" class="empty-state__action" @click="onAction">
      {{ actionLabel ?? 'Reset filters' }}
    </button>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  title?:       string
  body?:        string
  onAction?:    (() => void) | null
  actionLabel?: string | null
}>(), {
  title:       'No data found',
  body:        'Try adjusting your filters to see results.',
  onAction:    null,
  actionLabel: null,
})
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--sp-16) var(--sp-8);
  text-align: center;
  animation: fade-up var(--dur-slow) var(--ease-out) both;
}

.empty-state__graphic {
  width: 160px;
  height: 100px;
  margin-bottom: var(--sp-6);
  opacity: 0.7;
}

.empty-state__title {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  letter-spacing: 0.04em;
  color: var(--text-secondary);
  margin-bottom: var(--sp-2);
}

.empty-state__body {
  font-size: var(--text-sm);
  color: var(--text-muted);
  max-width: 320px;
}

.empty-state__action {
  margin-top: var(--sp-6);
  padding: var(--sp-2) var(--sp-6);
  background: var(--via-yellow-glow);
  border: 1px solid var(--via-yellow-dim);
  border-radius: var(--radius-pill);
  color: var(--via-yellow);
  font-size: var(--text-sm);
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
  transition: background var(--dur-fast) var(--ease-out),
              transform var(--dur-fast) var(--ease-out);
}
.empty-state__action:hover {
  background: rgba(255, 210, 0, 0.22);
  transform: translateY(-1px);
}
</style>
