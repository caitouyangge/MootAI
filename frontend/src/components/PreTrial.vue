<template>
  <div class="pretrial-container">

    <!-- ── 步骤导航 Stepper ── -->
    <div class="steps-nav">
      <div class="steps-track">
        <div
          v-for="(step, index) in steps"
          :key="step.key"
          class="step-item"
          :class="{
            'active':    currentStep === step.key,
            'completed': stepStatus[step.key] && currentStep !== step.key,
            'disabled':  !canAccessStep(step.key)
          }"
          @click="navigateToStep(step.key)"
        >
          <div class="step-circle">
            <!-- 未解锁：锁图标 -->
            <svg v-if="!canAccessStep(step.key)" class="step-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 1a4.5 4.5 0 00-4.5 4.5V9H5a2 2 0 00-2 2v6a2 2 0 002 2h10a2 2 0 002-2v-6a2 2 0 00-2-2h-.5V5.5A4.5 4.5 0 0010 1zm3 8V5.5a3 3 0 10-6 0V9h6z" clip-rule="evenodd"/>
            </svg>
            <!-- 已完成：勾选图标 -->
            <svg v-else-if="stepStatus[step.key] && currentStep !== step.key" class="step-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
            <!-- 当前/可访问：数字 -->
            <span v-else class="step-num">{{ index + 1 }}</span>
          </div>
          <div class="step-label">{{ step.label }}</div>
        </div>
      </div>
    </div>

    <!-- ── 步骤内容区域（带淡入切换） ── -->
    <div class="content-area">
      <Transition name="step-fade" mode="out-in">
        <div :key="currentStep" class="step-content">

          <!-- 步骤 1：选择身份 -->
          <template v-if="currentStep === 'identity'">
            <div class="step-header">
              <h3 class="step-title">选择您的身份</h3>
              <p class="step-desc">请选择您在本次模拟庭审中担任的角色</p>
            </div>
            <div class="identity-selector">
              <div
                class="identity-option"
                :class="{ active: selectedIdentity === 'plaintiff' }"
                @click="selectIdentity('plaintiff')"
              >
                <div class="option-icon-wrap">
                  <!-- 公诉人：文书/卷宗图标 -->
                  <svg viewBox="0 0 24 24" class="option-svg" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25"/>
                  </svg>
                </div>
                <div class="option-label">公诉人</div>
                <div class="option-desc">代表国家向被告提起诉讼</div>
                <div class="option-check">
                  <svg viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                  </svg>
                </div>
              </div>
              <div
                class="identity-option"
                :class="{ active: selectedIdentity === 'defendant' }"
                @click="selectIdentity('defendant')"
              >
                <div class="option-icon-wrap">
                  <!-- 辩护人：盾牌图标 -->
                  <svg viewBox="0 0 24 24" class="option-svg" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"/>
                  </svg>
                </div>
                <div class="option-label">辩护人</div>
                <div class="option-desc">为被告提供法律辩护</div>
                <div class="option-check">
                  <svg viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                  </svg>
                </div>
              </div>
            </div>
            <div v-if="selectedIdentity" class="step-actions">
              <el-button type="primary" size="large" @click="completeStep('identity')">
                确认并继续
              </el-button>
            </div>
          </template>

          <!-- 步骤 2：上传案件资料 -->
          <template v-else-if="currentStep === 'upload'">
            <div class="step-header">
              <h3 class="step-title">上传案件资料</h3>
              <p class="step-desc">请上传与案件相关的文件资料，支持多个文件</p>
            </div>
            <div class="upload-section">
              <div
                class="upload-area"
                @click="triggerUpload"
                @drop.prevent="handleDrop"
                @dragover.prevent="handleDragOver"
                @dragenter.prevent="handleDragEnter"
                @dragleave.prevent="handleDragLeave"
                :class="{ 'has-files': fileList.length > 0, 'dragging': isDragging }"
              >
                <input ref="fileInput" type="file" multiple style="display:none" @change="handleFileChange"/>

                <!-- 空状态占位 -->
                <div v-if="fileList.length === 0" class="upload-placeholder">
                  <div class="upload-icon-wrap" :class="{ 'is-dragging': isDragging }">
                    <svg viewBox="0 0 24 24" class="upload-svg" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"/>
                    </svg>
                  </div>
                  <p class="upload-text">{{ isDragging ? '松开即可上传' : '点击或拖拽文件到此处上传' }}</p>
                  <p class="upload-hint">支持 PDF、Word、TXT 等多种格式</p>
                </div>

                <!-- 文件列表 -->
                <div v-else class="file-preview">
                  <div class="file-count-row">
                    <svg viewBox="0 0 20 20" fill="currentColor" class="file-count-icon">
                      <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd"/>
                    </svg>
                    <span>已选择 {{ fileList.length }} 个文件</span>
                  </div>
                  <div class="file-list">
                    <div
                      v-for="(file, index) in fileList"
                      :key="index"
                      class="file-tag"
                      :class="{ uploading: file.uploading, uploaded: file.uploaded }"
                    >
                      <svg viewBox="0 0 20 20" fill="currentColor" class="file-tag-icon">
                        <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd"/>
                      </svg>
                      <span class="file-name">{{ file.name }}</span>
                      <span v-if="file.uploading" class="upload-status-text">上传中…</span>
                      <svg v-else-if="file.uploaded" viewBox="0 0 20 20" fill="currentColor" class="upload-ok-icon">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                      </svg>
                      <button class="remove-btn" @click.stop="removeFile(index)">
                        <svg viewBox="0 0 20 20" fill="currentColor" class="remove-icon">
                          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              <button v-if="fileList.length > 0" class="clear-btn" @click="clearAllFiles">清空所有文件</button>
            </div>
            <div v-if="fileList.length > 0" class="step-actions">
              <el-button type="primary" size="large" @click="completeStep('upload')">确认并继续</el-button>
            </div>
          </template>

          <!-- 步骤 3：生成案件描述 -->
          <template v-else-if="currentStep === 'description'">
            <div class="step-header">
              <h3 class="step-title">生成案件描述</h3>
              <p class="step-desc">AI 将根据您上传的材料自动生成案件描述，您也可以手动编辑</p>
            </div>
            <div class="description-section">
              <!-- 生成按钮 -->
              <button
                v-if="!caseDescription"
                class="generate-btn"
                :class="{ loading: generating }"
                :disabled="generating"
                @click="generateDescription"
              >
                <svg v-if="!generating" viewBox="0 0 24 24" class="gen-icon" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456z"/>
                </svg>
                <span class="gen-spinner" v-if="generating"></span>
                <span>{{ generating ? '正在分析案卷…' : '生成案件描述' }}</span>
              </button>
              <!-- 骨架屏加载 -->
              <div v-if="generating" class="desc-skeleton">
                <div class="sk-line sk-long"></div>
                <div class="sk-line sk-mid"></div>
                <div class="sk-line sk-short"></div>
                <div class="sk-line sk-long"></div>
                <div class="sk-line sk-mid"></div>
                <div class="sk-line sk-short"></div>
              </div>
              <!-- 描述内容 -->
              <div v-if="caseDescription" class="description-content">
                <el-input
                  v-model="caseDescription"
                  type="textarea"
                  :autosize="{ minRows: 10, maxRows: 20 }"
                  placeholder="案件描述将由系统自动生成…"
                  class="description-input"
                />
                <div class="description-tip">
                  <svg viewBox="0 0 20 20" fill="currentColor" class="tip-svg">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
                  </svg>
                  <span>您可以对上述内容进行编辑和调整</span>
                </div>
              </div>
            </div>
            <div v-if="caseDescription" class="step-actions">
              <el-button type="primary" size="large" @click="completeStep('description')">确认并继续</el-button>
            </div>
          </template>

          <!-- 步骤 4：选择审判员类型（卡片化） -->
          <template v-else-if="currentStep === 'judge'">
            <div class="step-header">
              <h3 class="step-title">选择审判员类型</h3>
              <p class="step-desc">请选择在本次模拟庭审中主持的审判员风格</p>
            </div>
            <div class="judge-select-section">
              <div class="judge-grid">
                <div
                  v-for="judge in judgeTypes"
                  :key="judge.value"
                  class="judge-card"
                  :class="{ active: selectedJudgeType === judge.value }"
                  @click="selectedJudgeType = judge.value; onJudgeTypeChange()"
                >
                  <div class="judge-card-label">{{ judge.label }}</div>
                  <div class="judge-card-desc">{{ judge.description }}</div>
                  <div class="judge-check">
                    <svg viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="selectedJudgeType" class="step-actions">
              <el-button type="primary" size="large" @click="completeStep('judge')">确认并继续</el-button>
            </div>
          </template>

          <!-- 步骤 5：选择对方 AI 律师辩论策略 -->
          <template v-else-if="currentStep === 'strategy'">
            <div class="step-header">
              <h3 class="step-title">选择对方辩论策略</h3>
              <p class="step-desc">请选择对方 AI 律师在庭审中采用的辩论策略风格</p>
            </div>
            <div class="strategy-select-section">
              <div class="strategy-options">
                <div
                  v-for="strategy in strategyOptions"
                  :key="strategy.value"
                  class="strategy-option"
                  :class="{ active: selectedOpponentStrategy === strategy.value }"
                  @click="selectStrategy(strategy.value)"
                >
                  <div class="strategy-option-header">
                    <div class="strategy-icon-wrap">
                      <!-- 激进：五角星/冲锋 -->
                      <svg v-if="strategy.value === 'aggressive'" viewBox="0 0 24 24" class="strategy-svg" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"/>
                      </svg>
                      <!-- 保守：盾牌勾 -->
                      <svg v-else-if="strategy.value === 'conservative'" viewBox="0 0 24 24" class="strategy-svg" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"/>
                      </svg>
                      <!-- 均衡：天平 -->
                      <svg v-else-if="strategy.value === 'balanced'" viewBox="0 0 24 24" class="strategy-svg" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v17.25m0 0c-1.472 0-2.882.265-4.185.75M12 20.25c1.472 0 2.882.265 4.185.75M18.75 4.97A48.416 48.416 0 0012 4.5c-2.291 0-4.545.16-6.75.47m13.5 0c1.01.143 2.01.317 3 .52m-3-.52l2.62 10.726c.122.499-.106 1.028-.589 1.202a5.988 5.988 0 01-2.031.352 5.988 5.988 0 01-2.031-.352c-.483-.174-.711-.703-.59-1.202L18.75 4.971zm-16.5.52c.99-.203 1.99-.377 3-.521m0 0l2.62 10.726c.122.499-.106 1.028-.589 1.202a5.989 5.989 0 01-2.031.352 5.989 5.989 0 01-2.031-.352c-.483-.174-.711-.703-.59-1.202L5.25 4.971z"/>
                      </svg>
                      <!-- 防御：纯盾牌 -->
                      <svg v-else viewBox="0 0 24 24" class="strategy-svg" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                      </svg>
                    </div>
                    <div class="strategy-title-text">{{ strategy.label }}</div>
                  </div>
                  <div class="strategy-description">{{ strategy.description }}</div>
                  <div class="strategy-features">
                    <div v-for="feature in strategy.features" :key="feature" class="strategy-feature">
                      <span class="feature-dot"></span>{{ feature }}
                    </div>
                  </div>
                  <div class="strategy-check">
                    <svg viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="selectedOpponentStrategy" class="step-actions">
              <el-button type="primary" size="large" @click="completeStep('strategy')">开始庭审</el-button>
            </div>
          </template>

        </div>
      </Transition>
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
  { key: 'description', label: '生成描述' },
  { key: 'judge', label: '选择审判员' },
  { key: 'strategy', label: '选择策略' }
]

