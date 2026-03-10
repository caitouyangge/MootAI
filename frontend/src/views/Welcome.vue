<template>
  <div class="welcome-page" @click.self="() => {}">
    <!-- 动态紫色背景 -->
    <div class="animated-background">
      <div class="bg-gradient"></div>
      <div class="bg-mesh"></div>
      <div class="bg-particles">
        <div v-for="i in 12" :key="i" class="particle" :style="getParticleStyle(i)"></div>
      </div>
      <div class="bg-noise" aria-hidden="true"></div>
    </div>
    
    <!-- 主要内容 -->
    <div class="welcome-content" :class="{ 'fade-out': showLoginForm || showRegisterForm }">
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
        <button type="button" class="cta-primary" @click.stop="showLogin">
          登录 / 注册
        </button>
        <p class="cta-hint">点击上方按钮进入 MootAI</p>
      </div>
    </div>
    
    <!-- 登录弹窗 -->
    <transition name="modal">
      <div class="modal-overlay" v-if="showLoginForm" @click.self="closeLogin">
        <LoginForm @close="closeLogin" @switch-to-register="switchToRegister" />
      </div>
    </transition>
    
    <!-- 注册弹窗 -->
    <transition name="modal">
      <div class="modal-overlay" v-if="showRegisterForm" @click.self="closeRegister">
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

const showLogin = () => {
  if (!showLoginForm.value && !showRegisterForm.value) {
    showLoginForm.value = true
  }
}

const closeLogin = () => {
  showLoginForm.value = false
}

const closeRegister = () => {
  showRegisterForm.value = false
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

const getParticleStyle = (index) => {
  const size = Math.random() * 2.5 + 1.2
  const left = Math.random() * 100
  const delay = Math.random() * 5
  const duration = Math.random() * 3 + 2
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${left}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`
  }
}
</script>

<style scoped>
.welcome-page {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  cursor: pointer;
  background: var(--bg-secondary);
}

/* 动态背景 */
.animated-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.bg-gradient {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    135deg,
    var(--primary-purple-lightest) 0%,
    var(--primary-purple-lighter) 25%,
    var(--primary-purple-light) 50%,
    var(--primary-purple) 75%,
    var(--primary-purple-dark) 100%
  );
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
}

.bg-mesh {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image:
    radial-gradient(ellipse 80% 50% at 50% 15%, rgba(255,255,255,0.18) 0%, transparent 55%),
    radial-gradient(ellipse 60% 40% at 75% 85%, rgba(255,255,255,0.08) 0%, transparent 50%),
    radial-gradient(ellipse 50% 35% at 25% 70%, rgba(139, 92, 246, 0.06) 0%, transparent 50%);
  pointer-events: none;
}

/* 极淡噪声纹理 */
.bg-noise {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0.035;
  pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  background-repeat: repeat;
}

.bg-particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.particle {
  position: absolute;
  background: rgba(255, 255, 255, 0.35);
  border-radius: 50%;
  animation: float 3s ease-in-out infinite;
  box-shadow: 0 0 6px rgba(139, 92, 246, 0.25);
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
  transition: opacity var(--transition-base);
}

.welcome-content.fade-out {
  opacity: 0.2;
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
  filter: drop-shadow(0 8px 24px rgba(139, 92, 246, 0.35));
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
  background: radial-gradient(circle, rgba(139, 92, 246, 0.25), transparent 70%);
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
  box-shadow: 0 8px 32px rgba(139, 92, 246, 0.4);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.cta-primary:hover {
  transform: scale(1.04) translateY(-2px);
  box-shadow: 0 12px 48px rgba(139, 92, 246, 0.55), 0 0 0 1px rgba(255,255,255,0.08);
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

/* 弹窗覆盖层 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.52);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

/* 弹窗过渡动画 */
.modal-enter-active,
.modal-leave-active {
  transition: all var(--transition-base);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-overlay > *,
.modal-leave-to .modal-overlay > * {
  transform: scale(0.9) translateY(20px);
}

.modal-enter-to .modal-overlay > *,
.modal-leave-from .modal-overlay > * {
  transform: scale(1) translateY(0);
}
</style>
