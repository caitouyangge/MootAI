<template>
  <div class="debate-container">
    <!-- 身份信息显示 -->
    <div class="identity-display-section">
      <h3 class="section-title">身份</h3>
      <div class="identity-info">
        <span class="identity-label">{{ userIdentity === 'plaintiff' ? '原告' : '被告' }}</span>
      </div>
    </div>

    <!-- 庭前准备材料查看 -->
    <div class="pretrial-materials-section">
      <div class="materials-header">
        <h3 class="section-title">庭前准备材料</h3>
        <el-button
          text
          size="small"
          @click="showMaterials = !showMaterials"
          class="toggle-btn"
        >
          {{ showMaterials ? '收起' : '查看' }}
        </el-button>
      </div>
      <el-collapse-transition>
        <div v-show="showMaterials" class="materials-content">
          <div class="material-item" v-if="fileList.length > 0">
            <div class="material-label">上传文件：</div>
            <div class="material-value">
              <div v-for="(file, index) in fileList" :key="index" class="file-item">
                <span class="file-icon">📄</span>
                <span>{{ file.name }}</span>
              </div>
            </div>
          </div>
          <div class="material-item" v-if="caseDescription">
            <div class="material-label">案件描述：</div>
            <div class="material-value case-description">{{ caseDescription }}</div>
          </div>
        </div>
      </el-collapse-transition>
    </div>

    <!-- 法官类型显示 -->
    <div class="judge-display-section">
      <h3 class="section-title">法官类型</h3>
      <div class="judge-info">
        <span class="judge-label">{{ getJudgeLabel(selectedJudgeType) }}</span>
        <span class="judge-desc">{{ getJudgeDescription(selectedJudgeType) }}</span>
      </div>
    </div>

    <!-- 对方AI律师策略显示 -->
    <div class="strategy-display-section">
      <h3 class="section-title">对方AI律师策略</h3>
      <div class="strategy-card" :class="userIdentity === 'plaintiff' ? 'defendant-strategy' : 'plaintiff-strategy'">
        <div class="strategy-label">{{ userIdentity === 'plaintiff' ? '被告' : '原告' }}策略</div>
        <div class="strategy-content">{{ userIdentity === 'plaintiff' ? defendantStrategy : plaintiffStrategy }}</div>
      </div>
    </div>

    <!-- 庭审对话区域 -->
    <div class="debate-chat-section">
      <div class="section-header">
        <h3 class="section-title">庭审现场</h3>
        <el-button
          v-if="debateStarted && messages.length > 0"
          type="warning"
          size="small"
          class="reset-debate-btn"
          @click="handleResetDebate"
          :icon="Refresh"
        >
          重置
        </el-button>
      </div>
      <div class="chat-container" ref="chatContainer">
        <!-- 模型初始化提示 -->
        <div v-if="modelInitializing || (modelInitProgress && !modelLoaded)" class="model-init-progress">
          <div class="progress-content">
            <el-icon class="is-loading progress-icon"><Loading /></el-icon>
            <div class="progress-text">
              <div class="progress-title">正在初始化AI模型...</div>
              <div class="progress-message">{{ modelInitProgress || '请稍候，模型正在加载中...' }}</div>
              <div class="progress-tip">首次加载可能需要几分钟时间，请耐心等待</div>
            </div>
          </div>
          <div v-if="modelInitError" class="progress-error">
            <el-icon><Warning /></el-icon>
            <span>初始化失败: {{ modelInitError }}</span>
          </div>
        </div>
        <div v-else-if="messages.length === 0" class="empty-tip">
          <p>请点击"开始庭审"按钮开始模拟法庭辩论</p>
        </div>
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message-item', `message-${message.role}`]"
        >
          <!-- 原告：左边布局 -->
          <template v-if="message.role === 'plaintiff'">
            <div class="message-avatar">
              <div class="avatar avatar-plaintiff">原</div>
            </div>
            <div class="message-content-wrapper">
              <div class="message-name">{{ message.name }}</div>
              <div class="message-bubble message-bubble-left">
                <div v-if="editingIndex !== index" class="message-text">{{ message.text }}</div>
                <el-input
                  v-else
                  v-model="editingText"
                  type="textarea"
                  :autosize="{ minRows: 1, maxRows: 50 }"
                  class="edit-textarea"
                  @blur="saveEdit(index)"
                  @keydown.ctrl.enter="saveEdit(index)"
                />
                <div v-if="userIdentity === 'plaintiff' && editingIndex !== index" class="edit-btn-wrapper">
                  <el-button
                    text
                    type="primary"
                    size="small"
                    class="edit-btn"
                    @click="startEdit(index, message.text)"
                  >
                    编辑
                  </el-button>
                </div>
              </div>
              <div class="message-time">{{ message.time }}</div>
            </div>
          </template>

          <!-- 法官：中间布局 -->
          <template v-else-if="message.role === 'judge'">
            <div class="message-center-wrapper">
              <div class="message-avatar-center">
                <div class="avatar avatar-judge">法</div>
              </div>
              <div class="message-content-center">
                <div class="message-name-center">{{ message.name }}</div>
                <div class="message-bubble message-bubble-center">
                  <div class="message-text">{{ message.text }}</div>
                </div>
                <div class="message-time-center">{{ message.time }}</div>
              </div>
            </div>
          </template>

          <!-- 被告：右边布局 -->
          <template v-else-if="message.role === 'defendant'">
            <div class="message-defendant-wrapper">
              <div class="message-content-wrapper message-content-right">
                <div class="message-name message-name-right">{{ message.name }}</div>
                <div class="message-bubble message-bubble-right">
                  <div v-if="editingIndex !== index" class="message-text">{{ message.text }}</div>
                  <el-input
                    v-else
                    v-model="editingText"
                    type="textarea"
                    :autosize="{ minRows: 1, maxRows: 50 }"
                    class="edit-textarea"
                    @blur="saveEdit(index)"
                    @keydown.ctrl.enter="saveEdit(index)"
                  />
                  <div v-if="userIdentity === 'defendant' && editingIndex !== index" class="edit-btn-wrapper">
                    <el-button
                      text
                      type="primary"
                      size="small"
                      class="edit-btn"
                      @click="startEdit(index, message.text)"
                    >
                      编辑
                    </el-button>
                  </div>
                </div>
                <div class="message-time message-time-right">{{ message.time }}</div>
              </div>
              <div class="message-avatar message-avatar-right">
                <div class="avatar avatar-defendant">被</div>
              </div>
            </div>
          </template>
        </div>
      </div>
      
      <!-- 用户输入区域 -->
      <div v-if="debateStarted && !debateCompleted" class="input-section">
        <!-- 发言状态提示 -->
        <div class="speaking-status">
          <div v-if="isGenerating" class="status-item status-generating">
            <span class="status-icon">⏳</span>
            <span class="status-text">{{ currentSpeakingRole }}正在发言中...</span>
          </div>
          <div v-else-if="isUserTurn" class="status-item status-user-turn">
            <span class="status-icon">💬</span>
            <span class="status-text">轮到您发言了（{{ userIdentity === 'plaintiff' ? '原告' : '被告' }}）</span>
          </div>
          <div v-else class="status-item status-waiting">
            <span class="status-icon">⏸️</span>
            <span class="status-text">请等待{{ nextSpeakerName }}发言</span>
          </div>
        </div>
        
        <!-- AI代理和策略选择 -->
        <div v-if="isUserTurn" class="ai-proxy-section">
          <div class="ai-proxy-switch">
            <el-switch
              v-model="useAiProxy"
              active-text="使用AI代理"
              inactive-text="手动输入"
              size="default"
            />
          </div>
          <div v-if="useAiProxy" class="strategy-selector">
            <span class="strategy-label">回复策略：</span>
            <el-select
              v-model="userStrategy"
              placeholder="请选择回复策略"
              size="small"
              style="width: 200px"
            >
              <el-option
                v-for="(desc, key) in strategyDefinitions"
                :key="key"
                :label="getStrategyLabel(key)"
                :value="key"
              >
                <div class="strategy-option">
                  <div class="strategy-option-label">{{ getStrategyLabel(key) }}</div>
                  <div class="strategy-option-desc">{{ desc }}</div>
                </div>
              </el-option>
            </el-select>
          </div>
        </div>
        
        <div class="input-wrapper">
          <el-input
            v-model="userInput"
            type="textarea"
            :rows="3"
            :placeholder="isUserTurn ? (useAiProxy ? '点击AI生成发言按钮生成内容，确认后点击发送' : `请输入您的发言（作为${userIdentity === 'plaintiff' ? '原告' : '被告'}）...`) : '请等待其他角色发言...'"
            class="user-input"
            :disabled="!isUserTurn || isGenerating"
            @keydown.ctrl.enter="sendMessage"
          />
          <div class="input-actions">
            <el-button
              v-if="useAiProxy"
              type="default"
              :loading="isGenerating"
              :disabled="!isUserTurn || isGenerating"
              @click="generateUserAiResponse"
            >
              {{ isGenerating ? '生成中...' : 'AI生成发言' }}
            </el-button>
            <el-button
              type="primary"
              :loading="isGenerating"
              :disabled="!isUserTurn || !userInput.trim() || isGenerating"
              @click="sendMessage"
            >
              {{ isGenerating ? '生成中...' : '发送' }}
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作按钮区域 -->
    <div class="action-section">
      <el-button
        v-if="!debateStarted"
        type="primary"
        size="large"
        class="start-btn"
        :disabled="!selectedJudgeType || !opponentStrategy"
        @click="startDebate"
      >
        开始庭审
      </el-button>
      <p v-if="!debateStarted && (!selectedJudgeType || !opponentStrategy)" class="start-hint">
        请先在庭前准备阶段完成法官类型和策略选择
      </p>
      <el-button
        v-if="debateCompleted"
        type="primary"
        size="large"
        class="generate-btn"
        @click="generateVerdict"
      >
        生成判决书
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading, Warning, Refresh } from '@element-plus/icons-vue'
import { useCaseStore } from '@/stores/case'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()

