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
      
      <!-- 动态装饰线 -->
      <div class="navbar-decoration"></div>
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
import { ElMessage } from 'element-plus'
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
  ElMessage.success('已退出登录')
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
  background: var(--bg-secondary);
}

/* 顶部导航栏 */
.top-navbar {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: var(--bg-primary);
  box-shadow: var(--shadow-md);
  border-bottom: 1px solid var(--border-color);
}

.navbar-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 16px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.navbar-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  user-select: none;
}

.logo-icon {
  font-size: 18px;
  animation: float 3s ease-in-out infinite;
}

.logo-text {
  font-size: 14px;
  font-weight: bold;
  background: linear-gradient(135deg, var(--primary-purple), var(--primary-purple-light));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.navbar-menu {
  display: flex;
  gap: 8px;
  flex: 1;
  justify-content: center;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all var(--transition-fast);
  position: relative;
  overflow: hidden;
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.menu-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.1), transparent);
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
  background: var(--bg-overlay);
  font-weight: 500;
}

.menu-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  height: 3px;
  background: var(--primary-purple);
  border-radius: 2px 2px 0 0;
}

.menu-icon {
  font-size: 12px;
}

.navbar-user {
  display: flex;
  align-items: center;
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

/* 导航栏装饰线 */
.navbar-decoration {
  height: 2px;
  background: linear-gradient(
    90deg,
    transparent,
    var(--primary-purple-light),
    var(--primary-purple),
    var(--primary-purple-light),
    transparent
  );
  background-size: 200% 100%;
  animation: shimmer 3s linear infinite;
}

/* 主内容区 */
.main-content {
  min-height: calc(100vh - 40px);
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