// 当前步骤
const currentStep = ref('identity')

// 步骤状态
const getStepStatus = () => {
  try {
    if (typeof localStorage === 'undefined') {
      return { identity: false, upload: false, description: false, judge: false, strategy: false }
    }
    const status = localStorage.getItem('pretrialStepStatus')
    if (status) {
      const parsed = JSON.parse(status)
      // 移除旧的 info 步骤状态
      if (parsed.info !== undefined) {
        delete parsed.info
      }
      // 确保包含所有步骤
      return {
        identity: parsed.identity || false,
        upload: parsed.upload || false,
        description: parsed.description || false,
        judge: parsed.judge || false,
        strategy: parsed.strategy || false
      }
    }
    return { identity: false, upload: false, description: false, judge: false, strategy: false }
  } catch {
    return { identity: false, upload: false, description: false, judge: false, strategy: false }
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
  
  // 在每一步完成后都尝试保存到数据库（逐步保存）
  // 使用 force=true 允许部分信息保存
  await saveCase(true)
  
  // 如果是完成最后一步（选择策略），直接完成整个流程
  if (stepKey === 'strategy') {
    // 所有步骤完成，再次保存确保所有信息都保存
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

// 保存案件信息到数据库（创建或更新）
const saveCase = async (force = false) => {
  // 如果强制保存，即使信息不完整也保存（用于逐步保存）
  if (!force) {
    // 只有在所有必要信息都完整时才保存
    if (!selectedIdentity.value || fileList.value.length === 0 || !caseDescription.value || !selectedJudgeType.value || !selectedOpponentStrategy.value) {
      return
    }
  }
  
  try {
    const fileNames = fileList.value
      .filter(file => file.uploaded) // 只保存已上传的文件
      .map(file => file.name)
    
    // 如果没有已上传的文件，不保存
    if (fileNames.length === 0 && !force) {
      return
    }
    
    const caseData = {
      identity: selectedIdentity.value || '',
      fileNames: fileNames,
      caseDescription: caseDescription.value || '',
      judgeType: selectedJudgeType.value || '',
      opponentStrategy: selectedOpponentStrategy.value || ''
    }
    
    let response
    if (caseStore.caseId) {
      // 更新现有案件
      response = await request.put(`/cases/${caseStore.caseId}`, caseData)
    } else {
      // 创建新案件
      response = await request.post('/cases', caseData)
    }
    
    if (response.code === 200) {
      // 保存成功，保存caseId到store
      if (response.data && response.data.id) {
        caseStore.setCaseId(response.data.id)
      }
      return true
    } else {
      console.error('保存案件信息失败:', response.message)
      return false
    }
  } catch (error) {
    console.error('保存案件信息失败:', error)
    // 不显示错误，因为用户可能正在填写中
    return false
  }
}

// 身份选择
const selectedIdentity = ref(caseStore.selectedIdentity || '')

const selectIdentity = async (identity) => {
  selectedIdentity.value = identity
  caseStore.setIdentity(identity)
  // 选择身份后，如果有其他信息，保存到数据库
  if (fileList.value.length > 0 || caseDescription.value) {
    await saveCase(true)
  }
}

// 文件上传
const fileList = ref(caseStore.fileList || [])
const fileInput = ref(null)
const isDragging = ref(false)
const uploading = ref(false)
const dragCounter = ref(0) // 用于跟踪拖拽进入/离开次数，避免子元素触发误判

const triggerUpload = () => {
  fileInput.value?.click()
}

const handleFileChange = async (event) => {
  const files = Array.from(event.target.files)
  if (files.length > 0) {
    await addFiles(files)
  }
  
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const handleDragEnter = (event) => {
  event.preventDefault()
  event.stopPropagation()
  dragCounter.value++
  // 检查是否有文件被拖拽
  const hasFiles = event.dataTransfer?.types?.includes('Files') || 
                   (event.dataTransfer?.items && event.dataTransfer.items.length > 0)
  if (hasFiles) {
    isDragging.value = true
  }
}

const handleDragLeave = (event) => {
  event.preventDefault()
  event.stopPropagation()
  dragCounter.value--
  // 只有当计数器归零时才取消拖拽状态
  if (dragCounter.value <= 0) {
    dragCounter.value = 0
    isDragging.value = false
  }
}

const handleDragOver = (event) => {
  event.preventDefault()
  event.stopPropagation()
  // 设置拖拽效果
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'copy'
  }
}

const handleDrop = async (event) => {
  event.preventDefault()
  event.stopPropagation()
  
  // 重置拖拽状态
  isDragging.value = false
  dragCounter.value = 0
  
  // 获取文件
  const files = Array.from(event.dataTransfer?.files || [])
  
  if (files.length > 0) {
    await addFiles(files)
  } else {
    ElMessage.warning('未检测到文件，请重试')
  }
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
  
  // 检查是否已登录
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录后再上传文件')
    // 触发登录弹窗（如果Layout组件支持）
    const event = new CustomEvent('show-login')
    window.dispatchEvent(event)
    return
  }
  
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
      // 文件上传成功后，保存到数据库
      await saveCase(true)
    } else {
      throw new Error(response.message || '上传失败')
    }
  } catch (error) {
    console.error('文件上传失败:', error)
    
    // 处理403错误（未认证）
    if (error.response?.status === 403 || error.response?.status === 401) {
      ElMessage.error('认证失败，请重新登录')
      // 清除可能无效的token
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('userId')
      // 触发登录弹窗
      const event = new CustomEvent('show-login')
      window.dispatchEvent(event)
    } else {
      ElMessage.error(error.response?.data?.message || error.message || '文件上传失败，请重试')
    }
    
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
      // 生成描述后，保存到数据库
      await saveCase(true)
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
watch(caseDescription, async (newVal) => {
  if (newVal) {
    caseStore.setCaseDescription(newVal)
    // 案件描述变化后，保存到数据库（延迟保存，避免频繁请求）
    if (caseStore.caseId) {
      // 使用防抖，避免频繁保存
      clearTimeout(window.caseDescriptionSaveTimer)
      window.caseDescriptionSaveTimer = setTimeout(async () => {
        await saveCase(true)
      }, 1000) // 1秒后保存
    }
  }
})

// 审判员类型
const judgeTypes = ref([
  {
    value: 'professional',
    label: '专业型',
    description: '讲话简洁，业务熟练，判决果断'
  },
  {
    value: 'strong',
    label: '强势型',
    description: '专业能力极度自信，不接受律师的反驳'
  },
  {
    value: 'irritable',
    label: '暴躁型',
    description: '急躁易怒，控制力强，常拍桌训人'
  },
  {
    value: 'lazy',
    label: '偷懒型',
    description: '粗略听案，嫌当事人啰嗦，不重视细节'
  },
  {
    value: 'wavering',
    label: '摇摆型',
    description: '优柔寡断，复杂案件时常左右摇摆'
  },
  {
    value: 'partial',
    label: '偏袒型',
    description: '常替弱者说话，判决会考虑弱者利益'
  },
  {
    value: 'partial-plaintiff',
    label: '偏袒型（公诉人）',
    description: '习惯对公诉人宽容，倾向于支持公诉方'
  },
  {
    value: 'partial-defendant',
    label: '偏袒型（辩护人）',
    description: '习惯对辩护人宽容，倾向于支持辩护方'
  }
])

const selectedJudgeType = ref(caseStore.selectedJudgeType || '')

const onJudgeTypeChange = async () => {
  caseStore.setJudgeType(selectedJudgeType.value)
  // 选择审判员类型后，保存到数据库
  await saveCase(true)
}

const getJudgeLabel = (value) => {
  const judge = judgeTypes.value.find(j => j.value === value)
  return judge ? judge.label : ''
}

const getJudgeDescription = (value) => {
  const judge = judgeTypes.value.find(j => j.value === value)
  return judge ? judge.description : ''
}

// 对方AI律师的辩论策略
const strategyOptions = ref([
  {
    value: 'aggressive',
    label: '激进策略',
    icon: '⚔️',
    description: '采取强硬立场，积极进攻，不轻易让步',
    features: [
      '主动质疑对方证据',
      '强调己方优势',
      '对争议点进行深入辩论',
      '较少妥协'
    ]
  },
  {
    value: 'conservative',
    label: '保守策略',
    icon: '🛡️',
    description: '优先考虑调解，主张温和，可适当让步',
    features: [
      '优先考虑调解解决',
      '主张较为温和',
      '可适当让步',
      '避免过度激化矛盾'
    ]
  },
  {
    value: 'balanced',
    label: '均衡策略',
    icon: '⚖️',
    description: '平衡攻守，主张适中，可协商',
    features: [
      '主张适中',
      '准备充分证据',
      '不过度激化矛盾',
      '保持协商空间'
    ]
  },
  {
    value: 'defensive',
    label: '防御策略',
    icon: '🛡️',
    description: '重点防守，回应对方质疑，保护己方利益',
    features: [
      '重点回应对方质疑',
      '保护己方核心利益',
      '谨慎应对争议点',
      '避免主动进攻'
    ]
  }
])

const selectedOpponentStrategy = ref(caseStore.opponentStrategy || '')

const selectStrategy = async (strategy) => {
  selectedOpponentStrategy.value = strategy
  caseStore.setOpponentStrategy(strategy)
  // 选择策略后，保存到数据库
  await saveCase(true)
}

// 组件挂载时，从数据库加载案件信息
onMounted(async () => {
  // 如果有案件ID，从数据库加载案件信息
  if (caseStore.caseId) {
    console.log('[PreTrial] 从数据库加载案件信息，caseId:', caseStore.caseId)
    const loaded = await caseStore.loadCaseFromDatabase(caseStore.caseId)
    if (loaded) {
      console.log('[PreTrial] 案件信息加载成功')
      // 更新本地状态（从 store 恢复）
      selectedIdentity.value = caseStore.selectedIdentity || ''
      fileList.value = caseStore.fileList || []
      caseDescription.value = caseStore.caseDescription || ''
      selectedJudgeType.value = caseStore.selectedJudgeType || ''
      selectedOpponentStrategy.value = caseStore.opponentStrategy || ''
      
      console.log('[PreTrial] 恢复的数据:', {
        identity: selectedIdentity.value,
        fileCount: fileList.value.length,
        hasDescription: !!caseDescription.value,
        judgeType: selectedJudgeType.value,
        strategy: selectedOpponentStrategy.value
      })
    } else {
      console.warn('[PreTrial] 案件信息加载失败')
    }
  } else {
    console.log('[PreTrial] 没有 caseId，使用 store 中的初始值')
    // 即使没有 caseId，也尝试从 store 恢复（可能来自其他页面）
    selectedIdentity.value = caseStore.selectedIdentity || ''
    fileList.value = caseStore.fileList || []
    caseDescription.value = caseStore.caseDescription || ''
    selectedJudgeType.value = caseStore.selectedJudgeType || ''
    selectedOpponentStrategy.value = caseStore.opponentStrategy || ''
  }
  
  // 检查每个步骤是否真正完成（不仅仅是可访问）
  // 1. identity 步骤：检查是否选择了身份
  const hasIdentity = selectedIdentity.value && selectedIdentity.value !== ''
  
  // 2. upload 步骤：检查是否有上传的文件
  const hasFiles = fileList.value && fileList.value.length > 0
  
  // 3. description 步骤：检查是否有案件描述
  const hasDescription = caseDescription.value && caseDescription.value.trim() !== ''
  
  // 4. judge 步骤：检查是否选择了审判员类型
  const hasJudge = selectedJudgeType.value && selectedJudgeType.value !== ''
  
  // 5. strategy 步骤：检查是否选择了策略
  const hasStrategy = selectedOpponentStrategy.value && selectedOpponentStrategy.value !== ''
  
  // 根据实际完成情况决定显示哪个步骤
  if (!hasIdentity) {
    // 如果还没有选择身份，显示身份选择页面
    currentStep.value = 'identity'
  } else if (!hasFiles) {
    // 如果还没有上传文件，显示上传页面
    currentStep.value = 'upload'
  } else if (!hasDescription) {
    // 如果还没有生成描述，显示描述生成页面
    currentStep.value = 'description'
  } else if (!hasJudge) {
    // 如果还没有选择审判员类型，显示审判员选择页面
    currentStep.value = 'judge'
  } else if (!hasStrategy) {
    // 如果还没有选择策略，显示策略选择页面
    currentStep.value = 'strategy'
  } else {
    // 所有步骤都完成了，显示最后一步
    currentStep.value = steps[steps.length - 1].key
    // 如果所有步骤都完成了，触发完成事件
    emit('complete')
  }
})

</script>

<style scoped>
/* =============================================
   PreTrial — 重构样式（全站 CSS 变量）
   ============================================= */

/* ── 容器 ── */
.pretrial-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

/* ─────────────── Stepper 步骤导航 ─────────────── */
.steps-nav {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  padding: var(--spacing-lg) var(--spacing-xl);
  box-shadow: var(--shadow-sm);
}

.steps-track {
  display: flex;
  align-items: flex-start;
  position: relative;
}

/* 连接线（灰色底线） */
.steps-track::before {
  content: '';
  position: absolute;
  top: 15px;
  left: 10%;
  right: 10%;
  height: 2px;
  background: var(--border-color);
  z-index: 0;
}

.step-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  position: relative;
  z-index: 1;
  transition: opacity var(--transition-base);
  padding: 0 4px;
}

.step-item.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* 圆形节点 */
.step-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: var(--font-size-sm);
  transition: all var(--transition-base);
  /* 默认：可访问未激活 */
  background: var(--bg-tertiary);
  border: 2px solid var(--border-color);
  color: var(--text-secondary);
  box-shadow: none;
}