// 定义emit
const emit = defineEmits(['complete'])

// 获取身份信息（从store或route）
const caseStore = useCaseStore()
const userIdentity = ref(caseStore.selectedIdentity || route.query.identity || 'plaintiff')
const caseDescription = ref(caseStore.caseDescription || '')
const fileList = ref(caseStore.fileList || [])
const showMaterials = ref(false)

// 法官类型（从store读取）
const judgeTypes = ref([
  {
    value: 'professional',
    label: '专业型',
    description: '讲话简洁，业务熟练，判决果断'
  },
  {
    value: 'strong',
    label: '强势型',
    description: '专业能力出众，细节能力强'
  },
  {
    value: 'partial-plaintiff',
    label: '偏袒型（原告）',
    description: '习惯对原告宽容'
  },
  {
    value: 'partial-defendant',
    label: '偏袒型（被告）',
    description: '习惯对被告宽容'
  },
  {
    value: 'neutral',
    label: '中立型',
    description: '保持中立，注重程序公正'
  }
])

const selectedJudgeType = ref(caseStore.selectedJudgeType || 'neutral')
const debateStarted = ref(false)
const isGenerating = ref(false)
const userInput = ref('')
const currentSpeakingRole = ref('') // 当前正在发言的角色

const getJudgeLabel = (value) => {
  const judge = judgeTypes.value.find(j => j.value === value)
  return judge ? judge.label : '未选择'
}

const getJudgeDescription = (value) => {
  const judge = judgeTypes.value.find(j => j.value === value)
  return judge ? judge.description : ''
}

// 策略选项定义
const strategyDefinitions = {
  aggressive: '激进策略：采取强硬立场，积极进攻，不轻易让步。主动质疑对方证据，强调己方优势，对争议点进行深入辩论。',
  conservative: '保守策略：优先考虑通过调解解决争议，主张较为温和，可适当让步。避免过度激化矛盾，保持协商空间。',
  balanced: '均衡策略：主张适中，准备充分的证据，但不过度激化矛盾。保持协商空间，平衡攻守。',
  defensive: '防御策略：重点防守，回应对方质疑，保护己方核心利益。谨慎应对争议点，避免主动进攻。'
}

// 策略标签映射
const strategyLabels = {
  aggressive: '激进策略',
  conservative: '保守策略',
  balanced: '均衡策略',
  defensive: '防御策略'
}

// 获取策略标签
const getStrategyLabel = (key) => {
  return strategyLabels[key] || key
}

// 诉讼策略（根据用户身份和对方策略设置）
const opponentStrategy = ref(caseStore.opponentStrategy || 'balanced')
const plaintiffStrategy = ref('')
const defendantStrategy = ref('')

// AI代理相关
const useAiProxy = ref(false) // 是否使用AI代理
const userStrategy = ref('balanced') // 用户自己的策略

// 根据用户身份和对方策略初始化策略
const initStrategies = () => {
  if (userIdentity.value === 'plaintiff') {
    // 用户是原告，对方是被告
    defendantStrategy.value = strategyDefinitions[opponentStrategy.value] || strategyDefinitions.balanced
    plaintiffStrategy.value = '均衡策略：主张适中，准备充分的证据，但不过度激化矛盾。保持协商空间，平衡攻守。'
  } else {
    // 用户是被告，对方是原告
    plaintiffStrategy.value = strategyDefinitions[opponentStrategy.value] || strategyDefinitions.balanced
    defendantStrategy.value = '均衡策略：主张适中，准备充分的证据，但不过度激化矛盾。保持协商空间，平衡攻守。'
  }
}

// 初始化策略
initStrategies()

// 监听用户身份变化，重新初始化策略
watch(userIdentity, () => {
  initStrategies()
})

// 监听对方策略变化，重新初始化策略
watch(opponentStrategy, () => {
  initStrategies()
})

// 对话消息
const messages = ref([])
const debateCompleted = ref(false)
const chatContainer = ref(null)

// 模型初始化状态
const modelInitializing = ref(false)
const modelLoaded = ref(false)
const modelInitProgress = ref('')
const modelInitProgressSteps = ref([])
const modelInitError = ref(null)
const modelStatusPollTimer = ref(null)

// 编辑相关
const editingIndex = ref(-1)
const editingText = ref('')

// 开始编辑
const startEdit = (index, text) => {
  editingIndex.value = index
  editingText.value = text
}

// 保存编辑
const saveEdit = async (index) => {
  if (editingIndex.value === index && editingText.value.trim()) {
    messages.value[index].text = editingText.value.trim()
    // TODO: 基于修改重新生成后续对话（AI部分暂时没有）
    ElMessage.success('内容已更新')
    
    // 保存到localStorage
    localStorage.setItem('debateMessages', JSON.stringify(messages.value))
    
    // 保存到数据库
    if (caseStore.caseId) {
      clearTimeout(saveDebateMessagesTimer)
      saveDebateMessagesTimer = setTimeout(() => {
        saveDebateMessages()
      }, 500) // 编辑后立即保存（0.5秒延迟）
    }
  }
  editingIndex.value = -1
  editingText.value = ''
}

