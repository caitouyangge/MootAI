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

// 全局错误处理 - 忽略浏览器扩展的错误
window.addEventListener('error', (event) => {
  if (event.filename && event.filename.includes('content.js')) {
    return
  }
  console.error('全局错误:', event.error)
})

window.addEventListener('unhandledrejection', (event) => {
  console.error('未处理的 Promise 拒绝:', event.reason)
})

const app = createApp(App)

app.use(router)
app.use(pinia)
app.use(ElementPlus)
app.use(Vant)

app.mount('#app')
