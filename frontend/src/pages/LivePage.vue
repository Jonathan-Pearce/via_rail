<template>
  <div class="live-placeholder animate-fade-up">
    <svg viewBox="0 0 80 80" class="live-placeholder__icon" aria-hidden="true">
      <!-- Simple animated radar pulse -->
      <circle cx="40" cy="40" r="8" fill="#FFD200"/>
      <circle cx="40" cy="40" r="16" fill="none" stroke="#FFD200" stroke-width="1.5" opacity="0.5"/>
      <circle cx="40" cy="40" r="28" fill="none" stroke="#FFD200" stroke-width="1" opacity="0.25"/>
    </svg>
    <h2 class="live-placeholder__title">Live Map</h2>
    <p class="live-placeholder__body">Real-time train tracking is coming soon.</p>
  </div>
</template>

<style scoped>
.live-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: var(--sp-4);
  text-align: center;
}
.live-placeholder__icon {
  width: 80px;
  height: 80px;
  opacity: 0.6;
  animation: pulse-yellow 2.4s ease-in-out infinite;
}
.live-placeholder__title {
  font-family: var(--font-display);
  font-size: var(--text-3xl);
  color: var(--text-secondary);
  letter-spacing: 0.05em;
}
.live-placeholder__body {
  font-size: var(--text-sm);
  color: var(--text-muted);
}
</style>