// 开始庭审
const startDebate = async () => {
  console.log('[辩论流程] 开始庭审 - 开始')
  console.log('[辩论流程] 法官类型:', selectedJudgeType.value, ', 对方策略:', opponentStrategy.value)
  
  if (!selectedJudgeType.value) {
    ElMessage.warning('请先在庭前准备阶段选择法官类型')
    return
  }
  
  if (!opponentStrategy.value) {
    ElMessage.warning('请先在庭前准备阶段选择对方AI律师的辩论策略')
    return
  }
  
  messages.value = []
  debateCompleted.value = false
  debateStarted.value = true
  
  console.log('[辩论流程] 初始化辩论状态完成')
  
  // 清除之前的辩论完成标记
  localStorage.removeItem('debateCompleted')
  
  // 立即保存空消息列表到数据库（标记辩论开始）
  if (caseStore.caseId) {
    clearTimeout(saveDebateMessagesTimer)
    await saveDebateMessages()
  }
  
  // 法官宣布开始（开庭时必须发言引导原告发言）
  const judgePrompt = '现在开庭。请原告陈述诉讼请求和事实理由。'
  console.log('[辩论流程] 生成首次法官发言')
  
  await generateAiResponse('judge', judgePrompt, true)
  console.log('[辩论流程] 开始庭审 - 结束')
}

// 发送用户消息
const sendMessage = async () => {
  console.log('[辩论流程] 用户发送消息 - 开始')
  console.log('[辩论流程] 当前状态 - isGenerating:', isGenerating.value, ', isUserTurn:', isUserTurn.value)
  
  if (isGenerating.value || !isUserTurn.value) {
    console.log('[辩论流程] 条件不满足，跳过发送')
    return
  }
  
  // 检查输入框是否有内容
  if (!userInput.value.trim()) {
    console.log('[辩论流程] 输入框为空，跳过发送')
    return
  }
  
  const userText = userInput.value.trim()
  userInput.value = ''
  
  console.log('[辩论流程] 用户发言内容长度:', userText.length, ', 预览:', userText.substring(0, 100))
  
  // 更新当前发言角色为用户
  const userRoleName = userIdentity.value === 'plaintiff' ? '原告' : '被告'
  currentSpeakingRole.value = userRoleName
  console.log('[辩论流程] 设置用户发言角色:', userRoleName)
  
  // 添加用户消息
  addMessage(userIdentity.value, userRoleName, userText)
  
  // 用户发言结束
  currentSpeakingRole.value = ''
  console.log('[辩论流程] 用户发言完成，清空发言角色')
  
  // 生成对方律师的回复
  // 传递 shouldCheckJudgeAfter=true，让AI回复后自动检查法官（因为已经完成一轮：用户发言 + AI回复）
  const opponentRole = userIdentity.value === 'plaintiff' ? 'defendant' : 'plaintiff'
  console.log('[辩论流程] 生成对方律师回复，角色:', opponentRole)
  await generateAiResponse(opponentRole, userText, false, true)
  console.log('[辩论流程] 用户发送消息 - 结束')
}

// 生成用户AI代理回复（生成到输入框，不直接发送）
const generateUserAiResponse = async () => {
  if (isGenerating.value) return
  
  isGenerating.value = true
  
  // 更新当前发言角色为用户
  const roleName = userIdentity.value === 'plaintiff' ? '原告' : '被告'
  currentSpeakingRole.value = roleName
  
  try {
    // 准备消息历史
    const messageHistory = messages.value.map(msg => ({
      role: msg.role,
      name: msg.name,
      text: msg.text
    }))
    
    // 构建完整的background（包含所有庭前准备资料）
    const background = buildBackground()
    
    const response = await request.post('/debate/generate', {
      userIdentity: userIdentity.value,
      currentRole: userIdentity.value, // 用户自己的角色
      messages: messageHistory,
      judgeType: selectedJudgeType.value || 'neutral',
      caseDescription: background,
      userStrategy: userStrategy.value || 'balanced', // 用户策略
      isUserProxy: true // 标记为用户代理模式
    }, {
      timeout: 0
    })
    
    if (response.code === 200 && response.data) {
      const aiText = response.data
      
      // 将生成的文本放入输入框，让用户确认后再发送
      userInput.value = aiText
      
      // 用户发言结束
      currentSpeakingRole.value = ''
      
      ElMessage.success('AI已生成发言内容，请确认后点击发送')
    } else {
      ElMessage.error(response.message || 'AI生成失败')
    }
  } catch (error) {
    console.error('生成用户AI回复失败:', error)
    ElMessage.error('生成失败，请重试: ' + (error.message || '未知错误'))
  } finally {
    isGenerating.value = false
    currentSpeakingRole.value = ''
  }
}

// 构建完整的background参数（包含庭前准备的所有资料）
const buildBackground = () => {
  let background = ''
  
  // 1. 身份信息
  background += `【身份信息】\n`
  background += `用户身份：${userIdentity.value === 'plaintiff' ? '原告' : '被告'}\n\n`
  
  // 2. 文件列表
  if (fileList.value && fileList.value.length > 0) {
    background += `【上传文件】\n`
    fileList.value.forEach((file, index) => {
      background += `${index + 1}. ${file.name}\n`
      // 如果有文件内容，也包含进去
      if (file.content) {
        background += `   内容预览：${file.content.substring(0, 200)}${file.content.length > 200 ? '...' : ''}\n`
      }
    })
    background += `\n`
  }
  
  // 3. 案件描述
  if (caseDescription.value) {
    background += `【案件描述】\n${caseDescription.value}\n\n`
  }
  
  // 4. 诉讼策略
  background += `【诉讼策略】\n`
  if (userIdentity.value === 'plaintiff') {
    // 如果用户使用AI代理，使用用户选择的策略；否则使用默认策略
    const userStrategyDesc = useAiProxy.value && userStrategy.value 
      ? strategyDefinitions[userStrategy.value] 
      : plaintiffStrategy.value
    background += `原告策略：${userStrategyDesc}\n`
    background += `被告策略：${defendantStrategy.value}\n`
  } else {
    // 如果用户使用AI代理，使用用户选择的策略；否则使用默认策略
    const userStrategyDesc = useAiProxy.value && userStrategy.value 
      ? strategyDefinitions[userStrategy.value] 
      : defendantStrategy.value
    background += `原告策略：${plaintiffStrategy.value}\n`
    background += `被告策略：${userStrategyDesc}\n`
  }
  
  return background
}

