<script setup>
import { RouterView } from 'vue-router'
import AnimatedBackground from '@/components/AnimatedBackground.vue'

// 点击内容层空白区域时，派发事件让背景在点击位置生成水波纹（内容层盖住了背景，背景收不到点击）
const RIPPLE_IGNORE = 'button, a, input, select, textarea, [contenteditable], .el-button, .el-dialog, .el-message-box, .el-select-dropdown, .menu-item, .logout-btn, .login-btn'

function onAppMainClick(ev) {
  if (ev.target.closest(RIPPLE_IGNORE)) return
  window.dispatchEvent(new CustomEvent('request-ripple', {
    detail: { clientX: ev.clientX, clientY: ev.clientY }
  }))
}
</script>

<template>
  <div class="app-root">
    <!-- 全局背景：始终挂载，避免路由切换时闪白 -->
    <AnimatedBackground
      class="app-bg"
      :enable-ripples="true"
      :click-to-ripple="true"
    />

    <!-- 路由内容层：在背景之上做转场；点击空白区域会派发 request-ripple 让背景出水波纹 -->
    <div class="app-main" @click="onAppMainClick">
      <router-view v-slot="{ Component, route }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" :key="route.path" />
        </transition>
      </router-view>
    </div>
  </div>
</template>

<style>
/* App 根容器：承载全局背景 + 路由内容 */
.app-root {
  position: relative;
  width: 100%;
  min-height: 100%;
}

/* 全局背景：固定铺满视口，位于所有内容下方 */
.app-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
}

/* 主内容层：盖在背景之上 */
.app-main {
  position: relative;
  z-index: 1;
  min-height: 100%;
}

/* 路由转场：丝滑淡入淡出 */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
}
.page-fade-enter-to,
.page-fade-leave-from {
  opacity: 1;
}
</style>
