<template>
  <div class="welcome-page">
    <!-- 仅内容区上移离场 -->
    <div class="welcome-content-wrap" :class="{ 'scene-exit': isModalOpen }">
      <div class="welcome-content">
      <!-- Logo和标题区域 -->
      <div class="hero-section fade-in">
        <div class="logo-container float">
          <div class="logo-icon">⚖️</div>
          <div class="logo-ring"></div>
          <div class="logo-glow"></div>
        </div>
        <h1 class="main-title">
          <span class="title-text">MootAI</span>
          <span class="title-subtitle">AI 模拟法庭</span>
        </h1>
        <p class="main-description">拟真法庭辩论体验</p>
      </div>
      
      <!-- 装饰元素（弱化，仅作氛围） -->
      <div class="decorative-elements" aria-hidden="true">
        <div class="deco-item deco-1 float" style="animation-delay: 0s"></div>
        <div class="deco-item deco-2 float" style="animation-delay: 1s"></div>
        <div class="deco-item deco-3 float" style="animation-delay: 2s"></div>
      </div>
      
      <!-- 主 CTA -->
      <div class="cta-section">
        <button type="button" class="cta-primary cta-hover" @click.stop="showLogin">
          登录 / 注册
        </button>
      </div>
      </div>
    </div>

    <!-- 登录（无遮罩，直接叠在背景上） -->
    <transition name="modal">
      <div class="modal-overlay" v-if="showLoginForm">
        <button type="button" class="back-to-welcome" @click.stop="closeLogin" aria-label="返回">
          <span class="back-arrow" aria-hidden="true">
            <svg class="back-arrow-icon" viewBox="0 0 24 24" fill="none">
              <path d="M5.5 14.5L12 8l6.5 6.5" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </span>
          <span class="back-text">返回</span>
        </button>
        <LoginForm @close="closeLogin" @switch-to-register="switchToRegister" />
      </div>
    </transition>

    <!-- 注册（无遮罩） -->
    <transition name="modal">
      <div class="modal-overlay" v-if="showRegisterForm">
        <button type="button" class="back-to-welcome" @click.stop="closeRegister" aria-label="返回">
          <span class="back-arrow" aria-hidden="true">
            <svg class="back-arrow-icon" viewBox="0 0 24 24" fill="none">
              <path d="M5.5 14.5L12 8l6.5 6.5" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </span>
          <span class="back-text">返回</span>
        </button>
        <RegisterForm @close="closeRegister" @switch-to-login="switchToLogin" />
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import LoginForm from '@/components/LoginForm.vue'
import RegisterForm from '@/components/RegisterForm.vue'

const showLoginForm = ref(false)
const showRegisterForm = ref(false)
/** 任一弹窗打开时为 true，用于保持欢迎场景上移状态（避免登录⇄注册切换时场景回弹） */
const isModalOpen = ref(false)
const WELCOME_MS = 600
const MODAL_MS = 600
let openSeq = 0

const showLogin = () => {
  if (!showLoginForm.value && !showRegisterForm.value) {
    isModalOpen.value = true
    // 串行：先让欢迎内容离场，再让登录入场，避免两者重叠
    const seq = ++openSeq
    window.setTimeout(() => {
      if (seq !== openSeq) return
      showLoginForm.value = true
    }, WELCOME_MS)
  }
}

const closeLogin = () => {
  openSeq++
  showLoginForm.value = false
  // 串行：先让登录离场，再让欢迎内容回场
  if (!showRegisterForm.value) {
    window.setTimeout(() => {
      if (showLoginForm.value || showRegisterForm.value) return
      isModalOpen.value = false
    }, MODAL_MS)
  }
}

const closeRegister = () => {
  openSeq++
  showRegisterForm.value = false
  if (!showLoginForm.value) {
    window.setTimeout(() => {
      if (showLoginForm.value || showRegisterForm.value) return
      isModalOpen.value = false
    }, MODAL_MS)
  }
}

const switchToRegister = () => {
  showLoginForm.value = false
  setTimeout(() => {
    showRegisterForm.value = true
  }, 200)
}

const switchToLogin = () => {
  showRegisterForm.value = false
  setTimeout(() => {
    showLoginForm.value = true
  }, 200)
}
</script>

<style scoped>
.welcome-page {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  cursor: default;
  background: transparent;
}

/* 仅内容区上移离场（背景不动），更慢更弹 */
.welcome-content-wrap {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  will-change: transform;
  transition: transform 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.welcome-content-wrap.scene-exit {
  transform: translateY(-100%);
}

/* 主要内容 */
.welcome-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 40px;
}

.welcome-content.fade-out {
  opacity: 0.18;
}

/* Hero区域 */
.hero-section {
  text-align: center;
  margin-bottom: 0;
  animation: fadeIn 1s ease;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.logo-container {
  position: relative;
  display: inline-block;
  margin-bottom: 30px;
}

.logo-icon {
  font-size: 80px;
  filter: drop-shadow(0 8px 24px rgba(6, 182, 212, 0.35));
  position: relative;
  z-index: 1;
}

.logo-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 120px;
  height: 120px;
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 50%;
  z-index: 0;
}

.logo-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 160px;
  height: 160px;
  background: radial-gradient(circle, rgba(6, 182, 212, 0.25), transparent 70%);
  border-radius: 50%;
  animation: pulse 2.5s ease-in-out infinite;
}

.main-title {
  margin: 0 0 20px 0;
}

.title-text {
  display: block;
  font-size: clamp(48px, 6vw, 64px);
  font-weight: 300;
  background: linear-gradient(160deg, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.92) 45%, rgba(220, 210, 255, 0.9) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.2em;
  margin-bottom: 10px;
}