// 检查法官是否应该发言
const checkJudgeShouldSpeak = async () => {
  console.log('[辩论流程] 检查法官是否应该发言 - 开始')
  console.log('[辩论流程] 当前状态 - isGenerating:', isGenerating.value, ', currentSpeakingRole:', currentSpeakingRole.value)
  console.log('[辩论流程] 消息数量:', messages.value.length)
  
  if (isGenerating.value) {
    console.log('[辩论流程] 正在生成中，跳过检查')
    return
  }
  
  // 如果最后一条消息是法官发言，说明法官刚刚发言了，应该从法官发言中提取下一个发言人
  // 这种情况不应该进入这个函数，但如果进入了，应该直接提取下一个发言人
  if (messages.value.length > 0) {
    const lastMessage = messages.value[messages.value.length - 1]
    console.log('[辩论流程] 最后一条消息 - 角色:', lastMessage.role, ', 内容预览:', lastMessage.text.substring(0, 50))
    
    if (lastMessage.role === 'judge') {
      console.log('[辩论流程] 最后是法官发言，从发言中提取下一个发言人')
      // 最后是法官发言，从法官发言中提取下一个发言人
      // 注意：这里不需要设置isGenerating，因为法官已经发言完成
      await extractNextSpeakerFromJudgeSpeech(lastMessage.text)
      console.log('[辩论流程] 提取下一个发言人完成')
      return
    }
  }
  
  // 设置生成状态，防止在法官思考时显示"轮到用户发言"
  console.log('[辩论流程] 设置法官发言状态')
  isGenerating.value = true
  currentSpeakingRole.value = '法官'
  
  // 检查是否至少完成一轮（原告+被告）
  // 硬性要求：必须确保双方已经进行了至少一轮完整的对话（原告发言+被告发言）
  const lastNonJudgeMessages = messages.value.filter(m => m.role !== 'judge')
  if (lastNonJudgeMessages.length === 0) {
    console.log('[辩论流程] 没有非法官消息，跳过法官检查')
    isGenerating.value = false
    currentSpeakingRole.value = ''
    await continueAlternatingDebate()
    return
  }
  
  const lastNonJudgeMessage = lastNonJudgeMessages[lastNonJudgeMessages.length - 1]
  const secondLastNonJudgeMessage = lastNonJudgeMessages.length >= 2 ? lastNonJudgeMessages[lastNonJudgeMessages.length - 2] : null
  
  // 硬性要求：必须至少完成一轮（原告+被告）
  // 如果最后一条是原告发言，说明被告还没有回复，此时不能介入
  if (lastNonJudgeMessage.role === 'plaintiff') {
    console.log('[辩论流程] 最后是原告发言，被告还没有回复，不满足硬性条件（至少完成一轮），跳过法官检查')
    isGenerating.value = false
    currentSpeakingRole.value = ''
    await continueAlternatingDebate()
    return
  }
  
  // 如果最后一条是被告发言，需要检查前一条是否是原告发言
  if (lastNonJudgeMessage.role === 'defendant') {
    if (!secondLastNonJudgeMessage || secondLastNonJudgeMessage.role !== 'plaintiff') {
      console.log('[辩论流程] 最后是被告发言，但前一条不是原告发言，不满足硬性条件（至少完成一轮），跳过法官检查')
      isGenerating.value = false
      currentSpeakingRole.value = ''
      await continueAlternatingDebate()
      return
    }
    // 如果最后是被告，前一条是原告，说明完成了一轮，可以判断
    console.log('[辩论流程] 满足硬性条件（至少完成一轮：原告+被告），开始判断法官是否需要介入')
  }
  
  // 构建判断提示词
  const judgeCheckPrompt = `根据当前的庭审对话历史，请判断作为审判员，你是否需要发言。

【重要】发言顺序：原告先发言，然后被告发言，每完成一轮（原告+被告）后，你判断是否需要介入。

【硬性要求】介入的硬性条件：必须确保双方已经进行了至少一轮完整的对话（原告发言+被告发言），否则绝对不能介入。如果对话历史中最后一条是原告发言，说明被告还没有回复，此时绝对不能介入，必须等待被告发言后再判断。

【介入条件】只有在满足硬性条件（至少完成一轮）的前提下，且出现以下情况时才需要介入：
- 需要归纳争议焦点时
- 需要纠正程序错误时
- 需要制止不当言论时
- 需要引导辩论方向时
- 辩论阶段结束时

【重要原则】
1. 即使满足硬性条件和介入条件，也要尽量减少介入。非必要不介入，不说废话。如果双方辩论正常进行，没有程序问题，没有需要纠正的地方，就不要发言。
2. 如果需要发言，发言内容必须简洁、专业、有针对性，不要说套话、空话。发言后必须明确指定下一个发言人的身份（"请原告继续"或"请被告继续"）。
3. 如果不需要发言，请只输出"不需要发言"，然后由原告和被告继续轮流发言。`
  
  try {
    const messageHistory = messages.value.map(msg => ({
      role: msg.role,
      name: msg.name,
      text: msg.text
    }))
    
    console.log('[辩论流程] 调用AI服务判断法官是否需要发言')
    const response = await request.post('/debate/generate', {
      userIdentity: userIdentity.value,
      currentRole: 'judge',
      messages: messageHistory,
      judgeType: selectedJudgeType.value || 'neutral',
      caseDescription: buildBackground(), // 使用完整的background
      checkMode: true, // 标记为判断模式
      prompt: judgeCheckPrompt
    }, {
      timeout: 0
    })
    
    if (response.code === 200 && response.data) {
      const judgeResponse = response.data.trim()
      console.log('[辩论流程] AI返回法官响应，长度:', judgeResponse.length, ', 预览:', judgeResponse.substring(0, 100))
      
      // 判断法官是否发言（如果包含"不需要发言"，则不发言）
      if (judgeResponse && !judgeResponse.includes('不需要发言')) {
        console.log('[辩论流程] 法官决定发言，添加消息')
        // 法官发言
        addMessage('judge', '法官', judgeResponse)
        
        console.log('[辩论流程] 法官发言完成，提取下一个发言人')
        // 法官发言后，从发言内容中提取下一个发言人
        // 注意：在extractNextSpeakerFromJudgeSpeech中可能会调用generateAiResponse，会设置新的状态
        await extractNextSpeakerFromJudgeSpeech(judgeResponse)
        console.log('[辩论流程] 提取下一个发言人完成')
      } else {
        console.log('[辩论流程] 法官决定不发言，继续轮流发言')
        // 法官不发言，由原告和被告轮流发言
        await continueAlternatingDebate()
      }
    } else {
      console.error('[辩论流程] AI服务返回错误:', response.message)
    }
  } catch (error) {
    console.error('[辩论流程] 法官判断失败:', error)
    // 如果判断失败，默认继续轮流发言
    await continueAlternatingDebate()
  } finally {
    // 重置生成状态和发言角色
    // 注意：如果extractNextSpeakerFromJudgeSpeech中调用了generateAiResponse，那个函数会设置新的状态
    // 所以这里需要确保状态被正确重置
    console.log('[辩论流程] 重置法官发言状态')
    isGenerating.value = false
    currentSpeakingRole.value = ''
    console.log('[辩论流程] 检查法官是否应该发言 - 结束，状态已重置')
  }
}

// 从法官发言中提取下一个发言人
const extractNextSpeakerFromJudgeSpeech = async (judgeSpeech) => {
  console.log('[辩论流程] 从法官发言中提取下一个发言人 - 开始')
  console.log('[辩论流程] 法官发言内容预览:', judgeSpeech.substring(0, 200))
  console.log('[辩论流程] 用户身份:', userIdentity.value)
  
  // 检查发言中是否指定了下一个发言人
  if (judgeSpeech.includes('请原告') || judgeSpeech.includes('原告继续') || judgeSpeech.includes('原告发言')) {
    console.log('[辩论流程] 法官指定下一个发言人是原告')
    // 如果用户是原告，轮到用户发言，不需要生成AI回复
    if (userIdentity.value === 'plaintiff') {
      console.log('[辩论流程] 用户是原告，轮到用户发言，等待用户输入')
      return
    } else {
      console.log('[辩论流程] 用户是被告，下一个是原告（AI发言），生成AI回复')
      // 用户是被告，下一个是原告（AI发言）
      // 法官发言后，AI回复后不检查法官，等待用户发言
      await generateAiResponse('plaintiff', '', false, false)
    }
  } else if (judgeSpeech.includes('请被告') || judgeSpeech.includes('被告继续') || judgeSpeech.includes('被告发言')) {
    console.log('[辩论流程] 法官指定下一个发言人是被告')
    // 如果用户是被告，轮到用户发言，不需要生成AI回复
    if (userIdentity.value === 'defendant') {
      console.log('[辩论流程] 用户是被告，轮到用户发言，等待用户输入')
      return
    } else {
      console.log('[辩论流程] 用户是原告，下一个是被告（AI发言），生成AI回复')
      // 用户是原告，下一个是被告（AI发言）
      // 法官发言后，AI回复后不检查法官，等待用户发言
      await generateAiResponse('defendant', '', false, false)
    }
  } else {
    console.log('[辩论流程] 法官未明确指定下一个发言人，根据对话历史决定')
    // 如果没有明确指定，根据对话历史决定
    // 注意：decideNextSpeaker 内部调用 generateAiResponse，也会触发 checkJudgeShouldSpeak
    await decideNextSpeaker()
  }
  console.log('[辩论流程] 从法官发言中提取下一个发言人 - 结束')
}

