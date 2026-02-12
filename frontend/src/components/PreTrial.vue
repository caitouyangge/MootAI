<template>
  <div class="pretrial-container">
    <!-- 步骤导航 -->
    <div class="steps-nav">
      <div
        v-for="(step, index) in steps"
        :key="step.key"
        class="step-item"
        :class="{
          'active': currentStep === step.key,
          'completed': stepStatus[step.key],
          'disabled': !canAccessStep(step.key)
        }"
        @click="navigateToStep(step.key)"
      >
        <div class="step-number">
          <span v-if="stepStatus[step.key]" class="step-check">✓</span>
          <span v-else>{{ index + 1 }}</span>
        </div>
        <div class="step-label">{{ step.label }}</div>
        <div v-if="!canAccessStep(step.key)" class="step-lock">🔒</div>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="content-area">
      <!-- 步骤1：选择身份 -->
      <div v-if="currentStep === 'identity'" class="step-content">
        <div class="step-header">
          <h3 class="step-title">步骤1：选择身份</h3>
          <p class="step-desc">请选择您在本次模拟中的身份角色</p>
        </div>
        <div class="identity-selector">
          <div
            class="identity-option"
            :class="{ 'active': selectedIdentity === 'plaintiff' }"
            @click="selectIdentity('plaintiff')"
          >
            <div class="option-icon">👨‍⚖️</div>
            <div class="option-label">原告</div>
            <div class="option-desc">提起诉讼的一方</div>
          </div>
          <div
            class="identity-option"
            :class="{ 'active': selectedIdentity === 'defendant' }"
            @click="selectIdentity('defendant')"
          >
            <div class="option-icon">⚖️</div>
            <div class="option-label">被告</div>
            <div class="option-desc">被起诉的一方</div>
          </div>
        </div>
        <div v-if="selectedIdentity" class="step-actions">
          <el-button type="primary" @click="completeStep('identity')">
            确认并继续
          </el-button>
        </div>
      </div>

      <!-- 步骤2：上传案件资料 -->
      <div v-else-if="currentStep === 'upload'" class="step-content">
        <div class="step-header">
          <h3 class="step-title">步骤2：上传案件资料</h3>
          <p class="step-desc">请上传与案件相关的文件资料</p>
        </div>
        <div class="upload-section">
          <div 
            class="upload-area" 
            @click="triggerUpload" 
            @drop.prevent="handleDrop"
            @dragover.prevent="isDragging = true"
            @dragenter.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            :class="{ 
              'has-files': fileList.length > 0,
              'dragging': isDragging
            }"
          >
            <input
              ref="fileInput"
              type="file"
              multiple
              style="display: none"
              @change="handleFileChange"
            />
            <div v-if="fileList.length === 0" class="upload-placeholder">
              <div class="upload-icon">📤</div>
              <p class="upload-text">点击或拖拽文件到此处上传</p>
              <p class="upload-hint">支持多个文件同时上传</p>
            </div>
            <div v-else class="file-preview">
              <div class="file-count">{{ fileList.length }} 个文件</div>
              <div class="file-list">
                <div
                  v-for="(file, index) in fileList"
                  :key="index"
                  class="file-tag"
                  :class="{ 'uploading': file.uploading, 'uploaded': file.uploaded }"
                >
                  <span class="file-icon">📄</span>
                  <span class="file-name">{{ file.name }}</span>
                  <span v-if="file.uploading" class="upload-status">上传中...</span>
                  <span v-else-if="file.uploaded" class="upload-status">✓</span>
                  <el-button
                    text
                    size="small"
                    @click.stop="removeFile(index)"
                    class="remove-btn"
                  >
                    ×
                  </el-button>
                </div>
              </div>
            </div>
          </div>
          <el-button
            v-if="fileList.length > 0"
            text
            size="small"
            @click="clearAllFiles"
            class="clear-btn"
          >
            清空所有文件
          </el-button>
        </div>
        <div v-if="fileList.length > 0" class="step-actions">
          <el-button type="primary" @click="completeStep('upload')">
            确认并继续
          </el-button>
        </div>
      </div>

      <!-- 步骤3：生成案件描述 -->
      <div v-else-if="currentStep === 'description'" class="step-content">
        <div class="step-header">
          <h3 class="step-title">步骤3：生成案件描述</h3>
          <p class="step-desc">系统将基于您上传的文件自动生成案件描述</p>
        </div>
        <div class="description-section">
          <el-button
            v-if="!caseDescription"
            type="primary"
            :loading="generating"
            @click="generateDescription"
            class="generate-btn"
          >
            <span v-if="!generating">🤖 生成案件描述</span>
            <span v-else>正在生成中...</span>
          </el-button>
          <div v-if="caseDescription" class="description-content">
            <el-input
              v-model="caseDescription"
              type="textarea"
              :autosize="{ minRows: 10, maxRows: 20 }"
              placeholder="案件描述将由系统自动生成..."
              class="description-input"
            />
            <div class="description-tip">
              <span class="tip-icon">💡</span>
              <span>您可以编辑上述内容进行调整</span>
            </div>
          </div>
        </div>
        <div v-if="caseDescription" class="step-actions">
          <el-button type="primary" @click="completeStep('description')">
            确认并继续
          </el-button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { ElMessage, ElButton, ElInput } from 'element-plus'
