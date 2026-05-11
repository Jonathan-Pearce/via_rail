import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'
import router from './router'
import App from './App.vue'
import './styles/global.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,        // 1 min — data is fresh enough
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
})

createApp(App)
  .use(createPinia())
  .use(router)
  .use(VueQueryPlugin, { queryClient })
  .mount('#app')
