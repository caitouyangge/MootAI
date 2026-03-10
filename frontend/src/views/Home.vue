<template>
  <div class="home-page">
    <!-- 顶部分割/装饰线 -->
    <div class="top-accent" aria-hidden="true"></div>

    <!-- 页面标题区域 -->
    <div class="page-banner fade-in">
      <div class="banner-content">
        <div class="banner-title-wrap">
          <h1 class="banner-title">智能模拟法庭</h1>
        </div>
        <p class="banner-subtitle">AI驱动的拟真法庭辩论模拟系统</p>
      </div>
    </div>

    <!-- 主要内容：产品卡片 + 功能亮点 -->
    <div class="content-wrapper">
      <div class="welcome-card card-hover fade-in">
        <div class="welcome-icon-svg" aria-hidden="true">
          <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <!-- 天平底座 -->
            <path d="M12 52h40" stroke="var(--primary-purple)" stroke-width="2.5" stroke-linecap="round"/>
            <path d="M20 52v-4h24v4" stroke="var(--primary-purple)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <!-- 立柱 -->
            <path d="M32 52V28" stroke="var(--primary-purple)" stroke-width="2" stroke-linecap="round"/>
            <!-- 横梁 -->
            <path d="M18 28h28" stroke="var(--primary-purple)" stroke-width="2" stroke-linecap="round"/>
            <!-- 左盘 + 吊线 -->
            <path d="M18 28v6l-6 8h12l-6-8v-6" stroke="var(--primary-purple)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" fill="var(--primary-purple-lightest)" opacity="0.9"/>
            <!-- 右盘 + 吊线 -->
            <path d="M46 28v6l6 8H40l6-8v-6" stroke="var(--primary-purple)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" fill="var(--primary-purple-lightest)" opacity="0.9"/>
            <!-- 顶部装饰（象征公正/AI） -->
            <circle cx="32" cy="22" r="5" stroke="var(--primary-purple)" stroke-width="1.8" fill="var(--primary-purple-lightest)"/>
          </svg>
        </div>
        <h2 class="welcome-title">欢迎使用智能模拟法庭</h2>
        <p class="welcome-desc">
          通过AI技术，为您提供完整的法庭模拟体验<br>
          包括庭前准备、庭中辩论和庭后宣判全流程
        </p>

        <!-- 功能亮点区：三个核心能力 -->
        <div class="feature-highlights">
          <div class="feature-item">
            <span class="feature-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <polyline points="10 9 9 9 8 9"/>
              </svg>
            </span>
            <span class="feature-label">庭前准备</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                <path d="M12 8h4M12 12h4M12 16h2"/>
              </svg>
            </span>
            <span class="feature-label">庭中辩论</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 20h16M6 16v4M10 16v4M14 16v4M18 16v4"/>
                <path d="M12 4L4 10v2h16v-2L12 4z"/>
                <path d="M8 10l4-4 4 4"/>
              </svg>
            </span>
            <span class="feature-label">庭后宣判</span>
          </div>
        </div>

        <button
          type="button"
          class="start-button cta-hover"
          @click="goToCourtroom"
        >
          <span class="button-icon-svg" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="5 3 19 12 5 21 5 3"/>
            </svg>
          </span>
          <span>开始模拟</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

onMounted(() => {
  document.body.classList.add('no-scroll')
})

onBeforeUnmount(() => {
  document.body.classList.remove('no-scroll')
})

const goToCourtroom = () => {
  try {
    router.push({ name: 'courtroom-content' })
      .catch(err => {
        console.error('路由跳转失败:', err)
        ElMessage.error('跳转失败，请重试')
      })
  } catch (error) {
    console.error('跳转出错:', error)
    ElMessage.error('跳转出错，请重试')
  }
}
</script>

<style scoped>
.home-page {
  /* 在 Layout 下总高度 = 52px + 本块高度，用 100vh - 52px 避免底部多出一截可滚动空白 */
  min-height: calc(100vh - 52px);
  box-sizing: border-box; /* 让 padding 计入高度，避免底部产生额外可滚动空白 */
  padding-bottom: 60px;
  position: relative;
  z-index: 1; /* 高于固定背景，保证内容在背景之上 */
  isolation: isolate;
  overflow: hidden;
}

/* 顶部分割/装饰线：产品首屏感 */
.top-accent {
  height: 3px;
  max-width: 200px;
  margin: 0 auto 32px;
  position: relative;
  z-index: 1;
}