// 决定下一个发言人（法官发言后调用）
const decideNextSpeaker = async () => {
  // 获取最后一条消息的角色
  const lastMessage = messages.value[messages.value.length - 1]
  const lastRole = lastMessage.role
  
  // 如果最后是法官发言，根据对话历史决定下一个发言人
  if (lastRole === 'judge') {
    // 简单逻辑：如果最后是原告发言，下一个是被告；反之亦然
    const plaintiffMessages = messages.value.filter(m => m.role === 'plaintiff')
    const defendantMessages = messages.value.filter(m => m.role === 'defendant')
    
    if (plaintiffMessages.length <= defendantMessages.length) {
      // 原告发言次数少，下一个是原告
      if (userIdentity.value === 'plaintiff') {
        // 轮到用户发言，不需要生成AI回复
        return
      } else {
        // 用户是被告，下一个是原告（AI发言）
        // 法官发言后，AI回复后不检查法官，等待用户发言
        await generateAiResponse('plaintiff', '', false, false)
      }
    } else {
      // 被告发言次数少，下一个是被告
      if (userIdentity.value === 'defendant') {
        // 轮到用户发言，不需要生成AI回复
        return
      } else {
        // 用户是原告，下一个是被告（AI发言）
        // 法官发言后，AI回复后不检查法官，等待用户发言
        await generateAiResponse('defendant', '', false, false)
      }
    }
  }
}

// 继续原告和被告轮流发言
const continueAlternatingDebate = async () => {
  console.log('[辩论流程] 继续原告和被告轮流发言 - 开始')
  
  // 获取最后一条非法官消息的角色
  const lastNonJudgeMessage = [...messages.value].reverse().find(m => m.role !== 'judge')
  
  if (!lastNonJudgeMessage) {
    console.log('[辩论流程] 没有非法官消息，判断下一个发言人')
    // 如果没有非法官消息，判断下一个应该是谁
    // 如果用户是原告，下一个应该是原告（用户发言）
    if (userIdentity.value === 'plaintiff') {
      console.log('[辩论流程] 轮到用户（原告）发言，等待用户输入')
      // 轮到用户发言，不需要生成AI回复
      return
    } else {
      console.log('[辩论流程] 用户是被告，下一个是原告（AI发言）')
      // 用户是被告，下一个是原告（AI发言）
      // 法官不发言，继续轮流发言，AI回复后需要检查法官（因为已经完成一轮）
      await generateAiResponse('plaintiff', '', false, true)
      return
    }
  }
  
  console.log('[辩论流程] 最后一条非法官消息 - 角色:', lastNonJudgeMessage.role)
  
  // 如果最后是原告发言，下一个是被告；反之亦然
  if (lastNonJudgeMessage.role === 'plaintiff') {
    console.log('[辩论流程] 最后是原告发言，下一个是被告')
    // 下一个是被告
    if (userIdentity.value === 'defendant') {
      console.log('[辩论流程] 轮到用户（被告）发言，等待用户输入')
      // 轮到用户发言，不需要生成AI回复
      return
    } else {
      console.log('[辩论流程] 用户是原告，下一个是被告（AI发言）')
      // 用户是原告，下一个是被告（AI发言）
      // 法官不发言，继续轮流发言，AI回复后需要检查法官（因为已经完成一轮）
      await generateAiResponse('defendant', '', false, true)
    }
  } else {
    console.log('[辩论流程] 最后是被告发言，下一个是原告')
    // 下一个是原告
    if (userIdentity.value === 'plaintiff') {
      console.log('[辩论流程] 轮到用户（原告）发言，等待用户输入')
      // 轮到用户发言，不需要生成AI回复
      return
    } else {
      console.log('[辩论流程] 用户是被告，下一个是原告（AI发言）')
      // 用户是被告，下一个是原告（AI发言）
      // 法官不发言，继续轮流发言，AI回复后需要检查法官（因为已经完成一轮）
      await generateAiResponse('plaintiff', '', false, true)
    }
  }
  console.log('[辩论流程] 继续原告和被告轮流发言 - 结束')
}

