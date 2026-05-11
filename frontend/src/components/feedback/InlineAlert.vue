<template>
  <div class="alert" :class="`alert--${variant}`" role="alert" aria-live="polite">
    <component :is="icon" class="alert__icon" aria-hidden="true" />
    <div class="alert__body">
      <p class="alert__message">{{ message }}</p>
      <button v-if="onRetry" class="alert__retry" @click="onRetry">
        Try again
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import IconAlert from '@/components/icons/IconAlert.vue'

const props = withDefaults(defineProps<{
  message:  string
  variant?: 'error' | 'warn' | 'info'
  onRetry?: (() => void) | null
}>(), {
  variant: 'error',
  onRetry: null,
})

const icon = computed(() => IconAlert)
</script>

<style scoped>
.alert {
  display: flex;
  align-items: flex-start;
  gap: var(--sp-3);
  padding: var(--sp-4) var(--sp-5);
  border-radius: var(--radius-md);
  border: 1px solid;
  font-size: var(--text-sm);
  animation: fade-up var(--dur-base) var(--ease-out) both;
}

.alert--error {
  background: var(--status-bad-bg);
  border-color: var(--status-bad);
  color: #fca5a5;
}
.alert--warn {
  background: var(--via-yellow-glow);
  border-color: var(--via-yellow-dim);
  color: var(--via-yellow);
}
.alert--info {
  background: rgba(99, 179, 237, 0.1);
  border-color: #4299e1;
  color: #63b3ed;
}

.alert__icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  margin-top: 1px;
}
.alert__body { flex: 1; min-width: 0; }
.alert__message { line-height: 1.5; }

.alert__retry {
  margin-top: var(--sp-2);
  padding: var(--sp-1) var(--sp-3);
  background: transparent;
  border: 1px solid currentColor;
  border-radius: var(--radius-sm);
  color: inherit;
  font-size: var(--text-xs);
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
  transition: background var(--dur-fast) var(--ease-out);
}
.alert__retry:hover { background: rgba(255,255,255,0.08); }
</style>
