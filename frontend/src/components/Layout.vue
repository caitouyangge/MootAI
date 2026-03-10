<template>
  <div class="bilibili-layout">
    <!-- 顶部导航栏 -->
    <header class="top-navbar">
      <div class="navbar-container">
        <!-- Logo区域 -->
        <div class="navbar-logo">
          <div class="logo-icon">⚖️</div>
          <span class="logo-text">MootAI</span>
        </div>
        
        <!-- 导航菜单 -->
        <nav class="navbar-menu">
          <router-link 
            v-for="item in menuItems" 
            :key="item.path"
            :to="item.path"
            class="menu-item"
            active-class="active"
          >
            <span class="menu-icon">{{ item.icon }}</span>
            <span class="menu-text">{{ item.name }}</span>
          </router-link>
        </nav>
        
        <!-- 用户信息 -->
        <div class="navbar-user">
          <div v-if="username" class="user-info">
            <span class="username">{{ username }}</span>
            <el-button 
              text 
              size="small" 
              @click="handleLogout"
              class="logout-btn"
            >
              退出
            </el-button>
          </div>
          <div v-else class="user-actions">
            <el-button 
              size="small" 
              @click="showLogin = true"
              class="login-btn"
            >
              登录
            </el-button>
          </div>
        </div>
      </div>
    </header>
    
    <!-- 主内容区 -->
    <main class="main-content">
      <router-view v-slot="{ Component, route }">
        <transition 
          :name="route.meta?.transition || 'page'"
          mode="out-in"
        >
          <component 
            v-if="Component"
            :is="Component" 
            :key="route.path"
          />
          <div v-else class="loading-placeholder">
            <p>组件加载中...</p>
            <el-button type="primary" @click="() => window.location.reload()">刷新页面</el-button>
          </div>
        </transition>
      </router-view>
    </main>
    
    <!-- 登录弹窗 -->
    <LoginForm 
      v-if="showLogin" 
      @close="showLogin = false" 
      @switch-to-register="showRegister = true; showLogin = false"
    />
    
    <!-- 注册弹窗 -->
    <RegisterForm 
      v-if="showRegister" 
      @close="showRegister = false" 
      @switch-to-login="showLogin = true; showRegister = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import LoginForm from './LoginForm.vue'
import RegisterForm from './RegisterForm.vue'

const router = useRouter()
const showLogin = ref(false)
const showRegister = ref(false)
const username = ref(localStorage.getItem('username') || '')

const menuItems = [
  { path: '/home', name: '首页', icon: '🏠' },
  { path: '/courtroom', name: '模拟法庭', icon: '⚖️' },
]

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  localStorage.removeItem('userId')
  username.value = ''
  router.push({ name: 'welcome' })
}

onMounted(() => {
  // 监听登录成功事件
  window.addEventListener('storage', (e) => {
    if (e.key === 'username') {
      username.value = e.newValue || ''
    }
  })
  
  // 监听显示登录弹窗事件
  window.addEventListener('show-login', () => {
    showLogin.value = true
  })
})
</script>

<style scoped>
.bilibili-layout {
  min-height: 100vh;
  background: transparent;
}

/* 顶部导航栏：毛玻璃（透出下方紫色渐变） */
.top-navbar {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.22);
  backdrop-filter: blur(14px) saturate(1.3);
  -webkit-backdrop-filter: blur(14px) saturate(1.3);
  box-shadow: var(--shadow-md);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  animation: navBarSlideIn 0.5s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}

@keyframes navBarSlideIn {
  from {
    opacity: 0;
    transform: translateY(-100%);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes navItemFadeIn {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
  .top-navbar {
    background: rgba(255, 255, 255, 0.88);
  }
}

.navbar-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.navbar-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  user-select: none;
  font-family: var(--font-heading);
  animation: navItemFadeIn 0.4s cubic-bezier(0.22, 1, 0.36, 1) 0.15s forwards;
  opacity: 0;
}

.logo-icon {
  font-size: 22px;
}

.logo-text {
  font-size: 17px;
  font-weight: 700;
  color: var(--primary-purple);
  letter-spacing: 0.02em;
}

.navbar-menu {
  display: flex;
  gap: 8px;
  flex: 1;
  justify-content: center;
  animation: navItemFadeIn 0.4s cubic-bezier(0.22, 1, 0.36, 1) 0.25s forwards;
  opacity: 0;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all var(--transition-fast);
  position: relative;
  overflow: hidden;
  font-size: 15px;
  font-weight: 500;
  font-family: var(--font-heading);
}

.menu-item:nth-child(1) { animation: menuItemFadeIn 0.35s cubic-bezier(0.22, 1, 0.36, 1) 0.4s forwards; opacity: 0; }
.menu-item:nth-child(2) { animation: menuItemFadeIn 0.35s cubic-bezier(0.22, 1, 0.36, 1) 0.48s forwards; opacity: 0; }

@keyframes menuItemFadeIn {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.menu-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  transition: left var(--transition-base);
}

.menu-item:hover::before {
  left: 100%;
}

.menu-item:hover {
  color: var(--primary-purple);
  background: var(--bg-overlay);
}

.menu-item.active {
  color: var(--primary-purple);
  background: rgba(6, 182, 212, 0.12);
  font-weight: 600;
}

.menu-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 70%;
  height: 3px;
  border-radius: 3px 3px 0 0;
  box-shadow: 0 -1px 2px rgba(6, 182, 212, 0.30);
}

.menu-icon {
  font-size: 14px;
}

.navbar-user {
  display: flex;
  align-items: center;
  animation: navItemFadeIn 0.4s cubic-bezier(0.22, 1, 0.36, 1) 0.35s forwards;
  opacity: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  color: var(--text-primary);
  font-weight: 500;
}

.logout-btn {
  color: var(--text-secondary);
}

.logout-btn:hover {
  color: var(--primary-purple);
}

.login-btn {
  background: var(--primary-purple);
  border-color: var(--primary-purple);
  color: var(--text-white);
}

.login-btn:hover {
  background: var(--primary-purple-dark);
  border-color: var(--primary-purple-dark);
}

/* 导航栏下 1px 毛玻璃装饰线 */
.navbar-decoration {
  height: 1px;
  background: rgba(6, 182, 212, 0.5);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  opacity: 0.9;
}

/* 主内容区 */
.main-content {
  min-height: calc(100vh - 52px);
  padding: 0;
  max-width: 100%;
  margin: 0 auto;
}

/* 页面过渡动画 */
.page-enter-active,
.page-leave-active {
  transition: all var(--transition-base) cubic-bezier(0.4, 0, 0.2, 1);
}

.page-enter-from {
  opacity: 0;
  transform: translateX(30px) scale(0.98);
}

.page-leave-to {
  opacity: 0;
  transform: translateX(-30px) scale(0.98);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-base);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.loading-placeholder {
  padding: 40px;
  text-align: center;
  color: var(--text-secondary);
}

.loading-placeholder p {
  margin: 8px 0;
}
</style>

