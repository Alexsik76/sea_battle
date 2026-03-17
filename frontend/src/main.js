import 'virtual:uno.css'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { MotionPlugin } from '@vueuse/motion'
import './style.css'
import App from './App.vue'

const app = createApp(App)
app.use(createPinia())
app.use(MotionPlugin)
app.mount('#app')