// 生成AI回复
const generateAiResponse = async (role, prompt, isFirstJudgeSpeech = false, shouldCheckJudgeAfter = false) => {
  console.log('[辩论流程] 生成AI回复 - 开始')
  console.log('[辩论流程] 参数 - role:', role, ', isFirstJudgeSpeech:', isFirstJudgeSpeech, ', shouldCheckJudgeAfter:', shouldCheckJudgeAfter)
  console.log('[辩论流程] 当前状态 - isGenerating:', isGenerating.value, ', currentSpeakingRole:', currentSpeakingRole.value)
  
  if (isGenerating.value) {
    console.log('[辩论流程] 正在生成中，跳过')
    return
  }
  
  isGenerating.value = true
  
  // 更新当前发言角色
  const roleName = role === 'judge' ? '法官' : (role === 'plaintiff' ? '原告' : '被告')
  currentSpeakingRole.value = roleName
  console.log('[辩论流程] 设置发言角色:', roleName)
  
  // 用于保存首次法官发言的文本，以便在 finally 块中使用
  let firstJudgeSpeechText = null
  
  try {
    // 准备消息历史（包含当前prompt作为上下文）
    const messageHistory = messages.value.map(msg => ({
      role: msg.role,
      name: msg.name,
      text: msg.text
    }))
    
    console.log('[辩论流程] 消息历史数量:', messageHistory.length)
    
    // 如果prompt不为空，添加一个临时消息作为上下文
    if (prompt) {
      messageHistory.push({
        role: role,
        name: role === 'judge' ? '法官' : (role === 'plaintiff' ? '原告' : '被告'),
        text: prompt
      })
      console.log('[辩论流程] 添加prompt到消息历史')
    }
    
    // 构建完整的background（包含所有庭前准备资料）
    const background = buildBackground()
    
    console.log('[辩论流程] 调用AI服务生成回复')
    const response = await request.post('/debate/generate', {
      userIdentity: userIdentity.value,
      currentRole: role,
      messages: messageHistory,
      judgeType: selectedJudgeType.value || 'neutral',
      caseDescription: background, // 使用完整的background，包含所有庭前准备资料
      opponentStrategy: opponentStrategy.value || 'balanced', // 对方AI律师的辩论策略
      isFirstJudgeSpeech: isFirstJudgeSpeech // 标记是否为首次法官发言
    }, {
      timeout: 0 // 取消超时限制，允许AI生成长时间运行
    })
    
    if (response.code === 200 && response.data) {
      const aiText = response.data
      const roleName = role === 'judge' ? '法官' : (role === 'plaintiff' ? '原告' : '被告')
      console.log('[辩论流程] AI生成成功，角色:', roleName, ', 内容长度:', aiText.length, ', 预览:', aiText.substring(0, 100))
      
      addMessage(role, roleName, aiText)
      
      // 如果是首次法官发言，保存文本以便后续处理
      if (isFirstJudgeSpeech && role === 'judge') {
        firstJudgeSpeechText = aiText
        console.log('[辩论流程] 保存首次法官发言文本')
      }
      
      // 检查是否应该结束庭审
      if (aiText.includes('休庭') || aiText.includes('评议') || aiText.includes('结束') || aiText.includes('合议庭')) {
        console.log('[辩论流程] 检测到庭审结束关键词，标记辩论完成')
        debateCompleted.value = true
        // 保存对话历史到localStorage，供判决书生成使用
        localStorage.setItem('debateMessages', JSON.stringify(messages.value))
        // 标记辩论完成
        localStorage.setItem('debateCompleted', 'true')
        // 立即保存到数据库（不等待防抖）
        if (caseStore.caseId) {
          clearTimeout(saveDebateMessagesTimer)
          await saveDebateMessages()
        }
        // 触发完成事件
        emit('complete')
      }
    } else {
      console.error('[辩论流程] AI服务返回错误:', response.message)
      ElMessage.error(response.message || '生成失败')
    }
  } catch (error) {
    console.error('[辩论流程] 生成AI回复失败:', error)
    ElMessage.error('生成失败，请重试: ' + (error.message || '未知错误'))
  } finally {
    console.log('[辩论流程] 重置生成状态')
    isGenerating.value = false
    currentSpeakingRole.value = '' // 发言结束，清空当前发言角色
    console.log('[辩论流程] 状态已重置 - isGenerating:', isGenerating.value, ', currentSpeakingRole:', currentSpeakingRole.value)
    
    // 如果是首次法官发言，发言后需要决定下一个发言人
    // 在 finally 块中调用，确保 isGenerating 已经重置
    if (isFirstJudgeSpeech && role === 'judge' && firstJudgeSpeechText) {
      console.log('[辩论流程] 首次法官发言完成，提取下一个发言人')
      // 使用 nextTick 确保在下一个事件循环中调用，避免阻塞
      await nextTick()
      // 从法官发言中提取下一个发言人
      await extractNextSpeakerFromJudgeSpeech(firstJudgeSpeechText)
    } else if (role === 'plaintiff' || role === 'defendant') {
      // 如果标记了需要检查法官（因为已经完成一轮：用户发言 + AI回复），直接检查法官
      if (shouldCheckJudgeAfter) {
        console.log('[辩论流程] AI回复完成，需要检查法官是否发言')
        await nextTick()
        await checkJudgeShouldSpeak()
      } else {
        console.log('[辩论流程] AI回复完成，等待用户发言')
        // AI（对方）发言后，下一个一定是用户，不检查法官，等待用户发言
        // 用户发言后会生成对方AI回复，然后检查法官
        // 所以这里什么都不做，直接返回
      }
    } else if (role === 'judge') {
      console.log('[辩论流程] 法官发言完成（非首次），状态已重置')
    }
    console.log('[辩论流程] 生成AI回复 - 结束')
  }
}

// 保存辩论消息到数据库（使用防抖）
const saveDebateMessages = async () => {
  if (!caseStore.caseId) {
    // 如果没有 caseId，无法保存
    return
  }
  
  try {
    const debateMessagesJson = JSON.stringify(messages.value)
    
    const caseData = {
      debateMessages: debateMessagesJson
    }
    
    await request.put(`/cases/${caseStore.caseId}`, caseData)
    // 静默保存，不显示成功消息，避免干扰用户
  } catch (error) {
    console.error('保存辩论消息失败:', error)
    // 静默失败，不显示错误消息，避免干扰用户
  }
}

// 防抖保存定时器
let saveDebateMessagesTimer = null

// 添加消息
const addMessage = (role, name, text) => {
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  
  messages.value.push({
    role,
    name,
    text,
    time
  })
  
  // 实时保存对话历史到localStorage
  localStorage.setItem('debateMessages', JSON.stringify(messages.value))
  
  // 保存到数据库（使用防抖，避免频繁请求）
  if (caseStore.caseId) {
    clearTimeout(saveDebateMessagesTimer)
    saveDebateMessagesTimer = setTimeout(() => {
      saveDebateMessages()
    }, 1000) // 1秒后保存
  }
  
  // 滚动到底部
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

// 判断是否轮到用户发言
const isUserTurn = computed(() => {
  if (!debateStarted.value || debateCompleted.value || isGenerating.value) {
    return false
  }
  
  // 获取最后一条消息
  if (messages.value.length === 0) {
    // 如果还没有消息，默认由法官开始，用户等待
    return false
  }
  
  const lastMessage = messages.value[messages.value.length - 1]
  const lastRole = lastMessage.role
  
  // 如果最后是法官发言，需要判断法官是否指定了下一个发言人
  if (lastRole === 'judge') {
    const judgeText = lastMessage.text
    // 检查法官是否指定了用户发言
    if (userIdentity.value === 'plaintiff') {
      return judgeText.includes('请原告') || judgeText.includes('原告继续') || judgeText.includes('原告发言')
    } else {
      return judgeText.includes('请被告') || judgeText.includes('被告继续') || judgeText.includes('被告发言')
    }
  }
  
  // 如果最后是对方发言，轮到用户发言
  const opponentRole = userIdentity.value === 'plaintiff' ? 'defendant' : 'plaintiff'
  if (lastRole === opponentRole) {
    return true
  }
  
  // 如果最后是用户自己发言，需要等待对方或法官
  if (lastRole === userIdentity.value) {
    return false
  }
  
  return false
})

// 获取下一个发言人的名称
const nextSpeakerName = computed(() => {
  if (!debateStarted.value || messages.value.length === 0) {
    return '法官'
  }
  
  const lastMessage = messages.value[messages.value.length - 1]
  const lastRole = lastMessage.role
  
  // 如果最后是法官发言，检查是否指定了下一个发言人
  if (lastRole === 'judge') {
    const judgeText = lastMessage.text
    if (judgeText.includes('请原告') || judgeText.includes('原告继续') || judgeText.includes('原告发言')) {
      return '原告'
    } else if (judgeText.includes('请被告') || judgeText.includes('被告继续') || judgeText.includes('被告发言')) {
      return '被告'
    }
  }
  
  // 如果最后是用户发言，下一个是对方
  if (lastRole === userIdentity.value) {
    return userIdentity.value === 'plaintiff' ? '被告' : '原告'
  }
  
  // 如果最后是对方发言，下一个应该是用户
  const opponentRole = userIdentity.value === 'plaintiff' ? 'defendant' : 'plaintiff'
  if (lastRole === opponentRole) {
    return userIdentity.value === 'plaintiff' ? '原告' : '被告'
  }
  
  return '法官'
})

// 生成判决结果
const generateVerdict = () => {
  router.push({
    name: 'courtroom',
    query: {
      ...route.query,
      tab: 'verdict'
    }
  })
}

// 重置庭审对话
const handleResetDebate = async () => {
  // 清空消息历史
  messages.value = []
  
  // 重置状态
  debateStarted.value = false
  debateCompleted.value = false
  userInput.value = ''
  currentSpeakingRole.value = ''
  isGenerating.value = false
  editingIndex.value = -1
  editingText.value = ''
  
  // 清除localStorage中的辩论记录
  try {
    localStorage.removeItem('debateMessages')
    localStorage.removeItem('debateCompleted')
  } catch (e) {
    console.error('清除localStorage失败:', e)
  }
  
  // 清除数据库中的辩论记录
  if (caseStore.caseId) {
    try {
      // 发送空字符串来清空数据库中的辩论消息字段
      const response = await request.put(`/cases/${caseStore.caseId}`, {
        debateMessages: '' // 设置为空字符串，清空数据库中的辩论消息
      })
      
      if (response.code === 200) {
        console.log('数据库辩论记录已清除')
        // 验证数据库是否真的被清空（可选，用于调试）
        if (response.data && response.data.debateMessages === '') {
          console.log('确认：数据库辩论记录已成功清空')
        }
      } else {
        console.warn('清除数据库辩论记录失败:', response.message)
        ElMessage.warning('本地记录已清除，但数据库更新失败，请刷新页面确认')
      }
    } catch (error) {
      console.error('清除数据库辩论记录失败:', error)
      // 即使数据库更新失败，localStorage已经清除，仍然提示成功
      // 但给用户一个警告提示
      ElMessage.warning('本地记录已清除，但数据库更新可能失败，请刷新页面确认')
    }
  }
  
  ElMessage.success('庭审现场已重置，可以重新开始庭审')
  
  // 滚动到顶部
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = 0
  }
}

