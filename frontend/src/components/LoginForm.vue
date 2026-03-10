<template>
  <div class="login-form-overlay" @click.self="$emit('close')">
    <div class="login-form-container scale-in">
      <div class="login-form">
        <!-- 关闭按钮 -->
        <div class="close-btn" @click.stop="handleClose">
          <span>×</span>
        </div>
        
        <!-- 装饰背景 -->
        <div class="form-decoration"></div>
        
        <!-- 标题 -->
        <div class="form-header">
          <div class="form-icon form-icon-lock" aria-hidden="true"></div>
          <h2 class="form-title">登录</h2>
          <p class="form-subtitle">欢迎回来</p>
        </div>
        
        <!-- 登录表单 -->
        <div class="form-content">
          <el-form :model="loginForm" label-width="0" :rules="rules" ref="formRef">
            <el-form-item prop="username">
              <div class="input-wrapper">
                <span class="input-icon input-icon-user" aria-hidden="true"></span>
                <el-input
                  v-model="loginForm.username"
                  placeholder="请输入用户名"
                  class="custom-input"
                  @focus="onUsernameFocus"
                  @blur="onUsernameBlur"
                >
                  <template #suffix>
                    <span
                      v-if="usernameFocused && loginForm.username"
                      class="field-suffix"
                      @click.stop
                    >
                      <span
                        class="suffix-btn clear-btn"
                        title="清空"
                        @click="loginForm.username = ''"
                      >
                        <el-icon><CircleClose /></el-icon>
                      </span>
                    </span>
                  </template>
                </el-input>
              </div>
            </el-form-item>
            <el-form-item prop="password">
              <div class="input-wrapper">
                <span class="input-icon input-icon-lock" aria-hidden="true"></span>
                <el-input
                  v-model="loginForm.password"
                  :type="passwordVisible ? 'text' : 'password'"
                  placeholder="请输入密码"
                  class="custom-input"
                  @focus="onPasswordFocus"
                  @blur="onPasswordBlur"
                >
                  <template #suffix>
                    <span
                      v-if="passwordFocused"
                      class="field-suffix"
                      @click.stop
                    >
                      <span
                        v-if="loginForm.password"
                        class="suffix-btn clear-btn"
                        title="清空"
                        @click="loginForm.password = ''"
                      >
                        <el-icon><CircleClose /></el-icon>
                      </span>
                      <span
                        class="suffix-btn password-eye"
                        :title="passwordVisible ? '隐藏密码' : '显示密码'"
                        @click="togglePasswordVisible"
                      >
                        <el-icon><Hide v-if="passwordVisible" /><View v-else /></el-icon>
                      </span>
                    </span>
                  </template>
                </el-input>
              </div>
            </el-form-item>
          </el-form>
          <div class="form-actions">
            <el-button 
              type="primary" 
              @click="handleLogin" 
              :loading="loading" 
              class="login-btn"
            >
              <span v-if="!loading">登录</span>
              <span v-else>登录中...</span>
            </el-button>
          </div>
        </div>
        
        <!-- 底部链接 -->
        <div class="form-footer">
          <span class="register-link" @click="$emit('switch-to-register')">
            还没有账号？<span class="link-text">立即注册</span>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { View, Hide, CircleClose } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { useRouter } from 'vue-router'

const emit = defineEmits(['close', 'switch-to-register'])

const router = useRouter()
const formRef = ref(null)

const handleClose = () => {
  emit('close')
}
const loading = ref(false)

const passwordVisible = ref(false)
const usernameFocused = ref(false)
const passwordFocused = ref(false)
let usernameBlurTimer = null
let passwordBlurTimer = null
const togglePasswordVisible = () => {
  passwordVisible.value = !passwordVisible.value
}
const onUsernameFocus = () => {
  if (usernameBlurTimer) {
    clearTimeout(usernameBlurTimer)
    usernameBlurTimer = null
  }
  usernameFocused.value = true
}
const onUsernameBlur = () => {
  usernameBlurTimer = setTimeout(() => {
    usernameFocused.value = false
    usernameBlurTimer = null
  }, 150)
}
const onPasswordFocus = () => {
  if (passwordBlurTimer) {
    clearTimeout(passwordBlurTimer)
    passwordBlurTimer = null
  }
  passwordFocused.value = true
}
const onPasswordBlur = () => {
  passwordBlurTimer = setTimeout(() => {
    passwordFocused.value = false
    passwordBlurTimer = null
  }, 150)
}

// 登录表单
const loginForm = ref({
  username: '',
  password: ''
})

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ]
}

// 登录
const handleLogin = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    const response = await request.post('/auth/login', {
      username: loginForm.value.username,
      password: loginForm.value.password
    })
    
    if (response.code === 200 && response.data) {
      // 保存token和用户信息
      localStorage.setItem('token', response.data.token)
      localStorage.setItem('username', response.data.username)
      localStorage.setItem('userId', response.data.userId)

      ElMessage.success('登录成功')
      emit('close')
      // 等弹窗关闭动画完成后再跳转，配合路由转场更丝滑
      setTimeout(() => {
        router.push('/home')
      }, 520)
    } else {
      ElMessage.error(response.message || '登录失败')
    }
  } catch (error) {
    console.error('登录错误:', error)
    ElMessage.error(error.response?.data?.message || error.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-form-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.36);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn var(--transition-base);
  pointer-events: auto;
}

.login-form-container {
  width: 360px;
  min-width: 320px;
  max-width: 400px;
}

