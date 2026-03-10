<template>
  <div class="home-page">
    <!-- 顶部分割/装饰线 -->
    <div class="top-accent" aria-hidden="true"></div>

    <!-- 页面标题区域：紫色渐变 + 几何/线条装饰 -->
    <div class="page-banner fade-in">
      <div class="banner-content">
        <div class="banner-title-wrap">
          <span class="title-icon-svg" aria-hidden="true">
            <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M24 4L8 14v20l16 10 16-10V14L24 4z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" fill="rgba(255,255,255,0.12)"/>
              <path d="M24 24V4M8 14l16 10 16-10M8 34l16-10 16 10" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" opacity="0.9"/>
            </svg>
          </span>
          <h1 class="banner-title">智能模拟法庭</h1>
        </div>
        <p class="banner-subtitle">AI驱动的拟真法庭辩论模拟系统</p>
      </div>
      <!-- 几何/线条装饰（替代 emoji） -->
      <div class="banner-decoration">
        <svg class="deco-shape deco-1" viewBox="0 0 120 120" aria-hidden="true">
          <circle cx="60" cy="60" r="45" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="1"/>
          <circle cx="60" cy="60" r="28" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.8"/>
          <line x1="60" y1="15" x2="60" y2="105" stroke="rgba(255,255,255,0.12)" stroke-width="0.6"/>
          <line x1="15" y1="60" x2="105" y2="60" stroke="rgba(255,255,255,0.12)" stroke-width="0.6"/>
        </svg>
        <svg class="deco-shape deco-2" viewBox="0 0 80 80" aria-hidden="true">
          <path d="M10 40 Q40 10 70 40 Q40 70 10 40" fill="none" stroke="rgba(255,255,255,0.12)" stroke-width="1"/>
          <path d="M25 40 Q40 25 55 40" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="0.8"/>
        </svg>
        <svg class="deco-shape deco-3" viewBox="0 0 100 60" aria-hidden="true">
          <rect x="5" y="5" width="35" height="50" rx="2" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
          <rect x="60" y="5" width="35" height="50" rx="2" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
          <line x1="22" y1="20" x2="22" y2="45" stroke="rgba(255,255,255,0.08)" stroke-width="0.6"/>
          <line x1="77" y1="20" x2="77" y2="45" stroke="rgba(255,255,255,0.08)" stroke-width="0.6"/>
        </svg>
      </div>
    </div>

    <!-- 主要内容：产品卡片 + 功能亮点 -->
    <div class="content-wrapper">
      <div class="welcome-card card-hover fade-in">
        <div class="welcome-icon-svg" aria-hidden="true">
          <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M32 8L12 20v24l20 12 20-12V20L32 8z" stroke="var(--primary-purple)" stroke-width="2" stroke-linejoin="round" fill="var(--primary-purple-lightest)"/>
            <path d="M32 32V8M12 20l20 12 20-12M12 44l20-12 20 12" stroke="var(--primary-purple)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" opacity="0.85"/>
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
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

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
  min-height: 100vh;
  background: var(--bg-secondary);
  padding-bottom: 60px;
  position: relative;
}

/* 顶部分割/装饰线：产品首屏感 */
.top-accent {
  height: 3px;
  max-width: 200px;
  margin: 0 auto 32px;
  background: linear-gradient(90deg, transparent, var(--primary-purple-light) 20%, var(--primary-purple) 50%, var(--primary-purple-light) 80%, transparent);
  border-radius: 2px;
  opacity: 0.7;
}

/* 页面横幅：紫色渐变 + 几何装饰 */
.page-banner {
  position: relative;
  background: linear-gradient(135deg, var(--primary-purple) 0%, var(--primary-purple-light) 100%);
  border-radius: var(--radius-xl);
  padding: 36px 24px;
  margin-bottom: 32px;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
}

.page-banner::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -10%;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1), transparent);
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
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

.title-icon-svg {
  width: 36px;
  height: 36px;
  color: rgba(255, 255, 255, 0.95);
  animation: float 3s ease-in-out infinite;
}

.title-icon-svg svg {
  width: 100%;
  height: 100%;
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

/* 几何/线条装饰 */
.banner-decoration {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  pointer-events: none;
}

.deco-shape {
  position: absolute;
  color: rgba(255, 255, 255, 0.35);
}

.deco-1 {
  width: 100px;
  height: 100px;
  top: 18%;
  left: 8%;
  animation: float 5s ease-in-out infinite;
}

.deco-2 {
  width: 70px;
  height: 70px;
  top: 28%;
  right: 12%;
  animation: float 4s ease-in-out infinite 0.5s;
}

.deco-3 {
  width: 90px;
  height: 54px;
  bottom: 18%;
  left: 15%;
  animation: float 5.5s ease-in-out infinite 1s;
}

/* 内容区域：加大上下留白 */
.content-wrapper {
  max-width: 720px;
  margin: 0 auto;
  padding: 48px 24px 32px;
}

/* 产品卡片：玻璃态 + 卡片悬浮阴影 + 统一 hover */
.welcome-card {
  --card-radius: 24px;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(139, 92, 246, 0.18);
  border-radius: var(--card-radius);
  padding: 56px 40px 48px;
  text-align: center;
  box-shadow: var(--shadow-card);
  transition: transform var(--transition-hover) ease, box-shadow var(--transition-hover) ease;
}

.welcome-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-card-hover);
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
  background: rgba(139, 92, 246, 0.04);
  border-radius: 16px;
  border: 1px solid rgba(139, 92, 246, 0.08);
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  min-width: 100px;
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
  background: linear-gradient(135deg, var(--primary-purple), var(--primary-purple-dark));
  border: none;
  border-radius: 999px;
  cursor: pointer;
  box-shadow: 0 8px 32px rgba(139, 92, 246, 0.4);
  transition: transform var(--transition-hover) ease, box-shadow var(--transition-hover) ease;
}

.start-button:hover {
  transform: scale(1.04) translateY(-2px);
  box-shadow: 0 12px 48px rgba(139, 92, 246, 0.55), 0 0 0 1px rgba(255, 255, 255, 0.08);
}

.start-button:active {
  transform: scale(0.98) translateY(0);
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
</style>