.step-item.active .step-circle {
  background: var(--primary-purple);
  border-color: var(--primary-purple);
  color: #fff;
  box-shadow: 0 0 0 4px var(--bg-overlay);
}

.step-item.completed .step-circle {
  background: var(--accent-green);
  border-color: var(--accent-green);
  color: #fff;
}

.step-item.disabled .step-circle {
  background: var(--bg-tertiary);
  border-color: var(--border-color);
  color: var(--text-tertiary);
}

.step-icon {
  width: 14px;
  height: 14px;
}

.step-num {
  font-size: var(--font-size-sm);
  line-height: 1;
}

.step-label {
  font-size: var(--font-size-xs);
  font-weight: 500;
  color: var(--text-secondary);
  text-align: center;
  white-space: nowrap;
  transition: color var(--transition-base);
}

.step-item.active .step-label {
  color: var(--primary-purple);
  font-weight: 600;
}

.step-item.completed .step-label {
  color: var(--accent-green);
}

/* ─────────────── 内容区域过渡 ─────────────── */
.content-area {
  min-height: 280px;
}

/* step-fade 过渡动画 */
.step-fade-enter-active,
.step-fade-leave-active {
  transition: opacity var(--transition-base) ease,
              transform var(--transition-base) ease;
}

.step-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.step-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.step-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

