<template>
  <div class="courtroom-page" @mousemove="handleMouseMove" @mouseleave="handleMouseLeave">
    <!-- 左侧边栏 -->
    <div 
      class="sidebar" 
      :class="{ 'sidebar-visible': sidebarVisible }"
      @mouseenter="sidebarVisible = true"
      @mouseleave="handleSidebarLeave"
    >
      <div class="sidebar-content">
        <!-- 返回按钮 -->
        <div class="sidebar-item sidebar-header" @click="goHome">
          <span class="sidebar-icon">←</span>
          <span class="sidebar-text">返回首页</span>
        </div>
        
        <div class="sidebar-divider"></div>
        
        <!-- 庭前准备 -->
        <div class="sidebar-section">
          <div 
            class="sidebar-item" 
            :class="{ 'active': activeTab === 'pretrial' }"
            @click="navigateToTab('pretrial')"
          >
            <span class="sidebar-icon">📋</span>
            <span class="sidebar-text">庭前准备</span>
          </div>
          <div 
            v-if="activeTab === 'pretrial'"
            class="sidebar-submenu"
          >
            <div 
              class="sidebar-subitem"
              :class="{ 'active': pretrialSubTab === 'basic' }"
              @click="navigateToSubTab('basic')"
            >
              <span class="sidebar-text">基本信息</span>
            </div>
            <div 
              class="sidebar-subitem"
              :class="{ 'active': pretrialSubTab === 'strategy' }"
              @click="navigateToSubTab('strategy')"
            >
              <span class="sidebar-text">诉讼策略</span>
            </div>
          </div>
        </div>
        
        <!-- 庭中辩论 -->
        <div 
          class="sidebar-item" 
          :class="{ 
            'active': activeTab === 'debate',
            'disabled': isStepDisabled('debate')
          }"
          @click="navigateToTab('debate')"
        >
          <span class="sidebar-icon">⚖️</span>
          <span class="sidebar-text">庭中辩论</span>
          <span v-if="isStepDisabled('debate')" class="lock-icon">🔒</span>
        </div>
        
        <!-- 庭后宣判 -->
        <div 
          class="sidebar-item" 
          :class="{ 
            'active': activeTab === 'verdict',
            'disabled': isStepDisabled('verdict')
          }"
          @click="navigateToTab('verdict')"
        >
          <span class="sidebar-icon">📜</span>
          <span class="sidebar-text">庭后宣判</span>
          <span v-if="isStepDisabled('verdict')" class="lock-icon">🔒</span>
        </div>
      </div>
    </div>
    
    <!-- 主内容区 -->
    <div class="courtroom-wrapper">
      <!-- 页面标题 -->
      <div class="page-header fade-in">
        <div class="header-content">
          <div class="header-left">
            <h1 class="page-title">
              <span class="title-icon">⚖️</span>
              <span class="title-text">模拟法庭</span>
            </h1>
            <p class="page-subtitle">智能诉讼审判模拟系统</p>
          </div>
          <el-button
            type="warning"
            size="default"
            class="reset-btn"
            @click="handleReset"
            :icon="Refresh"
          >
            重置
          </el-button>
        </div>
      </div>
      
      <!-- 顶部导航标签 -->
      <div class="nav-tabs slide-in-right">
        <div
          v-for="tab in tabs"
          :key="tab.key"
          class="nav-tab"
          :class="{ 
            'active': activeTab === tab.key,
            'disabled': isStepDisabled(tab.key)
          }"
          @click="navigateToTab(tab.key)"
        >
          <span class="tab-icon">{{ tab.icon }}</span>
          <span class="tab-text">{{ tab.name }}</span>
          <span v-if="isStepDisabled(tab.key)" class="tab-lock">🔒</span>
          <div class="tab-indicator"></div>
        </div>
      </div>

      <!-- 内容区域 -->
      <div class="content-area fade-in">
        <PreTrial 
          v-if="activeTab === 'pretrial'" 
          ref="preTrialRef"
          :active-sub-tab="pretrialSubTab"
          @update:active-sub-tab="pretrialSubTab = $event"
          @complete="completeStep('pretrial')"
        />
        <Debate 
          v-else-if="activeTab === 'debate'" 
          @complete="completeStep('debate')"
        />
        <Verdict v-else-if="activeTab === 'verdict'" />
      </div>
    </div>
    
    <!-- 回到顶部按钮 -->
    <transition name="fade">
      <div 
        v-show="showBackToTop" 
        class="back-to-top" 
        @click="scrollToTop"
      >
        <span class="back-icon">↑</span>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import PreTrial from '@/components/PreTrial.vue'
