<template>
  <div class="register-form-overlay" @click.self="$emit('close')">
    <div class="register-form-container">
      <div class="register-form">
        <!-- 装饰背景 -->
        <div class="form-decoration"></div>
        
        <!-- 标题 -->
        <div class="form-header">
          <div class="form-icon form-icon-register" aria-hidden="true"></div>
          <h2 class="form-title">注册</h2>
          <p class="form-subtitle">创建您的账号</p>
        </div>
        
        <!-- 注册表单 -->
        <div class="form-content">
          <el-form :model="registerForm" label-width="0" :rules="rules" ref="formRef">
            <el-form-item prop="username">
              <div class="input-wrapper">
                <span class="input-icon input-icon-user" aria-hidden="true"></span>
                <el-input
                  v-model="registerForm.username"
                  placeholder="请输入用户名（3-50个字符）"
                  class="custom-input"
                  @focus="onUsernameFocus"
                  @blur="onUsernameBlur"
                >
                  <template #suffix>
                    <span
                      v-if="usernameFocused && registerForm.username"
                      class="field-suffix"
                      @click.stop
                    >
                      <span
                        class="suffix-btn clear-btn"
                        title="清空"
                        @click="registerForm.username = ''"
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
                  v-model="registerForm.password"
                  :type="passwordVisible ? 'text' : 'password'"
                  placeholder="请输入密码（至少6个字符）"
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
                        v-if="registerForm.password"
                        class="suffix-btn clear-btn"
                        title="清空"
                        @click="registerForm.password = ''"
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
            <el-form-item prop="confirmPassword">
              <div class="input-wrapper">
                <span class="input-icon input-icon-lock" aria-hidden="true"></span>
                <el-input
                  v-model="registerForm.confirmPassword"
                  :type="confirmPasswordVisible ? 'text' : 'password'"
                  placeholder="请再次输入密码"
                  class="custom-input"
                  @focus="onConfirmPasswordFocus"
                  @blur="onConfirmPasswordBlur"
                >
                  <template #suffix>
                    <span
                      v-if="confirmPasswordFocused"
                      class="field-suffix"
                      @click.stop
                    >
                      <span
                        v-if="registerForm.confirmPassword"
                        class="suffix-btn clear-btn"
                        title="清空"
                        @click="registerForm.confirmPassword = ''"
                      >
                        <el-icon><CircleClose /></el-icon>
                      </span>
                      <span
                        class="suffix-btn password-eye"
                        :title="confirmPasswordVisible ? '隐藏密码' : '显示密码'"
                        @click="toggleConfirmPasswordVisible"
                      >
                        <el-icon><Hide v-if="confirmPasswordVisible" /><View v-else /></el-icon>
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
              @click="handleRegister" 
              :loading="loading" 
              class="register-btn"
            >
              <span v-if="!loading">注册</span>
              <span v-else>注册中...</span>
            </el-button>
          </div>
        </div>
        
        <!-- 底部链接 -->
        <div class="form-footer">
          <span class="login-link" @click="$emit('switch-to-login')">
            已有账号？<span class="link-text">立即登录</span>
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

const emit = defineEmits(['close', 'switch-to-login'])

const router = useRouter()
const formRef = ref(null)

const handleClose = () => {
  emit('close')
}
const loading = ref(false)

const passwordVisible = ref(false)
const confirmPasswordVisible = ref(false)
const usernameFocused = ref(false)
const passwordFocused = ref(false)
const confirmPasswordFocused = ref(false)
let usernameBlurTimer = null
let passwordBlurTimer = null
let confirmPasswordBlurTimer = null
const togglePasswordVisible = () => { passwordVisible.value = !passwordVisible.value }
const toggleConfirmPasswordVisible = () => { confirmPasswordVisible.value = !confirmPasswordVisible.value }
const onUsernameFocus = () => {
  if (usernameBlurTimer) { clearTimeout(usernameBlurTimer); usernameBlurTimer = null }
  usernameFocused.value = true
}
const onUsernameBlur = () => {
  usernameBlurTimer = setTimeout(() => { usernameFocused.value = false; usernameBlurTimer = null }, 150)
}
const onPasswordFocus = () => {
  if (passwordBlurTimer) { clearTimeout(passwordBlurTimer); passwordBlurTimer = null }
  passwordFocused.value = true
}
const onPasswordBlur = () => {
  passwordBlurTimer = setTimeout(() => { passwordFocused.value = false; passwordBlurTimer = null }, 150)
}
const onConfirmPasswordFocus = () => {
  if (confirmPasswordBlurTimer) { clearTimeout(confirmPasswordBlurTimer); confirmPasswordBlurTimer = null }
  confirmPasswordFocused.value = true
}
const onConfirmPasswordBlur = () => {
  confirmPasswordBlurTimer = setTimeout(() => { confirmPasswordFocused.value = false; confirmPasswordBlurTimer = null }, 150)
}