/* ─────────────── 通用步骤标题 ─────────────── */
.step-header {
  text-align: center;
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
}

.step-title {
  font-family: var(--font-heading);
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-xs) 0;
  letter-spacing: -0.02em;
}

.step-desc {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin: 0;
}

/* ─────────────── 步骤操作按钮 ─────────────── */
.step-actions {
  display: flex;
  justify-content: center;
  padding-top: var(--spacing-md);
}

.step-actions .el-button {
  min-width: 160px;
  font-size: var(--font-size-base);
  font-weight: 600;
  letter-spacing: 0.02em;
}

/* ─────────────── 身份选择卡片 ─────────────── */
.identity-selector {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-lg);
}

.identity-option {
  position: relative;
  padding: var(--spacing-2xl) var(--spacing-xl);
  border: 1.5px solid var(--border-color);
  border-radius: var(--radius-xl);
  text-align: center;
  cursor: pointer;
  background: var(--bg-primary);
  transition: all var(--transition-hover);
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(8px);
  overflow: hidden;
}

.identity-option::before {
  content: '';
  position: absolute;
  inset: 0;
  background: var(--bg-overlay);
  opacity: 0;
  transition: opacity var(--transition-hover);
  pointer-events: none;
}

.identity-option:hover {
  border-color: var(--primary-purple-light);
  transform: translateY(-4px);
  box-shadow: var(--shadow-card-hover);
}

