<template>
  <div class="shell rail-bg">
    <!-- ── Top navigation bar ────────────────────────────────────────── -->
    <header class="topnav" role="banner">
      <div class="topnav__inner">
        <!-- Logo -->
        <a class="topnav__logo" href="/" aria-label="Via Rail Performance Dashboard">
          <svg class="topnav__logo-mark" viewBox="0 0 32 32" fill="none" aria-hidden="true">
            <!-- Stylised train silhouette -->
            <rect x="2" y="18" width="28" height="6" rx="3" fill="#FFD200"/>
            <rect x="6" y="12" width="18" height="7" rx="2" fill="#FFD200" opacity=".8"/>
            <rect x="9" y="8" width="12" height="5" rx="2" fill="#FFD200" opacity=".5"/>
            <circle cx="8"  cy="25" r="2.5" fill="#090e15" stroke="#FFD200" stroke-width="1.2"/>
            <circle cx="24" cy="25" r="2.5" fill="#090e15" stroke="#FFD200" stroke-width="1.2"/>
          </svg>
          <span class="topnav__wordmark">VIA RAIL</span>
          <span class="topnav__separator" aria-hidden="true">|</span>
          <span class="topnav__subtitle">PERFORMANCE</span>
        </a>

        <!-- Tab navigation -->
        <nav class="topnav__tabs" aria-label="Main navigation">
          <RouterLink
            v-for="tab in tabs"
            :key="tab.to"
            :to="tab.to"
            class="topnav__tab"
            :class="{ 'topnav__tab--active': isActive(tab.to) }"
            :aria-current="isActive(tab.to) ? 'page' : undefined"
          >
            <component :is="tab.icon" class="topnav__tab-icon" aria-hidden="true" />
            <span>{{ tab.label }}</span>
          </RouterLink>
        </nav>

        <!-- Mobile sidebar toggle -->
        <button
          class="topnav__menu-toggle"
          :aria-label="sidebarOpen ? 'Close filters' : 'Open filters'"
          :aria-expanded="sidebarOpen"
          aria-controls="sidebar"
          @click="toggleSidebar"
        >
          <IconFilter />
        </button>
      </div>
    </header>

    <!-- ── Main layout ───────────────────────────────────────────────── -->
    <div class="layout">
      <!-- Sidebar (desktop pinned / mobile overlay) -->
      <aside
        id="sidebar"
        class="sidebar"
        :class="{ 'sidebar--open': sidebarOpen }"
        aria-label="Filters"
        v-show="showSidebar"
      >
        <PerformanceSidebar v-if="route.path.startsWith('/performance')" />
      </aside>

      <!-- Mobile overlay backdrop -->
      <Transition name="backdrop">
        <div
          v-if="sidebarOpen && isMobile"
          class="sidebar-backdrop"
          aria-hidden="true"
          @click="sidebarOpen = false"
        />
      </Transition>

      <!-- Page content -->
      <main class="content" id="main-content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { RouterView, RouterLink } from 'vue-router'
import IconFilter from '@/components/icons/IconFilter.vue'
import IconBarChart from '@/components/icons/IconBarChart.vue'
import IconMap from '@/components/icons/IconMap.vue'
import PerformanceSidebar from '@/components/filters/PerformanceSidebar.vue'

const route = useRoute()

const tabs = [
  { to: '/performance', label: 'Performance', icon: IconBarChart },
  { to: '/live',        label: 'Live Map',    icon: IconMap },
]

function isActive(path: string) {
  return route.path.startsWith(path)
}

const sidebarOpen = ref(false)
const isMobile = ref(false)
const showSidebar = computed(() => route.path.startsWith('/performance'))

function checkMobile() {
  isMobile.value = window.innerWidth < 1024
  if (!isMobile.value) sidebarOpen.value = false
}

function toggleSidebar() {
  sidebarOpen.value = !sidebarOpen.value
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
/* ── Shell wrapper ───────────────────────────────────────────────────── */
.shell {
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
}

/* ── Top nav ─────────────────────────────────────────────────────────── */
.topnav {
  position: sticky;
  top: 0;
  z-index: 100;
  height: var(--topnav-height);
  background: rgba(9, 14, 21, 0.92);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--surface-3);
  box-shadow: 0 1px 0 rgba(255,210,0,0.06);
}