import Debate from '@/components/Debate.vue'
import Verdict from '@/components/Verdict.vue'
import { useCaseStore } from '@/stores/case'

const route = useRoute()
const router = useRouter()
const caseStore = useCaseStore()
const activeTab = ref('pretrial')
const pretrialSubTab = ref('basic')
const preTrialRef = ref(null)

// 流程步骤定义
const steps = [
  { key: 'pretrial', name: '庭前准备', icon: '📋', order: 1 },
  { key: 'debate', name: '庭中辩论', icon: '⚖️', order: 2 },
  { key: 'verdict', name: '庭后宣判', icon: '📜', order: 3 }
]

const tabs = steps

// 流程状态管理
const getStepStatus = () => {
  try {
    if (typeof localStorage === 'undefined') {
      return { pretrial: false, debate: false, verdict: false }
    }
    const status = localStorage.getItem('courtroomStepStatus')
    if (status) {
      try {
        return JSON.parse(status)
      } catch {
        return { pretrial: false, debate: false, verdict: false }
      }
    }
    return { pretrial: false, debate: false, verdict: false }
  } catch (e) {
    console.error('获取步骤状态失败:', e)
    return { pretrial: false, debate: false, verdict: false }
  }
}

// 先定义保存函数
const saveStepStatus = () => {
  try {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('courtroomStepStatus', JSON.stringify(stepStatus.value))
    }
  } catch (e) {
    console.error('保存步骤状态失败:', e)
  }
}

// 然后初始化状态
const stepStatus = ref(getStepStatus())

// 初始化：庭前准备总是可访问的
if (!stepStatus.value.pretrial) {
  stepStatus.value.pretrial = true
  saveStepStatus()
}

// 完成当前步骤，解锁下一步
const completeStep = (stepKey) => {
  stepStatus.value[stepKey] = true
  saveStepStatus()
  
  // 解锁下一步
  const currentStep = steps.find(s => s.key === stepKey)
  if (currentStep) {
    const nextStep = steps.find(s => s.order === currentStep.order + 1)
    if (nextStep) {
      stepStatus.value[nextStep.key] = true
      saveStepStatus()
    }
  }
}

// 检查步骤是否可访问
const canAccessStep = (stepKey) => {
  return stepStatus.value[stepKey] === true
}

// 获取步骤的禁用状态
const isStepDisabled = (stepKey) => {
  return !canAccessStep(stepKey)
}

// 侧栏显示状态
const sidebarVisible = ref(false)
const sidebarTimer = ref(null)

// 鼠标移动处理
const handleMouseMove = (event) => {
  if (event.clientX < 50) {
    sidebarVisible.value = true
    if (sidebarTimer.value) {
      clearTimeout(sidebarTimer.value)
      sidebarTimer.value = null
    }
  }
}

// 鼠标离开页面
const handleMouseLeave = () => {
  sidebarTimer.value = setTimeout(() => {
    sidebarVisible.value = false
  }, 300)
}

// 鼠标离开侧栏
const handleSidebarLeave = () => {
  sidebarTimer.value = setTimeout(() => {
    sidebarVisible.value = false
  }, 300)
}

// 导航到主标签
const navigateToTab = (tab) => {
  // 检查是否可以访问该步骤
  if (!canAccessStep(tab)) {
    const step = steps.find(s => s.key === tab)
    const currentStep = steps.find(s => stepStatus.value[s.key] && !stepStatus.value[steps.find(ss => ss.order === s.order + 1)?.key])
    if (currentStep) {
      ElMessage.warning(`请先完成"${currentStep.name}"，才能进入"${step?.name}"`)
    } else {
      ElMessage.warning(`请按顺序完成流程，当前无法访问"${step?.name}"`)
    }
    return
  }
  
  activeTab.value = tab
  if (tab === 'pretrial') {
    pretrialSubTab.value = 'basic'
  }
}

// 导航到子标签
const navigateToSubTab = (subTab) => {
  if (activeTab.value === 'pretrial') {
    pretrialSubTab.value = subTab
    if (preTrialRef.value) {
      preTrialRef.value.setActiveTab(subTab)
    }
  }
}