.identity-option:hover::before {
  opacity: 1;
}

.identity-option.active {
  border-color: var(--primary-purple);
  background: var(--primary-purple-lightest);
  box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.15), var(--shadow-card);
}

.option-icon-wrap {
  width: 64px;
  height: 64px;
  margin: 0 auto var(--spacing-lg);
  border-radius: var(--radius-xl);
  background: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background var(--transition-hover);
}

.identity-option.active .option-icon-wrap {
  background: var(--bg-overlay);
}

.option-svg {
  width: 32px;
  height: 32px;
  color: var(--primary-purple);
}

.option-label {
  font-family: var(--font-heading);
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--spacing-xs);
}

.option-desc {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.5;
}

/* 选中状态勾图标 */
.option-check {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 22px;
  height: 22px;
  color: var(--accent-green);
  opacity: 0;
  transform: scale(0.6);
  transition: all var(--transition-base);
}

.identity-option.active .option-check {
  opacity: 1;
  transform: scale(1);
}

/* ─────────────── 上传区域 ─────────────── */
.upload-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.upload-area {
  min-height: 180px;
  border: 2px dashed var(--border-color);
  border-radius: var(--radius-xl);
  padding: var(--spacing-2xl) var(--spacing-xl);
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-base);
  background: var(--bg-primary);
  position: relative;
  pointer-events: auto;
  user-select: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area:hover {
  border-color: var(--primary-purple-light);
  background: var(--bg-tertiary);
}

