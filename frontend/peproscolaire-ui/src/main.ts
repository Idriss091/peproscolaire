import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { webSocketService } from './services/websocket'

// Create app instance
const app = createApp(App)

// Configure Pinia store
const pinia = createPinia()
app.use(pinia)

// Configure router
app.use(router)

// Initialize WebSocket service after Pinia is ready
webSocketService.initialize()
app.config.globalProperties.$websocket = webSocketService

// Mount the app
app.mount('#app')