/* 页面横幅：纯色 + 几何装饰（无渐变） */
.page-banner {
  position: relative;
  background: var(--primary-purple);
  border-radius: var(--radius-xl);
  padding: 36px 24px;
  margin-bottom: 32px;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  max-width: 720px;
  margin-left: auto;
  margin-right: auto;
  z-index: 1;
}

.page-banner.fade-in {
  /* 首屏横幅：带轻微 3D 下落 + 光感 */
  transform-origin: center top;
  animation:
    homeHeroDrop 1s cubic-bezier(0.16, 1, 0.3, 1) 0.05s both,
    homeHeroGlow 1.8s ease-out 0.4s both;
}

.page-banner::before {
  display: none;
}

.banner-content {
  position: relative;
  z-index: 1;
  text-align: center;
  color: var(--text-white);
}

.banner-title-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  margin-bottom: 14px;
}




.banner-title {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.banner-subtitle {
  font-size: 14px;
  opacity: 0.9;
  margin: 0;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}

/* 内容区域：加大上下留白 */
.content-wrapper {
  max-width: 720px;
  margin: 0 auto;
  padding: 48px 24px 32px;
  position: relative;
  z-index: 1;
}

.welcome-card.fade-in {
  /* 主卡片：稍晚于横幅的上升动画 */
  animation: homeCardRise 0.9s cubic-bezier(0.16, 1, 0.3, 1) 0.35s both;
}

@keyframes homeHeroDrop {
  from {
    opacity: 0;
    transform: translateY(-28px) scale(0.96) rotateX(-10deg);
    filter: blur(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1) rotateX(0deg);
    filter: blur(0);
  }
}

@keyframes homeHeroGlow {
  from {
    box-shadow: 0 0 0 rgba(6, 182, 212, 0.0);
  }
  40% {
    box-shadow: 0 14px 40px rgba(6, 182, 212, 0.55);
  }
  to {
    box-shadow: var(--shadow-lg);
  }
}

@keyframes homeCardRise {
  from {
    opacity: 0;
    transform: translateY(22px) scale(0.96);
    filter: blur(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
    filter: blur(0);
  }
}

/* 产品卡片：玻璃态 + 卡片悬浮阴影 + 统一 hover */
.welcome-card {
  --card-radius: 24px;
  position: relative;
  background: rgba(255, 255, 255, 0.68);
  backdrop-filter: blur(18px) saturate(1.25);
  -webkit-backdrop-filter: blur(18px) saturate(1.25);
  border: 1px solid rgba(255, 255, 255, 0.44);
  border-radius: var(--card-radius);
  padding: 56px 40px 48px;
  text-align: center;
  box-shadow: var(--shadow-card);
  transition: transform var(--transition-hover) ease, box-shadow var(--transition-hover) ease;
}

.welcome-card::before {
  /* 顶部高光与边缘“折射感” */
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background:
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='44' height='44' viewBox='0 0 44 44'%3E%3Cg fill='none'%3E%3Ccircle cx='6' cy='6' r='1.2' fill='%236366f1' opacity='0.18'/%3E%3Ccircle cx='22' cy='18' r='1.0' fill='%236366f1' opacity='0.14'/%3E%3Ccircle cx='34' cy='34' r='1.2' fill='%236366f1' opacity='0.18'/%3E%3Ccircle cx='14' cy='30' r='0.9' fill='%236366f1' opacity='0.12'/%3E%3C/g%3E%3C/svg%3E"),
    rgba(255, 255, 255, 0.35);
  background-size: 44px 44px, auto;
  background-repeat: repeat, no-repeat;
  opacity: 0.72;
  pointer-events: none;
  mix-blend-mode: overlay;
}

.welcome-card::after {
  /* 细内描边：更像玻璃边缘 */
  content: '';
  position: absolute;
  inset: 10px;
  border-radius: calc(var(--card-radius) - 10px);
  border: 1px solid rgba(255, 255, 255, 0.22);
  pointer-events: none;
  opacity: 0.8;
}

.welcome-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-card-hover), 0 0 0 1px rgba(255, 255, 255, 0.10);
}

.welcome-icon-svg {
  width: 80px;
  height: 80px;
  margin: 0 auto 28px;
  animation: float 3s ease-in-out infinite;
}

.welcome-icon-svg svg {
  width: 100%;
  height: 100%;
}