.upload-area.dragging {
  border-color: var(--primary-purple);
  border-style: solid;
  background: var(--primary-purple-lightest);
  transform: scale(1.01);
}

.upload-area.has-files {
  border-style: solid;
  border-color: var(--primary-purple-light);
  background: var(--bg-primary);
  padding: var(--spacing-xl);
  min-height: auto;
  align-items: flex-start;
  justify-content: flex-start;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.upload-icon-wrap {
  width: 72px;
  height: 72px;
  border-radius: var(--radius-xl);
  background: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--spacing-lg);
  transition: all var(--transition-base);
}

.upload-icon-wrap.is-dragging {
  background: var(--bg-overlay);
  animation: pulse 0.8s ease-in-out infinite;
}

.upload-svg {
  width: 32px;
  height: 32px;
  color: var(--primary-purple);
}

.upload-text {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-xs) 0;
}

.upload-hint {
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
  margin: 0;
}

/* 文件预览列表 */
.file-preview {
  width: 100%;
  pointer-events: none;
}

.file-count-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--primary-purple);
  margin-bottom: var(--spacing-md);
}

.file-count-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.file-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
  pointer-events: auto;
}

.file-tag {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: 6px var(--spacing-md);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  transition: all var(--transition-fast);
}

.file-tag.uploading {
  background: rgba(234, 179, 8, 0.08);
  border-color: rgba(234, 179, 8, 0.4);
}

