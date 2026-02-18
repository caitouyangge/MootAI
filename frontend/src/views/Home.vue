<template>
  <div class="home-page">
    <!-- 页面标题区域 -->
    <div class="page-banner fade-in">
      <div class="banner-content">
        <h1 class="banner-title">
          <span class="title-icon">⚖️</span>
          <span class="title-text">智能模拟法庭</span>
        </h1>
        <p class="banner-subtitle">AI驱动的智能诉讼审判模拟系统</p>
      </div>
      <div class="banner-decoration">
        <div class="decoration-item float" style="animation-delay: 0s">📜</div>
        <div class="decoration-item float" style="animation-delay: 1s">⚖️</div>
        <div class="decoration-item float" style="animation-delay: 2s">🔨</div>
      </div>
    </div>
    
    <!-- 主要内容 -->
    <div class="content-wrapper">
      <div class="welcome-card fade-in">
        <div class="welcome-icon">⚖️</div>
        <h2 class="welcome-title">欢迎使用智能模拟法庭</h2>
        <p class="welcome-desc">
          通过AI技术，为您提供完整的法庭模拟体验<br>
          包括庭前准备、庭中辩论和庭后宣判全流程
        </p>
        <el-button
          type="primary"
          size="large"
          class="start-button"
          @click="goToCourtroom"
        >
          <span class="button-icon">🚀</span>
          <span>开始模拟</span>
        </el-button>
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
    // 跳转到子路由，确保子组件被加载
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
  padding-bottom: 40px;
}

/* 页面横幅 */
.page-banner {
  position: relative;
  background: linear-gradient(135deg, var(--primary-purple) 0%, var(--primary-purple-light) 100%);
  border-radius: var(--radius-xl);
  padding: 32px 24px;
  margin-bottom: 24px;
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

.banner-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 16px;
}

.title-icon {
  font-size: 32px;
  animation: float 3s ease-in-out infinite;
}

.title-text {
  font-size: 24px;
  font-weight: bold;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.banner-subtitle {
  font-size: 14px;
  opacity: 0.9;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}

.banner-decoration {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  pointer-events: none;
}

.decoration-item {
  position: absolute;
  font-size: 32px;
  opacity: 0.3;
}

.decoration-item:nth-child(1) {
  top: 20%;
  left: 10%;
}

.decoration-item:nth-child(2) {
  top: 30%;
  right: 15%;
}

.decoration-item:nth-child(3) {
  bottom: 20%;
  left: 20%;
}

/* 内容区域 */
.content-wrapper {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 24px;
}

.welcome-card {
  background: var(--bg-primary);
  border-radius: var(--radius-xl);
  padding: 60px 40px;
  text-align: center;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border-color);
}

.welcome-icon {
  font-size: 80px;
  margin-bottom: 24px;
  animation: float 3s ease-in-out infinite;
}

.welcome-title {
  font-size: 28px;
  font-weight: bold;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.welcome-desc {
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.8;
  margin: 0 0 40px 0;
}

.start-button {
  height: 56px;
  font-size: 18px;
  font-weight: 600;
  padding: 0 40px;
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
  display: inline-flex;
  align-items: center;
  gap: 12px;
}

.start-button:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-xl);
}

.button-icon {
  font-size: 24px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .welcome-card {
    padding: 40px 24px;
  }
  
  .welcome-icon {
    font-size: 60px;
  }
  
  .welcome-title {
    font-size: 24px;
  }
  
  .welcome-desc {
    font-size: 14px;
  }
  
  .start-button {
    height: 48px;
    font-size: 16px;
    padding: 0 32px;
  }
}
</style>
