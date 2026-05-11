<template>
  <div class="combobox" ref="containerRef">
    <div class="combobox__input-wrap">
      <input
        ref="inputRef"
        v-model="query"
        class="combobox__input"
        type="text"
        :placeholder="placeholder"
        role="combobox"
        :aria-expanded="isOpen && filteredStations.length > 0"
        aria-autocomplete="list"
        :aria-activedescendant="hovered !== null ? `combobox-opt-${hovered}` : undefined"
        aria-controls="combobox-listbox"
        @focus="open"
        @input="open"
        @keydown.down.prevent="moveDown"
        @keydown.up.prevent="moveUp"
        @keydown.enter.prevent="selectHighlighted"
        @keydown.escape="close"
        @keydown.backspace="onBackspace"
      />
      <button
        v-if="modelValue"
        class="combobox__clear"
        aria-label="Clear station"
        @click="clear"
      >×</button>
    </div>

    <Transition name="combobox-list">
      <ul
        v-if="isOpen && filteredStations.length > 0"
        id="combobox-listbox"
        ref="listRef"
        class="combobox__list"
        role="listbox"
        :aria-label="placeholder"
      >
        <li
          v-for="(station, i) in filteredStations"
          :id="`combobox-opt-${i}`"
          :key="station.station_code"
          class="combobox__option"
          :class="{ 'combobox__option--highlighted': hovered === i }"
          role="option"
          :aria-selected="modelValue === station.station_code"
          @mouseenter="hovered = i"
          @mousedown.prevent="selectOption(station)"
        >
          <span class="combobox__option-code">{{ station.station_code }}</span>
          <span class="combobox__option-name">{{ station.station_name }}</span>
          <span
            v-if="modelValue === station.station_code"
            class="combobox__option-check"
            aria-hidden="true"
          >✓</span>
        </li>
      </ul>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import Fuse from 'fuse.js'
import { useStationsQuery } from '@/composables/useStationsQuery'
import type { StationRecord } from '@/api/types'

const props = withDefaults(defineProps<{
  modelValue:   string | null
  corridorOnly?: boolean
  placeholder?: string
}>(), {
  corridorOnly: false,
  placeholder:  'Search stations…',
})

const emit = defineEmits<{
  (e: 'update:modelValue', v: string | null): void
}>()

const containerRef = ref<HTMLElement | null>(null)
const inputRef     = ref<HTMLInputElement | null>(null)
const listRef      = ref<HTMLElement | null>(null)

const query   = ref('')
const isOpen  = ref(false)
const hovered = ref<number | null>(null)

const { data: stations } = useStationsQuery(() => props.corridorOnly)

// Seed input from modelValue label when it changes externally
watch(() => props.modelValue, (code) => {
  if (!code) { query.value = ''; return }
  const match = stations.value?.find(s => s.station_code === code)
  if (match) query.value = `${match.station_code} — ${match.station_name}`
})

const fuse = computed(() => {
  if (!stations.value?.length) return null
  return new Fuse(stations.value, {
    keys: ['station_code', 'station_name'],
    threshold: 0.35,
    includeScore: true,
  })
})

const filteredStations = computed<StationRecord[]>(() => {
  if (!stations.value?.length) return []
  const q = query.value.trim()
  if (!q) return stations.value.slice(0, 40)
  return fuse.value?.search(q).map(r => r.item) ?? []
})

function open() { isOpen.value = true; hovered.value = 0 }
function close() { isOpen.value = false; hovered.value = null }

function moveDown() {
  if (!isOpen.value) { open(); return }
  hovered.value = Math.min((hovered.value ?? -1) + 1, filteredStations.value.length - 1)
  scrollToHighlighted()
}
function moveUp() {
  hovered.value = Math.max((hovered.value ?? 0) - 1, 0)
  scrollToHighlighted()
}
function scrollToHighlighted() {
  if (hovered.value === null) return
  const el = listRef.value?.querySelector(`#combobox-opt-${hovered.value}`)
  el?.scrollIntoView({ block: 'nearest' })
}

function selectOption(station: StationRecord) {
  emit('update:modelValue', station.station_code)
  query.value = `${station.station_code} — ${station.station_name}`
  close()
}
function selectHighlighted() {
  if (hovered.value !== null && filteredStations.value[hovered.value]) {
    selectOption(filteredStations.value[hovered.value])
  }
}
function clear() {
  emit('update:modelValue', null)
  query.value = ''
  inputRef.value?.focus()
}
function onBackspace() {
  if (!query.value && props.modelValue) clear()
}

// Close on outside click
function handleOutsideClick(e: MouseEvent) {
  if (!containerRef.value?.contains(e.target as Node)) close()
}
onMounted(() => document.addEventListener('mousedown', handleOutsideClick))
onBeforeUnmount(() => document.removeEventListener('mousedown', handleOutsideClick))
</script>

<style scoped>
.combobox { position: relative; }

.combobox__input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.combobox__input {
  width: 100%;
  padding: var(--sp-2) var(--sp-3);
  padding-right: var(--sp-8);
  background: var(--surface-0);
  border: 1px solid var(--surface-3);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-family: var(--font-body);
  transition: border-color var(--dur-fast) var(--ease-out);
}
.combobox__input::placeholder { color: var(--text-muted); }
.combobox__input:focus {
  outline: none;
  border-color: var(--via-yellow-dim);
  box-shadow: 0 0 0 2px var(--via-yellow-glow);
}

.combobox__clear {
  position: absolute;
  right: var(--sp-3);
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: var(--text-lg);
  line-height: 1;
  cursor: pointer;
  padding: 0 2px;
}
.combobox__clear:hover { color: var(--text-primary); }

.combobox__list {
  position: absolute;
  top: calc(100% + 4px);
  left: 0; right: 0;
  background: var(--surface-1);
  border: 1px solid var(--surface-3);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  max-height: 240px;
  overflow-y: auto;
  z-index: 200;
  list-style: none;
  padding: var(--sp-1) 0;
}

.combobox__option {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  padding: var(--sp-2) var(--sp-3);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: background var(--dur-fast) var(--ease-out);
}
.combobox__option--highlighted,
.combobox__option:hover {
  background: var(--surface-2);
}

.combobox__option-code {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--via-yellow);
  width: 44px;
  flex-shrink: 0;
}
.combobox__option-name {
  flex: 1;
  min-width: 0;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.combobox__option-check {
  color: var(--status-good);
  font-size: var(--text-xs);
}

/* Dropdown transition */
.combobox-list-enter-active { transition: opacity var(--dur-fast) var(--ease-out), transform var(--dur-fast) var(--ease-out); }
.combobox-list-leave-active { transition: opacity var(--dur-fast) var(--ease-in); }
.combobox-list-enter-from   { opacity: 0; transform: translateY(-4px); }
.combobox-list-leave-to     { opacity: 0; }
</style>