.file-tag.uploaded {
  background: var(--accent-green-soft);
  border-color: rgba(34, 197, 94, 0.35);
}

.file-tag-icon {
  width: 14px;
  height: 14px;
  color: var(--text-secondary);
  flex-shrink: 0;
}

.file-name {
  color: var(--text-primary);
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: var(--font-size-sm);
}

.upload-status-text {
  font-size: var(--font-size-xs);
  color: #ca8a04;
}

.upload-ok-icon {
  width: 14px;
  height: 14px;
  color: var(--accent-green);
  flex-shrink: 0;
}

.remove-btn {
  width: 18px;
  height: 18px;
  border: none;
  background: transparent;
  padding: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  color: var(--text-tertiary);
  border-radius: var(--radius-sm);
  flex-shrink: 0;
  transition: color var(--transition-fast);
}

.remove-btn:hover {
  color: #ef4444;
}

.remove-icon {
  width: 12px;
  height: 12px;
}

.clear-btn {
  align-self: flex-start;
  background: transparent;
  border: none;
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 4px 0;
  transition: color var(--transition-fast);
}

.clear-btn:hover {
  color: #ef4444;
}

/* ─────────────── 描述生成 ─────────────── */
.description-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.generate-btn {
  width: 100%;
  height: 52px;
  border: none;
  border-radius: var(--radius-lg);
  background: var(--primary-purple);
  color: #fff;
  font-size: var(--font-size-base);
  font-weight: 600;
  font-family: var(--font-heading);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  transition: all var(--transition-hover);
  letter-spacing: 0.02em;
}