.title-subtitle {
  display: block;
  font-size: 20px;
  color: var(--text-white);
  font-weight: 300;
  letter-spacing: 0.35em;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  margin-top: 4px;
}

.main-description {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.88);
  line-height: 1.6;
  margin: 16px 0 0 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.15);
  font-weight: 400;
  letter-spacing: 0.02em;
}

/* 装饰元素 */
.decorative-elements {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.deco-item {
  position: absolute;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255,255,255,0.08), transparent);
  border: 1px solid rgba(255,255,255,0.06);
  opacity: 0.8;
}

.deco-1 {
  top: 15%;
  left: 10%;
}

.deco-2 {
  top: 20%;
  right: 15%;
}

.deco-3 {
  bottom: 25%;
  left: 20%;
}

/* 主 CTA */
.cta-section {
  margin-top: auto;
  padding-bottom: 48px;
  text-align: center;
}

.cta-primary {
  display: inline-block;
  padding: 14px 40px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.08em;
  color: #fff;
  background: linear-gradient(135deg, var(--primary-purple), var(--primary-purple-dark));
  border: none;
  border-radius: 999px;
  cursor: pointer;
  box-shadow: 0 8px 32px rgba(6, 182, 212, 0.40);
  transition: transform var(--transition-hover) ease, box-shadow var(--transition-hover) ease;
}

.cta-primary:hover {
  transform: scale(1.04) translateY(-2px);
  box-shadow: 0 12px 48px rgba(6, 182, 212, 0.50), 0 0 0 1px rgba(255,255,255,0.08);
}

.cta-primary:active {
  transform: scale(0.98) translateY(0);
}

.cta-hint {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin: 12px 0 0 0;
  font-weight: 400;
  letter-spacing: 0.04em;
}

/* 无遮罩层，仅居中放置表单；点击空白处仍可关闭 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  /* 允许点击穿透到背景触发水波纹 */
  pointer-events: none;
}

/* 背景上方的返回：^ + 返回 */
.back-to-welcome {
  position: fixed;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1101;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 6px 10px;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.95);
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.04em;
  cursor: pointer !important;
  pointer-events: auto !important;
  user-select: none;
  opacity: 1;
  transition: opacity 0.22s ease, color 0.2s ease, transform 0.2s ease;
}

.back-to-welcome,
.back-to-welcome * {
  cursor: pointer !important;
  pointer-events: auto !important;
}

.back-to-welcome:hover {
  color: #fff;
}

.back-to-welcome:active {
  transform: translateX(-50%) scale(0.98);
}

.back-arrow {
  display: block;
}

.back-arrow-icon {
  width: 20px;
  height: 20px;
  display: block;
}

.back-text {
  font-size: 12px;
  opacity: 0.95;
  cursor: pointer !important;
  pointer-events: auto !important;
  user-select: none;
}

/* 去掉子组件自带的遮罩背景，保留点击关闭 */
.modal-overlay :deep(.login-form-overlay),
.modal-overlay :deep(.register-form-overlay) {
  background: transparent;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
  animation: none !important;
  /* 保留全屏 overlay 用于拦截背景点击；把“返回”按钮抬到它上面 */
  z-index: 1000 !important;
  /* 但本页需要背景可点击出水波纹，所以 overlay 自身不吃事件 */
  pointer-events: none !important;
}

/* 表单本体仍需可交互 */
.modal-overlay :deep(.login-form-container),
.modal-overlay :deep(.register-form-container) {
  pointer-events: auto !important;
}

/* 去掉子组件内部任何入场动画，避免与转场 transform 叠加 */
.modal-overlay :deep(.login-form-container),
.modal-overlay :deep(.register-form-container),
.modal-overlay :deep(.login-form),
.modal-overlay :deep(.register-form) {
  animation: none !important;
}

/* 过渡：更慢更弹，登录/注册从底部上移入画 */
.modal-enter-active,
.modal-leave-active {
  /* 保持不透明（不做淡入淡出），但提供过渡时长给 Vue，用于正确等待 enter/leave 完成 */
  transition: opacity 0.6s linear;
}

.modal-enter-active :deep(.login-form-container),
.modal-enter-active :deep(.register-form-container),
.modal-leave-active :deep(.login-form-container),
.modal-leave-active :deep(.register-form-container) {
  animation: none;
  transition: transform 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  will-change: transform;
}

.modal-enter-from {
  opacity: 1;
}
.modal-enter-from .back-to-welcome {
  opacity: 0;
  transform: translateX(-50%) translateY(-4px);
}
.modal-enter-from :deep(.login-form-container),
.modal-enter-from :deep(.register-form-container) {
  transform: translateY(110vh);
}

.modal-enter-to {
  opacity: 1;
}
.modal-enter-active .back-to-welcome {
  transition-delay: 0.6s;
}
.modal-enter-to :deep(.login-form-container),
.modal-enter-to :deep(.register-form-container) {
  transform: translateY(0);
}

.modal-leave-from {
  opacity: 1;
}
.modal-leave-active .back-to-welcome {
  transition-delay: 0s;
}
.modal-leave-to .back-to-welcome {
  opacity: 0;
  transform: translateX(-50%) translateY(-4px);
}
.modal-leave-from :deep(.login-form-container),
.modal-leave-from :deep(.register-form-container) {
  transform: translateY(0);
}

.modal-leave-to {
  opacity: 1;
}
.modal-leave-to :deep(.login-form-container),
.modal-leave-to :deep(.register-form-container) {
  transform: translateY(110vh);
}
</style>