// 注册表单
const registerForm = ref({
  username: '',
  password: '',
  confirmPassword: ''
})

// 表单验证规则
const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.value.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 100, message: '密码长度在 6 到 100 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 注册
const handleRegister = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    const response = await request.post('/auth/register', {
      username: registerForm.value.username,
      password: registerForm.value.password
    })
    
    if (response.code === 200 && response.data) {
      // 保存token和用户信息
      localStorage.setItem('token', response.data.token)
      localStorage.setItem('username', response.data.username)
      localStorage.setItem('userId', response.data.userId)
      
      ElMessage.success('注册成功，已自动登录')
      // 关闭注册窗口
      emit('close')
      // 延迟跳转，确保弹窗关闭动画完成
      setTimeout(() => {
        router.push('/home')
      }, 200)
    } else {
      ElMessage.error(response.message || '注册失败')
    }
  } catch (error) {
    console.error('注册错误:', error)
    ElMessage.error(error.response?.data?.message || error.message || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-form-overlay {
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

.register-form-container {
  width: 360px;
  min-width: 320px;
  max-width: 400px;
}

.register-form {
  background: rgba(255, 255, 255, 0.96);
  border-radius: var(--radius-xl);
  padding: 28px 24px;
  box-shadow: 
    var(--shadow-xl),
    0 0 0 1px rgba(255, 255, 255, 0.6) inset,
    0 32px 64px -12px rgba(6, 182, 212, 0.18);
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(6, 182, 212, 0.12);
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

.form-icon-register {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-purple-light), var(--primary-purple));
  position: relative;
  box-shadow: 0 4px 12px rgba(6, 182, 212, 0.30);
}

.form-icon-register::after {
  content: '+';
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  line-height: 1;
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
}

.register-form :deep(.custom-input .el-input__wrapper) {
  border-radius: var(--radius-lg);
  box-shadow: 0 0 0 1px var(--border-color) inset;
  transition: all var(--transition-fast);
}

.register-form :deep(.custom-input .el-input__suffix:empty) {
  width: 0;
  padding: 0;
  min-width: 0;
  overflow: hidden;
}

.register-form .field-suffix {
  display: inline-flex;
  align-items: center;
}
.register-form .suffix-btn.password-eye {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0 4px;
  transition: color var(--transition-fast);
}
.register-form .suffix-btn.password-eye:hover {
  color: var(--primary-purple);
}
.register-form .suffix-btn.password-eye .el-icon {
  font-size: 16px;
}
.register-form .suffix-btn.clear-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0 2px;
  margin-right: 2px;
  transition: color var(--transition-fast);
}
.register-form .suffix-btn.clear-btn:hover {
  color: var(--primary-purple);
}
.register-form .suffix-btn.clear-btn .el-icon {
  font-size: 14px;
}

.register-form :deep(.custom-input .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--primary-purple-light) inset;
}

.register-form :deep(.custom-input .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px var(--primary-purple) inset;
}

.form-actions {
  margin-top: 20px;
}

.register-btn {
  width: 100%;
  height: 44px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.04em;
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, var(--primary-purple), var(--primary-purple-dark));
  border: none;
  transition: all var(--transition-base);
  box-shadow: 0 4px 14px rgba(6, 182, 212, 0.35);
}

.register-btn:hover {
  background: linear-gradient(135deg, var(--primary-purple-dark), var(--primary-purple));
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(6, 182, 212, 0.40);
}

.register-btn:active {
  transform: translateY(0);
}

.form-footer {
  margin-top: 20px;
  text-align: center;
  position: relative;
  z-index: 1;
}

.login-link {
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: color var(--transition-fast);
  letter-spacing: 0.02em;
}

.login-link:hover {
  color: var(--primary-purple);
}

.link-text {
  color: var(--primary-purple);
  font-weight: 600;
  text-decoration: none;
}
</style>