import { useCaseStore } from '@/stores/case'
import request from '@/utils/request'

const emit = defineEmits(['complete'])

const caseStore = useCaseStore()

// 步骤定义
const steps = [
  { key: 'identity', label: '选择身份' },
  { key: 'upload', label: '上传资料' },
  { key: 'description', label: '生成描述' }
]

// 当前步骤
const currentStep = ref('identity')

// 步骤状态
const getStepStatus = () => {
  try {
    if (typeof localStorage === 'undefined') {
      return { identity: false, upload: false, description: false }
    }
    const status = localStorage.getItem('pretrialStepStatus')
    if (status) {
      const parsed = JSON.parse(status)
      // 移除旧的 info 步骤状态
      if (parsed.info !== undefined) {
        delete parsed.info
      }
      return parsed
    }
    return { identity: false, upload: false, description: false }
  } catch {
    return { identity: false, upload: false, description: false }
  }
}

// 初始化步骤状态
const stepStatus = ref(getStepStatus())

// 保存步骤状态函数（在stepStatus定义之后）
const saveStepStatus = () => {
  try {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('pretrialStepStatus', JSON.stringify(stepStatus.value))
    }
  } catch (e) {
    console.error('保存步骤状态失败:', e)
  }
}

// 初始化：第一步总是可访问
if (!stepStatus.value.identity) {
  stepStatus.value.identity = true
  saveStepStatus()
}

// 检查步骤是否可访问
const canAccessStep = (stepKey) => {
  return stepStatus.value[stepKey] === true
}

// 导航到步骤
const navigateToStep = (stepKey) => {
  if (!canAccessStep(stepKey)) {
    ElMessage.warning('请按顺序完成前面的步骤')
    return
  }
  currentStep.value = stepKey
}

// 完成步骤
const completeStep = async (stepKey) => {
  stepStatus.value[stepKey] = true
  saveStepStatus()
  
  // 如果是完成步骤3（生成描述），直接完成整个流程
  if (stepKey === 'description') {
    // 所有步骤完成，保存案件信息并触发完成事件
    await saveCase()
    emit('complete')
    ElMessage.success('庭前准备已完成！')
    return
  }
  
  // 解锁下一步
  const currentIndex = steps.findIndex(s => s.key === stepKey)
  if (currentIndex < steps.length - 1) {
    const nextStep = steps[currentIndex + 1]
    stepStatus.value[nextStep.key] = true
    saveStepStatus()
    // 自动跳转到下一步
    currentStep.value = nextStep.key
  } else {
    // 所有步骤完成，保存案件信息并触发完成事件
    await saveCase()
    emit('complete')
    ElMessage.success('庭前准备已完成！')
  }
}

// 保存案件信息
const saveCase = async () => {
  if (!selectedIdentity.value || fileList.value.length === 0 || !caseDescription.value) {
    return
  }
  
  try {
    const fileNames = fileList.value.map(file => file.name)
    const response = await request.post('/cases', {
      identity: selectedIdentity.value,
      fileNames: fileNames,
      caseDescription: caseDescription.value
    })
    
    if (response.code === 200) {
      // 保存成功，可以在这里保存caseId到store或localStorage
      if (response.data && response.data.id) {
        caseStore.setCaseId(response.data.id)
      }
    }
  } catch (error) {
    console.error('保存案件信息失败:', error)
    // 不显示错误，因为用户可能已经可以继续了
  }
}