// 回到顶部按钮显示状态
const showBackToTop = ref(false)

// 监听滚动
const handleScroll = () => {
  showBackToTop.value = window.scrollY > 300
}

// 回到顶部
const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

// 返回首页
const goHome = () => {
  router.push({ name: 'home' })
}

// 重置模拟法庭
const handleReset = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重置模拟法庭吗？这将清除所有当前进度和数据，包括：\n' +
      '• 庭前准备的所有步骤\n' +
      '• 庭中辩论的对话记录\n' +
      '• 庭后宣判的判决书\n' +
      '• 案件信息和文件列表',
      '确认重置',
      {
        confirmButtonText: '确定重置',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: false
      }
    )
    
    // 清除localStorage中的状态
    try {
      localStorage.removeItem('courtroomStepStatus')
      localStorage.removeItem('pretrialStepStatus')
      localStorage.removeItem('debateMessages')
      localStorage.removeItem('debateCompleted')
    } catch (e) {
      console.error('清除localStorage失败:', e)
    }
    
    // 重置Pinia store
    caseStore.reset()
    
    // 重置页面状态
    stepStatus.value = { pretrial: false, debate: false, verdict: false }
    activeTab.value = 'pretrial'
    pretrialSubTab.value = 'basic'
    
    // 重新初始化：庭前准备总是可访问的
    stepStatus.value.pretrial = true
    saveStepStatus()
    
    ElMessage.success('模拟法庭已重置，已返回初始状态')
    
    // 刷新页面以确保所有组件重新初始化
    // 使用nextTick确保状态更新后再刷新
    await nextTick()
    window.location.reload()
  } catch (error) {
    // 用户取消操作
    if (error !== 'cancel') {
      console.error('重置失败:', error)
      ElMessage.error('重置失败，请重试')
    }
  }
}

// 定期检查辩论是否完成的定时器
let debateCheckInterval = null

// 如果路由中有tab参数，切换到对应标签
onMounted(() => {
  try {
    if (route.query.tab) {
      const tab = route.query.tab
      if (canAccessStep(tab)) {
        activeTab.value = tab
      } else {
        ElMessage.warning('无法访问该步骤，请按顺序完成流程')
      }
    }
    window.addEventListener('scroll', handleScroll)
    
    // 监听Debate组件的完成事件（通过localStorage）
    const checkDebateComplete = () => {
      try {
        const debateCompleted = localStorage.getItem('debateCompleted')
        if (debateCompleted === 'true' && !stepStatus.value.debate) {
          completeStep('debate')
        }
      } catch (e) {
        console.error('检查辩论完成状态失败:', e)
      }
    }
    
    // 定期检查辩论是否完成
    debateCheckInterval = setInterval(checkDebateComplete, 1000)
  } catch (e) {
    console.error('Courtroom页面初始化失败:', e)
  }
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  if (sidebarTimer.value) {
    clearTimeout(sidebarTimer.value)
  }
  if (debateCheckInterval) {
    clearInterval(debateCheckInterval)
    debateCheckInterval = null
  }
})
</script>

<style scoped>
.courtroom-page {
  width: 100%;
  min-height: calc(100vh - 64px);
  background: var(--bg-secondary);
  position: relative;
  padding: 0;
}

/* 左侧边栏 */
.sidebar {
  position: fixed;
  left: 0;
  top: 40px;
  height: calc(100vh - 40px);
  width: 80px;
  background: var(--bg-primary);
  box-shadow: var(--shadow-lg);
  transform: translateX(-100%);
  transition: transform var(--transition-base);
  z-index: 100;
  border-right: 1px solid var(--border-color);
}

.sidebar-visible {
  transform: translateX(0);
}

.sidebar-content {
  padding: 8px 0;
  height: 100%;
  overflow-y: auto;
}

.sidebar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px 4px;
  cursor: pointer;
  transition: all var(--transition-fast);
  color: var(--text-primary);
  position: relative;
  font-size: var(--font-size-xs);
  text-align: center;
}

.sidebar-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--primary-purple);
  transform: scaleY(0);
  transition: transform var(--transition-fast);
}

.sidebar-item:hover {
  background: var(--bg-overlay);
  color: var(--primary-purple);
}

.sidebar-item.active {
  background: var(--bg-overlay);
  color: var(--primary-purple);
  font-weight: 600;
}