.topnav__inner {
  display: flex;
  align-items: center;
  gap: var(--sp-6);
  height: 100%;
  max-width: var(--content-max);
  margin: 0 auto;
  padding: 0 var(--sp-6);
}

/* Logo */
.topnav__logo {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  color: var(--text-primary);
  text-decoration: none;
  flex-shrink: 0;
}
.topnav__logo-mark {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
}
.topnav__wordmark {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  letter-spacing: 0.08em;
  color: var(--via-yellow);
}
.topnav__separator {
  color: var(--surface-4);
  font-size: var(--text-sm);
}
.topnav__subtitle {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-secondary);
}

/* Tab nav */
.topnav__tabs {
  display: flex;
  align-items: center;
  gap: var(--sp-1);
  margin-left: auto;
}

.topnav__tab {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  padding: var(--sp-2) var(--sp-4);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: 500;
  letter-spacing: 0.04em;
  text-decoration: none;
  transition: color var(--dur-fast) var(--ease-out),
              background var(--dur-fast) var(--ease-out);
}
.topnav__tab:hover {
  color: var(--text-primary);
  background: var(--surface-2);
}
.topnav__tab--active {
  color: var(--via-yellow);
  background: var(--via-yellow-glow);
}
.topnav__tab-icon {
  width: 16px;
  height: 16px;
  opacity: 0.8;
}

/* Mobile menu toggle */
.topnav__menu-toggle {
  display: none;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: var(--radius-md);
  background: var(--surface-2);
  color: var(--text-secondary);
  cursor: pointer;
  transition: background var(--dur-fast) var(--ease-out),
              color var(--dur-fast) var(--ease-out);
  margin-left: var(--sp-3);
}
.topnav__menu-toggle:hover {
  background: var(--surface-3);
  color: var(--text-primary);
}

/* ── Layout ──────────────────────────────────────────────────────────── */
.layout {
  display: flex;
  flex: 1;
  max-width: var(--content-max);
  width: 100%;
  margin: 0 auto;
}

/* ── Sidebar ─────────────────────────────────────────────────────────── */
.sidebar {
  position: relative;
  width: var(--sidebar-width);
  flex-shrink: 0;
  background: var(--surface-1);
  border-right: 1px solid var(--surface-3);
  overflow-y: auto;
  /* sticky over the page, content scrolls beside it */
  position: sticky;
  top: var(--topnav-height);
  height: calc(100dvh - var(--topnav-height));
}

/* ── Content ─────────────────────────────────────────────────────────── */
.content {
  flex: 1;
  min-width: 0;
  padding: var(--sp-8) var(--sp-8);
  overflow-x: hidden;
}

/* ── Backdrop transition ─────────────────────────────────────────────── */
.backdrop-enter-active,
.backdrop-leave-active {
  transition: opacity var(--dur-base) var(--ease-out);
}
.backdrop-enter-from,
.backdrop-leave-to { opacity: 0; }

/* ── Responsive ──────────────────────────────────────────────────────── */
@media (max-width: 1023px) {
  .topnav__menu-toggle { display: flex; }
  .topnav__tabs { gap: 0; }
  .topnav__tab span { display: none; }

  .sidebar {
    position: fixed;
    top: var(--topnav-height);
    left: 0;
    height: calc(100dvh - var(--topnav-height));
    z-index: 90;
    transform: translateX(-100%);
    transition: transform var(--dur-slow) var(--ease-out);
  }
  .sidebar--open {
    transform: translateX(0);
  }
  .sidebar-backdrop {
    position: fixed;
    inset: var(--topnav-height) 0 0 0;
    background: rgba(9, 14, 21, 0.7);
    z-index: 80;
    backdrop-filter: blur(4px);
  }
  .content {
    padding: var(--sp-6) var(--sp-4);
  }
}

@media (max-width: 600px) {
  .topnav__subtitle { display: none; }
  .topnav__separator { display: none; }
}
</style>