// 身份选择
const selectedIdentity = ref(caseStore.selectedIdentity || '')

const selectIdentity = (identity) => {
  selectedIdentity.value = identity
  caseStore.setIdentity(identity)
}

// 文件上传
const fileList = ref(caseStore.fileList || [])
const fileInput = ref(null)
const isDragging = ref(false)
const uploading = ref(false)

const triggerUpload = () => {
  fileInput.value?.click()
}

const handleFileChange = async (event) => {
  const files = Array.from(event.target.files)
  await addFiles(files)
  
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const handleDrop = async (event) => {
  isDragging.value = false
  const files = Array.from(event.dataTransfer.files)
  await addFiles(files)
}

const addFiles = async (files) => {
  if (files.length === 0) return
  
  // 先添加到列表并读取文件内容
  for (const file of files) {
    const fileObj = {
      name: file.name,
      raw: file,
      uploading: false,
      uploaded: false,
      content: null // 文件内容
    }
    
    // 尝试读取文件内容（仅文本文件）
    await readFileContent(file, fileObj)
    
    fileList.value.push(fileObj)
  }
  caseStore.setFileList(fileList.value)
  
  // 上传文件
  await uploadFiles()
}

// 读取文件内容
const readFileContent = (file, fileObj) => {
  return new Promise((resolve) => {
    // 检查文件类型
    const fileName = file.name.toLowerCase()
    const textExtensions = ['.txt', '.md', '.json', '.xml', '.html', '.htm', 
                           '.css', '.js', '.java', '.py', '.sql', '.log',
                           '.csv', '.properties', '.yaml', '.yml', '.ini',
                           '.conf', '.config', '.sh', '.bat', '.ps1']
    
    const isTextFile = textExtensions.some(ext => fileName.endsWith(ext))
    const isPdfFile = fileName.endsWith('.pdf')
    
    if (!isTextFile && !isPdfFile) {
      // 非文本文件且非PDF文件，不读取内容（由后端处理）
      fileObj.content = null
      resolve()
      return
    }
    
    if (isPdfFile) {
      // PDF文件由后端解析，前端不读取
      fileObj.content = null
      fileObj.isPdf = true
      resolve()
      return
    }
    
    // 使用FileReader读取文本文件
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        fileObj.content = e.target.result
      } catch (error) {
        console.warn('读取文件内容失败:', file.name, error)
        fileObj.content = null
      }
      resolve()
    }
    reader.onerror = () => {
      console.warn('读取文件内容出错:', file.name)
      fileObj.content = null
      resolve()
    }
    reader.readAsText(file, 'UTF-8')
  })
}

const uploadFiles = async () => {
  if (uploading.value) return
  
  uploading.value = true
  
  try {
    // 找出未上传的文件
    const filesToUpload = fileList.value
      .filter(file => file.raw && !file.uploaded)
      .map(file => file.raw)
    
    if (filesToUpload.length === 0) {
      uploading.value = false
      return
    }
    
    // 标记为上传中
    fileList.value.forEach(file => {
      if (file.raw && !file.uploaded) {
        file.uploading = true
      }
    })
    
    // 创建FormData
    const formData = new FormData()
    filesToUpload.forEach(file => {
      formData.append('files', file)
    })
    
    // 上传文件（FormData会自动设置Content-Type，不需要手动设置）
    const response = await request.post('/cases/upload', formData)
    
    if (response.code === 200) {
      // 标记为已上传
      fileList.value.forEach(file => {
        if (file.raw && !file.uploaded) {
          file.uploading = false
          file.uploaded = true
        }
      })
      caseStore.setFileList(fileList.value)
      ElMessage.success(`成功上传 ${filesToUpload.length} 个文件`)
    } else {
      throw new Error(response.message || '上传失败')
    }
  } catch (error) {
    console.error('文件上传失败:', error)
    ElMessage.error(error.response?.data?.message || error.message || '文件上传失败，请重试')
    
    // 标记上传失败
    fileList.value.forEach(file => {
      if (file.uploading) {
        file.uploading = false
      }
    })
  } finally {
    uploading.value = false
  }
}