// 监听路由变化，如果从其他页面进入且已选择法官类型，自动开始
// 初始化模型
const initModel = async () => {
  try {
    // 检查模型是否已加载
    const statusRes = await request.get('/debate/model/status')
    if (statusRes.code === 200 && statusRes.data?.loaded) {
      modelLoaded.value = true
      modelInitializing.value = false
      return
    }
    
    // 启动模型初始化
    modelInitializing.value = true
    modelLoaded.value = false
    modelInitError.value = null
    modelInitProgress.value = '正在启动模型初始化...'
    
    const initRes = await request.post('/debate/model/init')
    if (initRes.code === 200) {
      // 开始轮询状态
      pollModelStatus()
    } else {
      throw new Error(initRes.message || '初始化失败')
    }
  } catch (error) {
    console.error('模型初始化失败:', error)
    modelInitError.value = error.message || '初始化失败'
    modelInitializing.value = false
  }
}

// 轮询模型状态
const pollModelStatus = () => {
  if (modelStatusPollTimer.value) {
    clearInterval(modelStatusPollTimer.value)
  }
  
  modelStatusPollTimer.value = setInterval(async () => {
    try {
      const statusRes = await request.get('/debate/model/status')
      if (statusRes.code === 200 && statusRes.data) {
        const status = statusRes.data
        
        modelInitProgress.value = status.progress || ''
        modelInitProgressSteps.value = status.progress_steps || []
        modelInitError.value = status.error || null
        
        if (status.loaded) {
          modelLoaded.value = true
          modelInitializing.value = false
          if (modelStatusPollTimer.value) {
            clearInterval(modelStatusPollTimer.value)
            modelStatusPollTimer.value = null
          }
          ElMessage.success('AI模型初始化完成')
        } else if (status.error) {
          modelInitializing.value = false
          if (modelStatusPollTimer.value) {
            clearInterval(modelStatusPollTimer.value)
            modelStatusPollTimer.value = null
          }
        }
      }
    } catch (error) {
      console.error('获取模型状态失败:', error)
    }
  }, 1000) // 每秒轮询一次
}

// 加载辩论消息从数据库
const loadDebateMessages = async () => {
  if (!caseStore.caseId) {
    // 如果没有 caseId，尝试从 localStorage 恢复
    const savedMessages = localStorage.getItem('debateMessages')
    if (savedMessages) {
      try {
        messages.value = JSON.parse(savedMessages)
        // 如果加载了消息，说明辩论已开始
        if (messages.value.length > 0) {
          debateStarted.value = true
        }
      } catch (error) {
        console.error('从 localStorage 加载辩论消息失败:', error)
      }
    }
    return
  }
  
  try {
    const response = await request.get(`/cases/${caseStore.caseId}`)
    if (response.code === 200 && response.data) {
      const caseData = response.data
      
      // 如果有保存的辩论消息，恢复它们
      if (caseData.debateMessages) {
        try {
          messages.value = JSON.parse(caseData.debateMessages)
          // 如果加载了消息，说明辩论已开始
          if (messages.value.length > 0) {
            debateStarted.value = true
            // 同时保存到 localStorage 作为备份
            localStorage.setItem('debateMessages', caseData.debateMessages)
          }
        } catch (error) {
          console.error('解析辩论消息失败:', error)
          // 如果解析失败，尝试从 localStorage 恢复
          const savedMessages = localStorage.getItem('debateMessages')
          if (savedMessages) {
            try {
              messages.value = JSON.parse(savedMessages)
              if (messages.value.length > 0) {
                debateStarted.value = true
              }
            } catch (e) {
              console.error('从 localStorage 加载辩论消息失败:', e)
            }
          }
        }
      } else {
        // 如果没有保存的辩论消息，尝试从 localStorage 恢复
        const savedMessages = localStorage.getItem('debateMessages')
        if (savedMessages) {
          try {
            messages.value = JSON.parse(savedMessages)
            if (messages.value.length > 0) {
              debateStarted.value = true
            }
          } catch (error) {
            console.error('从 localStorage 加载辩论消息失败:', error)
          }
        }
      }
      
      // 检查是否已完成辩论
      const isCompleted = localStorage.getItem('debateCompleted') === 'true'
      if (isCompleted) {
        debateCompleted.value = true
      }
    }
  } catch (error) {
    console.error('加载辩论消息失败:', error)
    // 如果加载失败，尝试从 localStorage 恢复
    const savedMessages = localStorage.getItem('debateMessages')
    if (savedMessages) {
      try {
        messages.value = JSON.parse(savedMessages)
        if (messages.value.length > 0) {
          debateStarted.value = true
        }
      } catch (e) {
        console.error('从 localStorage 加载辩论消息失败:', e)
      }
    }
  }
}

// 监听路由变化，如果从其他页面进入且已选择法官类型，自动开始
onMounted(async () => {
  // 进入辩论阶段时，自动初始化模型
  initModel()
  
  // 加载辩论消息
  await loadDebateMessages()
})

// 组件卸载时清理定时器
onUnmounted(() => {
  if (modelStatusPollTimer.value) {
    clearInterval(modelStatusPollTimer.value)
    modelStatusPollTimer.value = null
  }
  
  // 清理保存定时器
  if (saveDebateMessagesTimer) {
    clearTimeout(saveDebateMessagesTimer)
    saveDebateMessagesTimer = null
  }
  
  // 组件卸载前，立即保存一次辩论消息（确保不丢失）
  if (caseStore.caseId && messages.value.length > 0) {
    saveDebateMessages()
  }
})
</script>