.sidebar-item.active::before {
  transform: scaleY(1);
}

.sidebar-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: auto;
}

.sidebar-item.disabled:hover {
  background: var(--bg-primary);
  color: var(--text-primary);
}

.lock-icon {
  font-size: 10px;
  margin-top: 2px;
}

.sidebar-header {
  font-weight: 600;
  margin-bottom: 8px;
}

.sidebar-icon {
  font-size: 16px;
  width: auto;
  text-align: center;
}

.sidebar-text {
  font-size: 10px;
  font-weight: 500;
  line-height: 1.2;
}

.sidebar-divider {
  height: 1px;
  background: var(--border-color);
  margin: 6px 8px;
}

.sidebar-section {
  margin-bottom: 8px;
}

.sidebar-submenu {
  padding-left: 0;
  margin-top: 2px;
}

.sidebar-subitem {
  padding: 6px 4px;
  font-size: 9px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
  text-align: center;
}

.sidebar-subitem::before {
  content: '';
  position: absolute;
  left: 4px;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--text-tertiary);
  transition: all var(--transition-fast);
}

.sidebar-subitem:hover {
  color: var(--primary-purple);
  background: var(--bg-secondary);
}

.sidebar-subitem.active {
  color: var(--primary-purple);
  font-weight: 500;
}

.sidebar-subitem.active::before {
  background: var(--primary-purple);
  width: 5px;
  height: 5px;
}

/* 主内容区 */
.courtroom-wrapper {
  margin-left: 0;
  padding: 16px;
  max-width: 100%;
  margin: 0 auto;
  transition: margin-left var(--transition-base);
  width: 100%;
}

/* 页面标题 */
.page-header {
  margin-bottom: 16px;
  padding: 16px 20px;
  background: linear-gradient(135deg, var(--primary-purple) 0%, var(--primary-purple-light) 100%);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  position: relative;
  overflow: hidden;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 1;
}

.header-left {
  flex: 1;
  text-align: center;
}

.reset-btn {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  color: var(--text-white);
  font-weight: 500;
  backdrop-filter: blur(10px);
  transition: all var(--transition-base);
}

.reset-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.page-header::before {
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

.page-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
}

.title-icon {
  font-size: 20px;
  animation: float 3s ease-in-out infinite;
}

.title-text {
  font-size: 16px;
  font-weight: bold;
  color: var(--text-white);
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.page-subtitle {
  font-size: 11px;
  color: var(--text-white);
  opacity: 0.9;
  margin: 0;
  position: relative;
  z-index: 1;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}

/* 导航标签 */
.nav-tabs {
  display: flex;
  gap: 6px;
  margin-bottom: 16px;
  background: var(--bg-primary);
  padding: 4px;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
}

.nav-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 5px 10px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  color: var(--text-secondary);
  position: relative;
  font-weight: 500;
  font-size: var(--font-size-sm);
}

.nav-tab:hover {
  background: var(--bg-overlay);
  color: var(--primary-purple);
  transform: translateY(-2px);
}

.nav-tab.active {
  background: linear-gradient(135deg, var(--primary-purple), var(--primary-purple-light));
  color: var(--text-white);
  box-shadow: var(--shadow-md);
}

.nav-tab.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: auto;
}

.nav-tab.disabled:hover {
  background: var(--bg-primary);
  color: var(--text-secondary);
  transform: none;
}

.tab-lock {
  font-size: 10px;
  margin-left: 4px;
}

.tab-icon {
  font-size: 12px;
}

.tab-text {
  font-size: var(--font-size-xs);
}

.tab-indicator {
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  height: 3px;
  background: var(--text-white);
  border-radius: 2px;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.nav-tab.active .tab-indicator {
  opacity: 1;
}

/* 内容区域 */
.content-area {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: 16px;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-color);
  min-height: 300px;
  width: 100%;
}

/* 回到顶部按钮 */
.back-to-top {
  position: fixed;
  right: 32px;
  bottom: 32px;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-purple), var(--primary-purple-light));
  color: var(--text-white);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: var(--shadow-lg);
  transition: all var(--transition-base);
  z-index: 1000;
  border: 2px solid var(--bg-primary);
}

.back-to-top:hover {
  transform: translateY(-5px) scale(1.1);
  box-shadow: var(--shadow-xl);
}

.back-icon {
  font-size: 24px;
  font-weight: bold;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-base);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