const removeFile = (index) => {
  fileList.value.splice(index, 1)
  caseStore.setFileList(fileList.value)
  ElMessage.info('文件已移除')
}

const clearAllFiles = () => {
  if (fileList.value.length === 0) return
  fileList.value = []
  caseStore.setFileList([])
  ElMessage.success('已清空所有文件')
}

// 生成案件描述
const caseDescription = ref(caseStore.caseDescription || '')
const generating = ref(false)

const generateDescription = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先上传文件')
    return
  }
  
  if (!selectedIdentity.value) {
    ElMessage.warning('请先选择身份')
    return
  }
  
  // 检查是否有未上传的文件
  const hasUnuploadedFiles = fileList.value.some(file => file.raw && !file.uploaded)
  if (hasUnuploadedFiles) {
    ElMessage.warning('请先完成文件上传')
    await uploadFiles()
    // 再次检查
    const stillUnuploaded = fileList.value.some(file => file.raw && !file.uploaded)
    if (stillUnuploaded) {
      return
    }
  }
  
  generating.value = true
  ElMessage.info('正在分析文件，生成案件描述...')
  
  try {
    const fileNames = fileList.value.map(file => file.name)
    // 收集文件内容（仅包含有内容的文件）
    const fileContents = fileList.value
      .filter(file => file.content != null && file.content.trim() !== '')
      .map(file => `文件名: ${file.name}\n内容:\n${file.content}`)
    
    // 案件总结可能需要较长时间，设置60秒超时
    const response = await request.post('/cases/summarize', {
      fileNames: fileNames,
      fileContents: fileContents.length > 0 ? fileContents : undefined,
      identity: selectedIdentity.value
    }, {
      timeout: 90000 // 90秒超时，适应AI处理大文件的情况
    })
    
    if (response.code === 200 && response.data) {
      caseDescription.value = response.data
      caseStore.setCaseDescription(response.data)
      ElMessage.success('案件描述已生成')
    } else {
      throw new Error(response.message || '生成案件描述失败')
    }
  } catch (error) {
    console.error('生成案件描述失败:', error)
    // 处理超时错误
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      ElMessage.warning('请求超时，AI服务可能正在处理中。请稍后刷新页面查看结果，或重新尝试生成。')
    } else {
      ElMessage.error(error.response?.data?.message || error.message || '生成案件描述失败，请重试')
    }
  } finally {
    generating.value = false
  }
}

// 监听案件描述变化
watch(caseDescription, (newVal) => {
  if (newVal) {
    caseStore.setCaseDescription(newVal)
  }
})

// 组件挂载时，如果有已完成的步骤，跳转到第一个未完成的步骤
onMounted(() => {
  const firstIncompleteStep = steps.find(step => !stepStatus.value[step.key])
  if (firstIncompleteStep) {
    currentStep.value = firstIncompleteStep.key
  } else {
    // 所有步骤都完成了，显示最后一步
    currentStep.value = steps[steps.length - 1].key
    // 如果所有步骤都完成了，触发完成事件
    emit('complete')
  }
})

</script>

<style scoped>
.pretrial-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 步骤导航 */
.steps-nav {
  display: flex;
  gap: 8px;
  background: #f5f7fa;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
}

.step-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  min-width: 100px;
}

.step-item:hover:not(.disabled) {
  background: #ecf5ff;
}

.step-item.active {
  background: #409eff;
  color: white;
}

.step-item.completed {
  background: #67c23a;
  color: white;
}

.step-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: white;
  color: #409eff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
}

.step-item.active .step-number,
.step-item.completed .step-number {
  background: rgba(255, 255, 255, 0.3);
  color: white;
}

.step-check {
  font-size: 18px;
}

.step-label {
  font-size: 12px;
  font-weight: 500;
  text-align: center;
}

.step-lock {
  font-size: 12px;
  margin-top: 4px;
}

/* 内容区域 */
.content-area {
  background: transparent;
  border-radius: 0;
  padding: 0;
}

.step-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.step-header {
  text-align: center;
  margin-bottom: 20px;
}

.step-title {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin: 0 0 8px 0;
}