.login-form {
  background: rgba(255, 255, 255, 0.96);
  border-radius: var(--radius-xl);
  padding: 28px 24px;
  box-shadow: 
    var(--shadow-xl),
    0 0 0 1px rgba(255, 255, 255, 0.6) inset,
    0 32px 64px -12px rgba(139, 92, 246, 0.18);
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(139, 92, 246, 0.12);
}

.form-decoration {
  position: absolute;
  top: -40%;
  right: -30%;
  width: 280px;
  height: 280px;
  background: radial-gradient(circle, var(--primary-purple-lightest) 0%, transparent 65%);
  border-radius: 50%;
  opacity: 0.35;
  animation: float 8s ease-in-out infinite;
  z-index: 0;
}

.close-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 50%;
  transition: all var(--transition-fast);
  z-index: 100;
  pointer-events: auto;
  color: var(--text-secondary);
}

.close-btn:hover {
  background: var(--bg-tertiary);
  color: var(--primary-purple);
  transform: rotate(90deg);
}

.close-btn span {
  font-size: 20px;
  line-height: 1;
  font-weight: 300;
  transition: color var(--transition-fast);
}

.form-header {
  text-align: center;
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
}

.form-icon {
  display: inline-block;
  margin-bottom: 12px;
  animation: float 3s ease-in-out infinite;
}

.form-icon-lock {
  width: 32px;
  height: 32px;
  border: 2px solid var(--primary-purple-light);
  border-radius: 6px;
  position: relative;
  background: linear-gradient(135deg, var(--primary-purple-lightest), #fff);
}

.form-icon-lock::after {
  content: '';
  position: absolute;
  left: 50%;
  top: 6px;
  transform: translateX(-50%);
  width: 10px;
  height: 8px;
  border: 2px solid var(--primary-purple);
  border-bottom: none;
  border-radius: 4px 4px 0 0;
  background: transparent;
}

.form-title {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 6px 0;
  letter-spacing: 0.02em;
  background: linear-gradient(135deg, var(--primary-purple), var(--primary-purple-dark));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.form-subtitle {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
  font-weight: 400;
  letter-spacing: 0.02em;
}

.form-content {
  position: relative;
  z-index: 1;
}

:deep(.el-form-item) {
  margin-bottom: 14px;
}

:deep(.el-input__wrapper) {
  padding: 10px 14px 10px 44px;
  min-height: 44px;
  font-size: 14px;
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
}

:deep(.el-input__inner) {
  font-size: 14px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  z-index: 1;
  color: var(--text-secondary);
  transition: color var(--transition-fast);
}

.input-icon-user {
  width: 18px;
  height: 18px;
  border: 2px solid currentColor;
  border-radius: 50%;
  box-sizing: border-box;
  top: 50%;
  transform: translateY(-50%);
}

.input-icon-user::after {
  content: '';
  position: absolute;
  left: 50%;
  bottom: -6px;
  transform: translateX(-50%);
  width: 8px;
  height: 6px;
  border: 2px solid currentColor;
  border-top: none;
  border-radius: 0 0 4px 4px;
}

.input-icon-lock {
  width: 16px;
  height: 14px;
  border: 2px solid currentColor;
  border-radius: 3px;
  top: 50%;
  transform: translateY(-50%);
  box-sizing: border-box;
}

.input-icon-lock::after {
  content: '';
  position: absolute;
  left: 50%;
  top: -6px;
  transform: translateX(-50%);
  width: 10px;
  height: 6px;
  border: 2px solid currentColor;
  border-bottom: none;
  border-radius: 3px 3px 0 0;
}

:deep(.custom-input .el-input__wrapper) {
  padding-left: 44px;
  border-radius: var(--radius-lg);
  box-shadow: 0 0 0 1px var(--border-color) inset;
  transition: all var(--transition-fast);
}

/* 无内容时 suffix 不占位（与清空按钮行为一致） */
:deep(.custom-input .el-input__suffix:empty) {
  width: 0;
  padding: 0;
  min-width: 0;
  overflow: hidden;
}

.field-suffix {
  display: inline-flex;
  align-items: center;
}
.suffix-btn.password-eye {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0 4px;
  transition: color var(--transition-fast);
}
.suffix-btn.password-eye:hover {
  color: var(--primary-purple);
}
.suffix-btn.password-eye .el-icon {
  font-size: 16px;
}
.suffix-btn.clear-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0 2px;
  margin-right: 2px;
  transition: color var(--transition-fast);
}
.suffix-btn.clear-btn:hover {
  color: var(--primary-purple);
}
.suffix-btn.clear-btn .el-icon {
  font-size: 14px;
}

:deep(.custom-input .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--primary-purple-light) inset;
}

:deep(.custom-input .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px var(--primary-purple) inset;
}

.form-actions {
  margin-top: 20px;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.04em;
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, var(--primary-purple), var(--primary-purple-dark));
  border: none;
  transition: all var(--transition-base);
  box-shadow: 0 4px 14px rgba(139, 92, 246, 0.35);
}

.login-btn:hover {
  background: linear-gradient(135deg, var(--primary-purple-dark), var(--primary-purple));
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.4);
}

.login-btn:active {
  transform: translateY(0);
}

.form-footer {
  margin-top: 20px;
  text-align: center;
  position: relative;
  z-index: 1;
}

.register-link {
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: color var(--transition-fast);
  letter-spacing: 0.02em;
}

.register-link:hover {
  color: var(--primary-purple);
}

.link-text {
  color: var(--primary-purple);
  font-weight: 600;
  text-decoration: none;
}
</style>