.welcome-title {
  font-size: 26px;
  font-weight: bold;
  color: var(--text-primary);
  margin: 0 0 14px 0;
}

.welcome-desc {
  font-size: 15px;
  color: var(--text-secondary);
  line-height: 1.8;
  margin: 0 0 32px 0;
}

/* 功能亮点区 */
.feature-highlights {
  display: flex;
  justify-content: center;
  gap: 32px;
  flex-wrap: wrap;
  margin-bottom: 40px;
  padding: 24px 16px;
  position: relative;
  background: rgba(255, 255, 255, 0.42);
  backdrop-filter: blur(14px) saturate(1.15);
  -webkit-backdrop-filter: blur(14px) saturate(1.15);
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.34);
  box-shadow: 0 10px 30px rgba(17, 24, 39, 0.06);
}

.feature-highlights::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  opacity: 0.35;
  pointer-events: none;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  min-width: 100px;
  opacity: 0;
  transform: translateY(12px) scale(0.98);
  /* 功能点：等主卡片基本就位后再依次弹入 */
  animation: featurePop 0.7s cubic-bezier(0.22, 1, 0.36, 1) 0.8s forwards;
}

.feature-item:nth-child(2) {
  animation-delay: 1s;
}

.feature-item:nth-child(3) {
  animation-delay: 1.2s;
}

@keyframes featurePop {
  from {
    opacity: 0;
    transform: translateY(16px) scale(0.96);
  }
  70% {
    opacity: 1;
    transform: translateY(-2px) scale(1.02);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.feature-icon {
  width: 36px;
  height: 36px;
  color: var(--primary-purple);
  flex-shrink: 0;
}

.feature-icon svg {
  width: 100%;
  height: 100%;
}

.feature-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

/* 主按钮：与 Welcome CTA 统一 - 渐变、阴影、hover 微动 */
.start-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  height: 52px;
  padding: 0 36px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.06em;
  color: #fff;
  background: rgba(6, 182, 212, 0.9);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: none;
  border-radius: 999px;
  cursor: pointer;
  box-shadow: 0 8px 32px rgba(6, 182, 212, 0.40);
  opacity: 0;
  transform: translateY(14px) scale(0.96);
  /* 三个功能点弹入结束后再入场（约 0.8+0.7、1+0.7、1.2+0.7 中最大 1.9s） */
  animation: ctaEnter 0.8s cubic-bezier(0.22, 1, 0.36, 1) 1.8s forwards;
  transition: transform var(--transition-hover) ease, box-shadow var(--transition-hover) ease;
}

.start-button:hover {
  transform: scale(1.04) translateY(-2px);
  box-shadow: 0 12px 48px rgba(6, 182, 212, 0.50), 0 0 0 1px rgba(255, 255, 255, 0.08);
}

.start-button:active {
  transform: scale(0.98) translateY(0);
}

@keyframes ctaEnter {
  from {
    opacity: 0;
    transform: translateY(18px) scale(0.94);
  }
  70% {
    opacity: 1;
    transform: translateY(-1px) scale(1.03);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.button-icon-svg {
  width: 20px;
  height: 20px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.button-icon-svg svg {
  width: 100%;
  height: 100%;
}

/* 响应式 */
@media (max-width: 768px) {
  .top-accent {
    margin-bottom: 24px;
  }

  .content-wrapper {
    padding: 32px 20px 24px;
  }

  .welcome-card {
    padding: 40px 24px 36px;
  }

  .welcome-icon-svg {
    width: 64px;
    height: 64px;
    margin-bottom: 22px;
  }

  .welcome-title {
    font-size: 22px;
  }

  .welcome-desc {
    font-size: 14px;
    margin-bottom: 28px;
  }

  .feature-highlights {
    gap: 24px;
    margin-bottom: 32px;
    padding: 20px 12px;
  }

  .feature-item {
    min-width: 80px;
  }

  .feature-icon {
    width: 32px;
    height: 32px;
  }

  .feature-label {
    font-size: 13px;
  }

  .start-button {
    height: 48px;
    padding: 0 28px;
    font-size: 15px;
  }
}

/* 降级：不支持 backdrop-filter 时，提高不透明度避免“脏灰” */
@supports not ((backdrop-filter: blur(2px)) or (-webkit-backdrop-filter: blur(2px))) {
  .welcome-card {
    background: rgba(255, 255, 255, 0.92);
  }
  .feature-highlights {
    background: rgba(255, 255, 255, 0.88);
  }
}
</style>