<style scoped>
.debate-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-title {
  font-size: 12px;
  color: #333;
  margin: 0;
  font-weight: 600;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.reset-debate-btn {
  font-size: 12px;
  padding: 6px 12px;
  height: auto;
}

/* 身份信息显示 */
.identity-display-section {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
}

.identity-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.identity-label {
  font-size: 16px;
  font-weight: 600;
  color: #409eff;
  padding: 8px 16px;
  background: white;
  border-radius: 6px;
  border-left: 4px solid #409eff;
}

/* 庭前准备材料查看 */
.pretrial-materials-section {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
}

.materials-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.toggle-btn {
  font-size: 12px;
  color: #409eff;
}

.materials-content {
  padding-top: 10px;
  border-top: 1px solid #e0e0e0;
}

.material-item {
  display: flex;
  margin-bottom: 12px;
  align-items: flex-start;
}

.material-item:last-child {
  margin-bottom: 0;
}

.material-label {
  font-size: 12px;
  font-weight: 600;
  color: #333;
  min-width: 80px;
  flex-shrink: 0;
}

.material-value {
  font-size: 12px;
  color: #666;
  flex: 1;
  line-height: 1.6;
}

.case-description {
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 200px;
  overflow-y: auto;
  padding: 8px;
  background: white;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
  font-size: 12px;
}

.file-item:last-child {
  margin-bottom: 0;
}

.file-icon {
  font-size: 14px;
}

/* 法官类型显示 */
.judge-display-section {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 15px;
}

.judge-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.judge-label {
  font-size: 16px;
  font-weight: 600;
  color: #409eff;
}

.judge-desc {
  font-size: 14px;
  color: #666;
}

/* 诉讼策略显示 */
.strategy-display-section {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 15px;
}

.strategy-card {
  background: white;
  border-radius: 6px;
  padding: 15px;
  border-left: 4px solid;
}

.plaintiff-strategy {
  border-left-color: #409eff;
}

.defendant-strategy {
  border-left-color: #f56c6c;
}

.strategy-label {
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
}

.plaintiff-strategy .strategy-label {
  color: #409eff;
}

.defendant-strategy .strategy-label {
  color: #f56c6c;
}

.strategy-content {
  font-size: 12px;
  color: #666;
  line-height: 1.6;
}

/* 庭审对话区域 */
.debate-chat-section {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 400px;
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  background: #ededed;
  border-radius: 6px;
  max-height: 600px;
  min-height: 400px;
}

.empty-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #999;
  font-size: 6px;
}

/* 模型初始化进度 */
.model-init-progress {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: #f5f7fa;
  border-radius: 8px;
  margin: 20px 0;
}

.progress-content {
  display: flex;
  align-items: center;
  gap: 20px;
  width: 100%;
  max-width: 600px;
}

.progress-icon {
  font-size: 32px;
  color: #409eff;
  flex-shrink: 0;
}

.progress-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.progress-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.progress-message {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.progress-tip {
  margin-top: 12px;
  font-size: 13px;
  color: #909399;
  font-style: italic;
}

.progress-error {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 12px;
  background: #fef0f0;
  border: 1px solid #fde2e2;
  border-radius: 6px;
  color: #f56c6c;
  font-size: 14px;
}

.message-item {
  margin-bottom: 11px;
  animation: fadeIn 0.3s ease-in;
  display: flex;
  width: 100%;
  box-sizing: border-box;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 原告：左边布局 */
.message-plaintiff {
  justify-content: flex-start;
  align-items: flex-start;
}

.message-plaintiff .message-avatar {
  flex-shrink: 0;
  margin-right: 6px;
}

.message-plaintiff .message-content-wrapper {
  flex: 1;
  max-width: 70%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.message-plaintiff .message-name {
  font-size: 7px;
  color: #999;
  margin-bottom: 3px;
}

.message-plaintiff .message-time {
  font-size: 6px;
  color: #999;
  margin-top: 3px;
  align-self: flex-start;
}

/* 法官：中间布局 */
.message-judge {
  justify-content: center;
  align-items: center;
}

.message-center-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 80%;
  margin: 0 auto;
}

.message-avatar-center {
  margin-bottom: 5px;
}

.message-content-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.message-name-center {
  font-size: 7px;
  color: #999;
  margin-bottom: 3px;
}

.message-time-center {
  font-size: 6px;
  color: #999;
  margin-top: 3px;
}

/* 被告：右边布局 */
.message-defendant {
  justify-content: flex-end;
  align-items: flex-start;
}

.message-defendant-wrapper {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: flex-end;
  width: 100%;
  gap: 6px;
}

.message-defendant-wrapper .message-content-wrapper {
  flex: 1;
  max-width: 70%;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message-defendant-wrapper .message-avatar {
  flex-shrink: 0;
  align-self: flex-start;
}

.message-defendant-wrapper .message-name-right {
  font-size: 7px;
  color: #999;
  margin-bottom: 3px;
  text-align: right;
}

.message-defendant-wrapper .message-time-right {
  font-size: 6px;
  color: #999;
  margin-top: 3px;
  text-align: right;
}

/* 头像样式 */
.avatar {
  width: 23px;
  height: 23px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  font-weight: 600;
  color: white;
  flex-shrink: 0;
}

.avatar-judge {
  background: linear-gradient(135deg, #e6a23c 0%, #ebb563 100%);
}

.avatar-plaintiff {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
}

.avatar-defendant {
  background: linear-gradient(135deg, #f56c6c 0%, #f89898 100%);
}

/* 消息气泡 */
.message-bubble {
  padding: 6px 8px;
  border-radius: 5px;
  font-size: 12px;
  color: #333;
  line-height: 1.4;
  word-wrap: break-word;
  position: relative;
  max-width: 100%;
  display: inline-block;
}

.message-bubble-left {
  background: #95ec69;
  border-radius: 5px 5px 5px 2px;
  align-self: flex-start;
}

.message-bubble-center {
  background: #fff7e6;
  border-radius: 5px;
  text-align: center;
  display: block;
  margin: 0 auto;
}

.message-bubble-right {
  background: #ffffff;
  border-radius: 5px 5px 2px 5px;
  align-self: flex-end;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.message-text {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  display: block;
}

/* 编辑功能 */
.edit-btn-wrapper {
  margin-top: 4px;
  text-align: right;
}

.message-bubble-left .edit-btn-wrapper {
  text-align: left;
}

.message-bubble-right .edit-btn-wrapper {
  text-align: right;
}

.edit-btn {
  font-size: 6px;
  padding: 2px 6px;
  height: auto;
  min-height: auto;
}

:deep(.edit-textarea .el-textarea__inner) {
  font-size: 6px;
  padding: 4px 6px;
  line-height: 1.4;
  overflow-y: visible !important;
  resize: none;
}

/* 用户输入区域 */
.input-section {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
}

/* AI代理和策略选择 */
.ai-proxy-section {
  margin-bottom: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.ai-proxy-switch {
  margin-bottom: 10px;
}

.strategy-selector {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
}

.strategy-label {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.strategy-option {
  padding: 4px 0;
}

.strategy-option-label {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.strategy-option-desc {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

/* 发言状态提示 */
.speaking-status {
  margin-bottom: 12px;
  padding: 10px 15px;
  border-radius: 6px;
  background: #f5f7fa;
  animation: fadeIn 0.3s ease-in;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
}

.status-icon {
  font-size: 16px;
  animation: pulse 1.5s ease-in-out infinite;
}

.status-generating {
  color: #e6a23c;
}

.status-generating .status-text {
  color: #e6a23c;
}

.status-user-turn {
  color: #409eff;
}

.status-user-turn .status-text {
  color: #409eff;
}

.status-waiting {
  color: #909399;
}

.status-waiting .status-text {
  color: #909399;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.user-input {
  width: 100%;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
}

/* 操作按钮 */
.action-section {
  text-align: center;
  padding: 20px 0;
}

.start-btn,
.generate-btn {
  width: 200px;
  height: 50px;
  font-size: 14px;
  font-weight: 600;
  border-radius: 6px;
}

.start-btn {
  background: #409eff;
  border-color: #409eff;
}

.start-btn:hover {
  background: #66b1ff;
  border-color: #66b1ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.start-btn:disabled {
  background: #c0c4cc;
  border-color: #c0c4cc;
  cursor: not-allowed;
}

.start-hint {
  margin-top: 12px;
  font-size: 14px;
  color: #e6a23c;
  text-align: center;
}

.generate-btn {
  background: #07c160;
  border-color: #07c160;
}

.generate-btn:hover {
  background: #06ad56;
  border-color: #06ad56;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(7, 193, 96, 0.3);
}
</style>

