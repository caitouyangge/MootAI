import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import pinia from './stores'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import Vant from 'vant'
import 'vant/lib/index.css'
import '@vant/touch-emulator'

const app = createApp(App)

app.use(router)
app.use(pinia)
app.use(ElementPlus)
app.use(Vant)

app.mount('#app')