.step-desc {
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* 身份选择 */
.identity-selector {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin: 20px 0;
}

.identity-option {
  padding: 24px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
}

.identity-option:hover {
  border-color: #409eff;
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.identity-option.active {
  border-color: #409eff;
  background: #ecf5ff;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
}

.option-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.option-label {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.option-desc {
  font-size: 14px;
  color: #666;
}

/* 文件上传 */
.upload-section {
  margin: 20px 0;
}

.upload-area {
  min-height: 200px;
  border: 2px dashed #e0e0e0;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #fafafa;
  margin-bottom: 12px;
}

.upload-area:hover {
  border-color: #409eff;
  background: #f0f9ff;
}

.upload-area.dragging {
  border-color: #409eff;
  background: #e6f7ff;
  border-style: solid;
}

.upload-area.has-files {
  border-style: solid;
  border-color: #409eff;
  background: white;
  padding: 24px;
  min-height: auto;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.upload-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.upload-text {
  font-size: 16px;
  color: #333;
  margin: 0 0 8px 0;
  font-weight: 500;
}

.upload-hint {
  font-size: 14px;
  color: #999;
  margin: 0;
}

.file-preview {
  width: 100%;
}

.file-count {
  font-size: 14px;
  color: #666;
  margin-bottom: 12px;
  font-weight: 500;
}

.file-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.file-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f5f7fa;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
}

.file-tag.uploading {
  background: #fff7e6;
  border-color: #ffc53d;
}

.file-tag.uploaded {
  background: #f6ffed;
  border-color: #95de64;
}

.upload-status {
  font-size: 12px;
  color: #666;
  margin-left: 4px;
}

.file-icon {
  font-size: 16px;
}

.file-name {
  color: #333;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-btn {
  padding: 0;
  min-width: auto;
  width: 20px;
  height: 20px;
  color: #999;
  font-size: 18px;
}

.remove-btn:hover {
  color: #f56c6c;
}

.clear-btn {
  color: #999;
}

.clear-btn:hover {
  color: #f56c6c;
}

/* 案件描述 */
.description-section {
  margin: 20px 0;
}

.generate-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  margin-bottom: 20px;
}

.description-content {
  margin-top: 20px;
}

.description-input {
  width: 100%;
  margin-bottom: 12px;
}

.description-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #f0f9ff;
  border-radius: 6px;
  font-size: 14px;
  color: #409eff;
}

.tip-icon {
  font-size: 16px;
}

/* 步骤操作按钮 */
.step-actions {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}

.step-actions .el-button {
  min-width: 150px;
  height: 40px;
  font-size: 16px;
}

/* 子导航 */
.sub-nav-tabs {
  display: flex;
  gap: 8px;
  background: #f5f7fa;
  padding: 8px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.sub-nav-btn {
  flex: 1;
  height: 32px;
  font-size: 12px;
  border-radius: 6px;
}

.sub-nav-btn.active {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border-color: #409eff;
  color: white;
}

/* 统一模块样式 */
.unified-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 基本信息 */
.info-item {
  background: #f5f7fa;
  border-radius: 6px;
  padding: 12px;
  border-left: 3px solid #409eff;
  transition: all 0.3s;
}

.info-item:hover {
  background: #ecf5ff;
  transform: translateX(3px);
}

.info-title {
  font-size: 12px;
  color: #409eff;
  margin: 0 0 8px 0;
  font-weight: 600;
}

.info-content {
  font-size: 12px;
  color: #606266;
  line-height: 1.6;
  white-space: pre-line;
}

/* 诉讼策略 */
.strategy-item {
  border-radius: 6px;
  padding: 12px;
  border-top: 3px solid;
  transition: all 0.3s;
}

.strategy-aggressive {
  background: #fee;
  border-top-color: #f56c6c;
}

.strategy-conservative {
  background: #fffbeb;
  border-top-color: #e6a23c;
}

.strategy-balanced {
  background: #f5f7fa;
  border-top-color: #67c23a;
}

.strategy-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.strategy-title {
  font-size: 12px;
  margin: 0 0 8px 0;
  font-weight: 600;
}

.strategy-aggressive .strategy-title {
  color: #f56c6c;
}

.strategy-conservative .strategy-title {
  color: #e6a23c;
}

.strategy-balanced .strategy-title {
  color: #67c23a;
}

.strategy-content {
  font-size: 12px;
  color: #606266;
  line-height: 1.6;
  white-space: pre-line;
}
</style>