.generate-btn:hover:not(:disabled) {
  background: var(--primary-purple-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.generate-btn:disabled {
  opacity: 0.75;
  cursor: not-allowed;
}

.gen-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

/* 旋转加载 spinner */
.gen-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255,255,255,0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 骨架屏 */
.desc-skeleton {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: var(--spacing-xl);
  background: var(--bg-tertiary);
  border-radius: var(--radius-lg);
}

.sk-line {
  height: 12px;
  border-radius: var(--radius-sm);
  background: linear-gradient(90deg, var(--border-color) 25%, var(--bg-primary) 50%, var(--border-color) 75%);
  background-size: 400% 100%;
  animation: shimmer 1.4s ease-in-out infinite;
}

.sk-long  { width: 100%; }
.sk-mid   { width: 75%; }
.sk-short { width: 55%; }

.description-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.description-input {
  width: 100%;
}

.description-tip {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--bg-overlay);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  color: var(--primary-purple);
  border: 1px solid rgba(6, 182, 212, 0.2);
}

.tip-svg {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

/* ─────────────── 审判员卡片 ─────────────── */
.judge-select-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.judge-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-md);
}

.judge-card {
  position: relative;
  padding: var(--spacing-lg) var(--spacing-md);
  border: 1.5px solid var(--border-color);
  border-radius: var(--radius-lg);
  cursor: pointer;
  background: var(--bg-primary);
  transition: all var(--transition-hover);
  box-shadow: var(--shadow-sm);
  text-align: center;
}

.judge-card:hover {
  border-color: var(--primary-purple-light);
  transform: translateY(-3px);
  box-shadow: var(--shadow-card-hover);
}

.judge-card.active {
  border-color: var(--primary-purple);
  background: var(--primary-purple-lightest);
  box-shadow: 0 0 0 2px rgba(6,182,212,0.15), var(--shadow-card);
}

.judge-card-label {
  font-family: var(--font-heading);
  font-size: var(--font-size-base);
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--spacing-xs);
}

.judge-card.active .judge-card-label {
  color: var(--primary-purple-dark);
}

.judge-card-desc {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  line-height: 1.5;
}

.judge-check {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 18px;
  height: 18px;
  color: var(--accent-green);
  opacity: 0;
  transform: scale(0.5);
  transition: all var(--transition-base);
}

.judge-card.active .judge-check {
  opacity: 1;
  transform: scale(1);
}

/* ─────────────── 策略选择卡片 ─────────────── */
.strategy-select-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.strategy-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-lg);
}

.strategy-option {
  position: relative;
  padding: var(--spacing-xl);
  border: 1.5px solid var(--border-color);
  border-radius: var(--radius-xl);
  cursor: pointer;
  background: var(--bg-primary);
  transition: all var(--transition-hover);
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(8px);
  overflow: hidden;
}

.strategy-option:hover {
  border-color: var(--primary-purple-light);
  transform: translateY(-4px);
  box-shadow: var(--shadow-card-hover);
}

.strategy-option.active {
  border-color: var(--primary-purple);
  background: var(--primary-purple-lightest);
  box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.12), var(--shadow-card);
}

.strategy-option-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.strategy-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-lg);
  background: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background var(--transition-hover);
}

.strategy-option.active .strategy-icon-wrap {
  background: var(--bg-overlay);
}

.strategy-svg {
  width: 22px;
  height: 22px;
  color: var(--primary-purple);
}

.strategy-title-text {
  font-family: var(--font-heading);
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--text-primary);
}

.strategy-description {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin-bottom: var(--spacing-md);
  line-height: 1.6;
}

.strategy-features {
  border-top: 1px solid var(--border-color);
  padding-top: var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.strategy-feature {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  line-height: 1.5;
}

.feature-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--primary-purple);
  flex-shrink: 0;
}

/* 策略选中勾 */
.strategy-check {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 22px;
  height: 22px;
  color: var(--accent-green);
  opacity: 0;
  transform: scale(0.5);
  transition: all var(--transition-base);
}

.strategy-option.active .strategy-check {
  opacity: 1;
  transform: scale(1);
}
</style>

