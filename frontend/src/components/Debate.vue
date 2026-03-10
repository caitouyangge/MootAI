<template>
  <div class="debate-container">
    <!-- 顶部信息卡片网格 -->
    <div class="debate-info-grid">
      <!-- 身份信息显示 -->
      <div class="identity-display-section debate-card">
        <h3 class="section-title">身份</h3>
        <div class="identity-info">
          <span class="identity-label">{{ userIdentity === 'plaintiff' ? '公诉人' : '辩护人' }}</span>
        </div>
      </div>

      <!-- 审判员类型显示 -->
      <div class="judge-display-section debate-card">
        <h3 class="section-title">审判员类型</h3>
        <div class="judge-info">
          <span class="judge-label">{{ getJudgeLabel(selectedJudgeType) }}</span>
          <span class="judge-desc">{{ getJudgeDescription(selectedJudgeType) }}</span>
        </div>
      </div>

      <!-- 庭前准备材料（简洁文字展示，默认展开） -->
      <div class="pretrial-materials-section debate-card">
        <h3 class="section-title">庭前准备材料</h3>
        <div class="materials-content">
          <div class="material-item" v-if="caseDescription">
            <div class="material-label">案件描述：</div>
            <div class="material-value case-description">{{ caseDescription }}</div>
          </div>
          <div class="material-empty" v-else>
            暂无案件描述，请先在庭前准备阶段生成。
          </div>
        </div>
      </div>

      <!-- 对方AI律师策略显示 -->
      <div class="strategy-display-section debate-card">
        <h3 class="section-title">对方AI律师策略</h3>
        <div
          class="strategy-card"
          :class="userIdentity === 'plaintiff' ? 'defendant-strategy' : 'plaintiff-strategy'"
        >
          <div class="strategy-label">
            {{ userIdentity === 'plaintiff' ? '辩护人' : '公诉人' }}策略
          </div>
          <div class="strategy-content">
            {{ userIdentity === 'plaintiff' ? defendantStrategy : plaintiffStrategy }}
          </div>
        </div>
      </div>
    </div>

    <!-- 庭审对话区域 -->
    <div class="debate-chat-section debate-card" :class="{ 'debate-ended': isDebateEnded }">
      <div v-if="!isModelLoading" class="section-header">
        <h3 class="section-title">庭审现场</h3>
        <div v-if="debateStarted && messages.length > 0" class="header-actions">
          <el-button
            type="primary"
            size="small"
            class="copy-debate-btn"
            @click="copyDebateContent"
            :icon="DocumentCopy"
          >
            复制发言
          </el-button>
          <el-button
            type="warning"
            size="small"
            class="reset-debate-btn"
            @click="handleResetDebate"
            :icon="Refresh"
          >
            重置
          </el-button>
        </div>
      </div>
      <div v-if="!isModelLoading && isDebateEnded" class="debate-ended-notice">
        <div class="notice-icon">🔒</div>
        <div class="notice-text">法官已决定结束辩论，输入区域已隐藏。您仍可使用复制、重置、重新生成和编辑功能。使用这些功能将解除庭审结束状态。</div>
      </div>
      <div class="chat-container" ref="chatContainer">
        <!-- 模型初始化提示 -->
        <div v-if="isModelLoading" class="model-init-progress">
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
        <template v-else>
          <div v-if="messages.length === 0" class="empty-tip">
            <p>请点击"开始庭审"按钮开始模拟法庭辩论</p>
          </div>
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="['message-item', `message-${message.role}`]"
          >
          <!-- 公诉人：左边布局 -->
          <template v-if="message.role === 'plaintiff'">
            <div class="message-avatar">
              <div class="avatar avatar-plaintiff">原</div>
            </div>
            <div class="message-content-wrapper">
              <div class="message-name">{{ message.name }}</div>
              <div class="message-bubble message-bubble-left">
                <div v-if="editingIndex !== index" class="message-text">{{ message.text }}</div>
                <div v-else class="edit-container">
                  <el-input
                    v-model="editingText"
                    type="textarea"
                    :autosize="{ minRows: 1, maxRows: 50 }"
                    class="edit-textarea"
                  />
                  <div class="edit-actions">
                    <el-button
                      type="default"
                      size="small"
                      class="edit-action-btn"
                      @click="cancelEdit"
                    >
                      取消
                    </el-button>
                    <el-button
                      type="primary"
                      size="small"
                      class="edit-action-btn"
                      @click="resendMessage(index)"
                      :disabled="!editingText.trim()"
                    >
                      重新发送
                    </el-button>
                  </div>
                </div>
              </div>
              <div class="message-time">
                {{ message.time }}
                <span v-if="message.duration !== null && message.duration !== undefined" class="message-duration">
                  ({{ message.duration }}s)
                </span>
              </div>
              <!-- 编辑按钮：鼠标悬停时显示在消息下方 -->
              <div v-if="userIdentity === 'plaintiff' && editingIndex !== index && !isGenerating" class="edit-btn-wrapper">
                <el-button
                  text
                  type="primary"
                  size="default"
                  class="edit-btn"
                  @click="startEdit(index, message.text)"
                >
                  编辑
                </el-button>
              </div>
              <!-- 重新生成按钮：鼠标悬停时显示在消息下方（AI生成的消息） -->
              <div v-if="userIdentity !== 'plaintiff' && editingIndex !== index && !isGenerating" class="regenerate-btn-wrapper">
                <el-button
                  text
                  type="warning"
                  size="default"
                  class="regenerate-btn"
                  @click="regenerateAiMessage(index)"
                  :loading="isGenerating"
                >
                  重新生成
                </el-button>
              </div>
            </div>
          </template>

          <!-- 审判员：中间布局 -->
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
                <div class="message-time-center">
                  {{ message.time }}
                  <span v-if="message.duration !== null && message.duration !== undefined" class="message-duration">
                    ({{ message.duration }}s)
                  </span>
                </div>
                <!-- 重新生成按钮：鼠标悬停时显示在消息下方（审判员消息都是AI生成的） -->
                <div v-if="!isGenerating" class="regenerate-btn-wrapper regenerate-btn-center">
                  <el-button
                    text
                    type="warning"
                    size="default"
                    class="regenerate-btn"
                    @click="regenerateAiMessage(index)"
                    :loading="isGenerating"
                  >
                    重新生成
                  </el-button>
                </div>
              </div>
            </div>
          </template>

          <!-- 辩护人：右边布局 -->
          <template v-else-if="message.role === 'defendant'">
            <div class="message-defendant-wrapper">
              <div class="message-content-wrapper message-content-right">
                <div class="message-name message-name-right">{{ message.name }}</div>
                <div class="message-bubble message-bubble-right">
                  <div v-if="editingIndex !== index" class="message-text">{{ message.text }}</div>
                  <div v-else class="edit-container">
                    <el-input
                      v-model="editingText"
                      type="textarea"
                      :autosize="{ minRows: 1, maxRows: 50 }"
                      class="edit-textarea"
                    />
                    <div class="edit-actions">
                      <el-button
                        type="default"
                        size="small"
                        class="edit-action-btn"
                        @click="cancelEdit"
                      >
                        取消
                      </el-button>
                      <el-button
                        type="primary"
                        size="small"
                        class="edit-action-btn"
                        @click="resendMessage(index)"
                        :disabled="!editingText.trim()"
                      >
                        重新发送
                      </el-button>
                    </div>
                  </div>
                </div>
                <div class="message-time message-time-right">
                  {{ message.time }}
                  <span v-if="message.duration !== null && message.duration !== undefined" class="message-duration">
                    ({{ message.duration }}s)
                  </span>
                </div>
                <!-- 编辑按钮：鼠标悬停时显示在消息下方 -->
                <div v-if="userIdentity === 'defendant' && editingIndex !== index && !isGenerating" class="edit-btn-wrapper">
                  <el-button
                    text
                    type="primary"
                    size="default"
                    class="edit-btn"
                    @click="startEdit(index, message.text)"
                  >
                    编辑
                  </el-button>
                </div>
                <!-- 重新生成按钮：鼠标悬停时显示在消息下方（AI生成的消息） -->
                <div v-if="userIdentity !== 'defendant' && editingIndex !== index && !isGenerating" class="regenerate-btn-wrapper">
                  <el-button
                    text
                    type="warning"
                    size="default"
                    class="regenerate-btn"
                    @click="regenerateAiMessage(index)"
                    :loading="isGenerating"
                  >
                    重新生成
                  </el-button>
                </div>
              </div>
              <div class="message-avatar message-avatar-right">
                <div class="avatar avatar-defendant">被</div>
              </div>
            </div>
          </template>
          </div>
        </template>
      </div>
      
      <!-- 用户输入区域 -->
      <div v-if="!isModelLoading && debateStarted && !debateCompleted && !isDebateEnded" class="input-section">
        <!-- 发言状态提示 -->
        <div class="speaking-status">
          <div v-if="isGenerating" class="status-item status-generating">
            <span class="status-icon">⏳</span>
            <span class="status-text">{{ currentSpeakingRole }}正在思考中...</span>
          </div>
          <div v-else-if="isUserTurn" class="status-item status-user-turn">
            <span class="status-icon">💬</span>
            <span class="status-text">轮到您发言了（{{ userIdentity === 'plaintiff' ? '公诉人' : '辩护人' }}）</span>
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
            :placeholder="isUserTurn ? (useAiProxy ? '点击AI生成发言按钮生成内容，确认后点击发送' : `请输入您的发言（作为${userIdentity === 'plaintiff' ? '公诉人' : '辩护人'}）...`) : '请等待其他角色发言...'"
            class="user-input"
            :disabled="!isUserTurn || isGenerating"
            @keydown.ctrl.enter="sendMessage"
          />
          <div class="input-actions">
            <el-button
              v-if="useAiProxy && !isGenerating"
              type="default"
              :loading="isGenerating"
              :disabled="!isUserTurn || isGenerating"
              @click="generateUserAiResponse"
            >
              {{ isGenerating ? '生成中...' : 'AI生成发言' }}
            </el-button>
            <el-button
              v-if="!isGenerating"
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
        请先在庭前准备阶段完成审判员类型和策略选择
      </p>
      <el-button
        v-if="debateCompleted || isDebateEnded"
        type="primary"
        size="large"
        class="generate-btn"
        @click="generateVerdict"
      >
        生成庭后宣判
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading, Warning, Refresh, DocumentCopy } from '@element-plus/icons-vue'
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

// 审判员类型（从store读取）
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

const selectedJudgeType = ref(caseStore.selectedJudgeType || 'professional')
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
    // 用户是公诉人，对方是辩护人
    defendantStrategy.value = strategyDefinitions[opponentStrategy.value] || strategyDefinitions.balanced
    plaintiffStrategy.value = '均衡策略：主张适中，准备充分的证据，但不过度激化矛盾。保持协商空间，平衡攻守。'
  } else {
    // 用户是辩护人，对方是公诉人
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
const isDebateEnded = ref(false) // 法官决定结束辩论
const chatContainer = ref(null)
const judgeSkipCount = ref(0) // 审判员跳过次数

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

// 取消编辑
const cancelEdit = () => {
  editingIndex.value = -1
  editingText.value = ''
}

// 保存编辑（仅保存，不重新发送）
const saveEdit = async (index) => {
  if (editingIndex.value === index && editingText.value.trim()) {
    messages.value[index].text = editingText.value.trim()
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

// 重新发送编辑后的消息
const resendMessage = async (index) => {
  if (editingIndex.value !== index || !editingText.value.trim()) {
    return
  }
  
  // 如果辩论已结束，解除结束状态
  if (isDebateEnded.value || debateCompleted.value) {
    isDebateEnded.value = false
    debateCompleted.value = false
    localStorage.removeItem('debateCompleted')
    localStorage.removeItem('isDebateEnded')
    ElMessage.info('已解除庭审结束状态，可以继续辩论')
  }
  
  // 更新消息内容
  messages.value[index].text = editingText.value.trim()
  
  // 删除该消息之后的所有消息
  const deletedCount = messages.value.length - index - 1
  if (deletedCount > 0) {
    messages.value.splice(index + 1, deletedCount)
    console.log(`[编辑重发] 删除了 ${deletedCount} 条后续消息`)
  }
  
  // 退出编辑模式
  editingIndex.value = -1
  editingText.value = ''
  
  // 保存到localStorage
  localStorage.setItem('debateMessages', JSON.stringify(messages.value))
  
  // 保存到数据库
  if (caseStore.caseId) {
    clearTimeout(saveDebateMessagesTimer)
    await saveDebateMessages()
  }
  
  ElMessage.success('消息已重新发送，后续对话已删除')
  
  // 从该消息处继续辩论流程
  await nextTick()
  
  // 获取编辑的消息角色
  const editedMessage = messages.value[index]
  const editedRole = editedMessage.role
  
  // 如果编辑的是用户自己的消息，继续正常的辩论流程
  if (editedRole === userIdentity.value) {
    console.log('[编辑重发] 用户消息已重新发送，继续辩论流程')
    // 重置状态
    isGenerating.value = false
    currentSpeakingRole.value = ''
    // 继续辩论流程（检查审判员是否需要介入，或继续轮流发言）
    await checkJudgeShouldSpeak()
  } else {
    // 如果编辑的是AI消息（理论上不应该发生，但为了完整性处理）
    console.log('[编辑重发] AI消息已重新发送，继续辩论流程')
    isGenerating.value = false
    currentSpeakingRole.value = ''
    await checkJudgeShouldSpeak()
  }
}

// 重新生成AI消息
const regenerateAiMessage = async (index) => {
  // 如果辩论已结束，解除结束状态
  if (isDebateEnded.value || debateCompleted.value) {
    isDebateEnded.value = false
    debateCompleted.value = false
    localStorage.removeItem('debateCompleted')
    localStorage.removeItem('isDebateEnded')
    ElMessage.info('已解除庭审结束状态，可以继续辩论')
  }
  
  // 如果正在生成中，不允许重新生成
  if (isGenerating.value) {
    ElMessage.warning('正在生成中，请稍候')
    return
  }
  
  const message = messages.value[index]
  const messageRole = message.role
  
  // 只允许重新生成AI消息（审判员、对方AI律师的消息）
  if (messageRole === userIdentity.value) {
    ElMessage.warning('只能重新生成AI生成的消息')
    return
  }
  
  // 删除该消息及之后的所有消息
  const deletedCount = messages.value.length - index
  if (deletedCount > 0) {
    messages.value.splice(index, deletedCount)
    console.log(`[重新生成] 删除了 ${deletedCount} 条消息（包括当前消息）`)
  }
  
  // 保存到localStorage
  localStorage.setItem('debateMessages', JSON.stringify(messages.value))
  
  // 保存到数据库
  if (caseStore.caseId) {
    clearTimeout(saveDebateMessagesTimer)
    await saveDebateMessages()
  }
  
  ElMessage.success('正在重新生成消息...')
  
  // 等待DOM更新
  await nextTick()
  
  // 重新生成该消息
  console.log(`[重新生成] 重新生成角色 ${messageRole} 的消息`)
  
  // 根据角色重新生成
  if (messageRole === 'judge') {
    // 审判员消息：直接生成（不检查是否需要发言，因为用户明确要求重新生成）
    await generateAiResponse('judge', '', false, false)
  } else {
    // AI律师消息：直接生成
    await generateAiResponse(messageRole, '', false, false)
  }
}

// 开始庭审
const startDebate = async () => {
  console.log('[辩论流程] 开始庭审 - 开始')
  console.log('[辩论流程] 审判员类型:', selectedJudgeType.value, ', 对方策略:', opponentStrategy.value)
  
  if (!selectedJudgeType.value) {
    ElMessage.warning('请先在庭前准备阶段选择审判员类型')
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
  
  // 审判员宣布开始（使用固定文本，避免AI生成不同内容）
  const firstJudgeSpeech = '现在开庭。请公诉人陈述诉讼请求和事实理由。'
  console.log('[辩论流程] 添加首次审判员发言（固定文本）')
  
  // 直接添加审判员消息，不使用AI生成
  addMessage('judge', '审判员', firstJudgeSpeech)
  
  // 立即保存到数据库
  if (caseStore.caseId) {
    clearTimeout(saveDebateMessagesTimer)
    await saveDebateMessages()
  }
  
  // 审判员发言后，继续正常的发言顺序
  console.log('[辩论流程] 首次审判员发言完成，继续正常的发言顺序')
  await nextTick() // 确保消息已添加
  await extractNextSpeakerFromJudgeSpeech(firstJudgeSpeech)
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
  const userRoleName = userIdentity.value === 'plaintiff' ? '公诉人' : '辩护人'
  currentSpeakingRole.value = userRoleName
  console.log('[辩论流程] 设置用户发言角色:', userRoleName)
  
  // 添加用户消息
  addMessage(userIdentity.value, userRoleName, userText)
  
  // 用户发言结束
  currentSpeakingRole.value = ''
  console.log('[辩论流程] 用户发言完成，清空发言角色')
  
  // 每次发言结束后，都检查审判员是否需要介入
  // checkJudgeShouldSpeak 内部会判断是否满足硬性条件（距离上次审判员发言后，至少完成一轮）
  await checkJudgeShouldSpeak()
  console.log('[辩论流程] 用户发送消息 - 结束')
}

// 生成用户AI代理回复（生成到输入框，不直接发送）
const generateUserAiResponse = async () => {
  if (isGenerating.value) return
  
  isGenerating.value = true
  
  // 更新当前发言角色为用户
  const roleName = userIdentity.value === 'plaintiff' ? '公诉人' : '辩护人'
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
  
  // 案件描述
  if (caseDescription.value) {
    background += `${caseDescription.value}\n\n`
  }
  
  return background
}

// 检查审判员是否应该发言
const checkJudgeShouldSpeak = async () => {
  console.log('[辩论流程] 检查审判员是否应该发言 - 开始')
  console.log('[辩论流程] 当前状态 - isGenerating:', isGenerating.value, ', currentSpeakingRole:', currentSpeakingRole.value)
  console.log('[辩论流程] 消息数量:', messages.value.length)
  
  // 如果辩论已结束，不再检查
  if (isDebateEnded.value || debateCompleted.value) {
    console.log('[辩论流程] 辩论已结束，不再检查审判员发言')
    return
  }
  
  if (isGenerating.value) {
    console.log('[辩论流程] 正在生成中，跳过检查')
    return
  }
  
  // 如果最后一条消息是审判员发言，说明审判员刚刚发言了，应该继续正常的发言顺序
  // 这种情况不应该进入这个函数，但如果进入了，应该直接继续正常发言顺序
  if (messages.value.length > 0) {
    const lastMessage = messages.value[messages.value.length - 1]
    console.log('[辩论流程] 最后一条消息 - 角色:', lastMessage.role, ', 内容预览:', lastMessage.text.substring(0, 50))
    
    if (lastMessage.role === 'judge') {
      console.log('[辩论流程] 最后是审判员发言，继续正常的发言顺序')
      // 最后是审判员发言，继续正常的发言顺序
      // 注意：这里不需要设置isGenerating，因为审判员已经发言完成
      await extractNextSpeakerFromJudgeSpeech(lastMessage.text)
      console.log('[辩论流程] 继续正常发言顺序完成')
      return
    }
  }
  
  // 设置生成状态，防止在审判员思考时显示"轮到用户发言"
  console.log('[辩论流程] 设置审判员发言状态')
  isGenerating.value = true
  currentSpeakingRole.value = '审判员'
  
  // 检查是否满足硬性条件：距离上一次审判员发言，至少已经有两条消息（构成一轮）
  // 找到最后一次审判员发言的位置
  let lastJudgeIndex = -1
  for (let i = messages.value.length - 1; i >= 0; i--) {
    if (messages.value[i].role === 'judge') {
      lastJudgeIndex = i
      break
    }
  }
  
  // 获取距离上次审判员发言后的所有非审判员消息
  const messagesAfterLastJudge = messages.value.slice(lastJudgeIndex + 1).filter(m => m.role !== 'judge')
  console.log('[辩论流程] 距离上次审判员发言后的非审判员消息数:', messagesAfterLastJudge.length)
  
  // 硬性要求：必须距离上一次审判员发言后，至少已经有两条消息（构成一轮）
  if (messagesAfterLastJudge.length < 2) {
    console.log('[辩论流程] 距离上次审判员发言后，只有', messagesAfterLastJudge.length, '条消息，不满足硬性条件（至少完成一轮），跳过审判员检查')
    isGenerating.value = false
    currentSpeakingRole.value = ''
    await continueAlternatingDebate()
    return
  }
  
  // 检查最后两条消息是否构成一轮（公诉人+辩护人或辩护人+公诉人）
  const lastMessage = messagesAfterLastJudge[messagesAfterLastJudge.length - 1]
  const secondLastMessage = messagesAfterLastJudge[messagesAfterLastJudge.length - 2]
  
  const isCompleteRound = 
    (lastMessage.role === 'plaintiff' && secondLastMessage.role === 'defendant') ||
    (lastMessage.role === 'defendant' && secondLastMessage.role === 'plaintiff')
  
  if (!isCompleteRound) {
    console.log('[辩论流程] 距离上次审判员发言后，最后两条消息不构成一轮（公诉人+辩护人），不满足硬性条件，跳过审判员检查')
    console.log('[辩论流程] 最后一条:', lastMessage.role, ', 前一条:', secondLastMessage.role)
    isGenerating.value = false
    currentSpeakingRole.value = ''
    await continueAlternatingDebate()
    return
  }
  
  // 满足硬性条件，可以判断
  console.log('[辩论流程] 满足硬性条件（距离上次审判员发言后，至少完成一轮：' + secondLastMessage.role + '->' + lastMessage.role + '），开始判断审判员是否需要介入')
  
  // 获取最后一条非审判员消息，确定下一个发言人
  const lastNonJudgeMessage = [...messages.value].reverse().find(m => m.role !== 'judge')
  let nextSpeakerHint = ''
  if (lastNonJudgeMessage) {
    if (lastNonJudgeMessage.role === 'plaintiff') {
      nextSpeakerHint = '\n\n【当前发言顺序】最后是公诉人发言，下一个应该发言的是辩护人。如果你需要提问或引导，应该针对辩护人，而不是公诉人。'
    } else if (lastNonJudgeMessage.role === 'defendant') {
      nextSpeakerHint = '\n\n【当前发言顺序】最后是辩护人发言，下一个应该发言的是公诉人。如果你需要提问或引导，应该针对公诉人，而不是辩护人。'
    }
  }
  
  // 检查是否有辩护人或公诉人表示不再重复
  const hasNoMoreSpeech = messages.value.some(msg => {
    if (msg.role === 'plaintiff' || msg.role === 'defendant') {
      const text = msg.text || ''
      return text.includes('不再重复') || 
             text.includes('已表达相关观点') || 
             text.includes('不再重复观点') ||
             text.includes('无其他补充')
    }
    return false
  })
  
  // 构建判断提示词
  let judgeCheckPrompt = `根据当前的庭审对话历史，请判断作为审判员，你是否需要发言。

【重要】庭审全程处于法庭辩论阶段，直到你宣布结束。发言顺序：公诉人先发言，然后辩护人发言，每完成一轮（公诉人+辩护人）后，你判断是否需要介入。${nextSpeakerHint}`

  // 如果检测到有角色表示不再重复，增加特殊提示
  if (hasNoMoreSpeech) {
    judgeCheckPrompt += `

【特别提醒】检测到辩护人或公诉人已经表示"不再重复"或"已表达相关观点"。此时：
- 如果双方都已经充分表达观点，你应该考虑结束辩论阶段，宣布进入评议或休庭
- 绝对禁止继续重复要求同一方发言（如反复说"请公诉人发表公诉意见"）
- 如果确实需要补充提问，应该针对新的争议点，而不是重复之前的要求
- 如果双方观点已经充分表达，建议直接输出"不需要发言"或宣布结束辩论`
  }

  judgeCheckPrompt += `

【绝对禁止的阶段转换语】
如果对话历史不为空，说明庭审已经开始了，你绝对不能再重复说以下任何内容：
- "现在开庭"、"开庭"
- "法庭辩论阶段开始"、"开始法庭辩论"、"现在开始法庭辩论"、"进入法庭辩论阶段"、"现在进入法庭辩论"
- "进入最后陈述环节"、"现在进入最后陈述环节"、"最后陈述阶段"
- "现在进行法庭辩论"、"进入法庭辩论"
- "辩论结束"（除非你真的要结束庭审）
- 任何包含"开始"、"开庭"、"进入"、"阶段"等表示阶段转换的词语

【指定发言人规则】
如果你想指定下一个发言人，必须使用以下格式：
- "请公诉人发言"
- "请辩护人发言"
只有使用这种明确格式，系统才会执行你的指令。其他任何形式的指定（如"请被告人申晓发表最后陈述"）都不会被执行。

【绝对禁止重复】
绝对禁止重复之前已经说过的内容，特别是：
- 禁止重复说"请公诉人发表公诉意见"、"请辩护人发言"等相同或类似的指令
- 如果之前已经说过"请XX发言"，绝对不能再重复说相同的话
- 每次发言必须有不同的内容或角度。如果检测到重复发言，系统将拒绝你的发言。

你应该根据对话历史，直接进行必要的介入（如归纳争议焦点、纠正程序错误等），不要说重复的套话。如果违反此规定，系统将拒绝你的发言。

【介入条件】只有在以下情况才需要介入：
- 需要归纳争议焦点时
- 需要纠正程序错误时
- 需要制止不当言论时
- 需要引导辩论方向时
- 辩论结束时（宣布休庭、评议等）

【重要原则】
1. 非必要不介入，不说废话。如果双方辩论正常进行，没有程序问题，没有需要纠正的地方，就不要发言。
2. 如果需要发言，发言内容必须简洁、专业、有针对性，不要说套话、空话。如果不指定发言人，发言顺序由系统自动管理，公诉人和辩护人会按照正常顺序轮流发言。
3. 绝对禁止重复之前已经说过的内容。每次发言必须提出新的观点、从不同角度分析，或者针对新的争议点进行归纳。
4. 如果不需要发言，请只输出"不需要发言"，然后由公诉人和辩护人继续轮流发言。`
  
  // 记录开始时间
  const startTime = Date.now()
  
  try {
    const messageHistory = messages.value.map(msg => ({
      role: msg.role,
      name: msg.name,
      text: msg.text
    }))
    
    console.log('[辩论流程] 调用AI服务判断审判员是否需要发言')
    const response = await request.post('/debate/generate', {
      userIdentity: userIdentity.value,
      currentRole: 'judge',
      messages: messageHistory,
      judgeType: selectedJudgeType.value || 'neutral',
      caseDescription: buildBackground(), // 使用完整的background
      checkMode: true, // 标记为判断模式
      prompt: judgeCheckPrompt,
      judge_skip_count: judgeSkipCount.value // 传递跳过次数
    }, {
      timeout: 0
    })
    
    // 计算耗时
    const endTime = Date.now()
    const duration = ((endTime - startTime) / 1000).toFixed(2) // 转换为秒，保留2位小数
    
    if (response.code === 200 && response.data) {
      // 更新跳过计数（如果响应中包含）
      if (response.judge_skip_count !== undefined) {
        judgeSkipCount.value = response.judge_skip_count
        console.log('[辩论流程] 更新审判员跳过次数:', judgeSkipCount.value)
      }
      
      // 检查是否为硬编码结束
      if (response.is_hardcoded) {
        console.log('[辩论流程] 审判员跳过次数达到3次，使用硬编码结束语')
        const hardcodedEnding = response.data.trim()
        addMessage('judge', '审判员', hardcodedEnding, parseFloat(duration))
        // 标记辩论已结束
        isDebateEnded.value = true
        debateCompleted.value = true
        return
      }
      
      let judgeResponse = response.data.trim()
      console.log('[辩论流程] AI返回审判员响应，长度:', judgeResponse.length, ', 耗时:', duration, '秒, 预览:', judgeResponse.substring(0, 100))
      
      // 检查是否为跳过发言
      const isSkipped = response.is_skipped === true || judgeResponse.includes('不需要发言')
      
      if (isSkipped) {
        console.log('[辩论流程] 审判员跳过此次发言（角色混淆检测失败），继续轮流发言')
        console.log('[辩论流程] 当前跳过次数:', judgeSkipCount.value)
        // 审判员跳过发言，由公诉人和辩护人轮流发言
        // 确保状态正确重置
        isGenerating.value = false
        currentSpeakingRole.value = ''
        await continueAlternatingDebate()
        return
      }
      
      // 检查并过滤禁止的短语（如果对话历史不为空）
      if (messages.value.length > 0) {
        const forbiddenPhrases = [
          '现在开庭',
          '开庭',
          '法庭辩论阶段开始',
          '现在开始',
          '开始法庭辩论',
          '进入法庭辩论阶段',
          '现在进入法庭辩论',
          '进入最后陈述环节',
          '现在进入最后陈述环节',
          '最后陈述阶段',
          '最后陈述',
          '发表最后陈述',
          '进行最后陈述',
          '现在进行法庭辩论',
          '进入法庭辩论'
        ]
        
        // 特殊处理：如果包含"最后陈述"相关短语，说明AI错误地提到了不存在的环节
        // 这种情况下，如果同时包含结束关键词，应该直接结束辩论
        const lastStatementPhrases = ['最后陈述', '进入最后陈述环节', '现在进入最后陈述环节', '最后陈述阶段', '发表最后陈述', '进行最后陈述']
        const hasLastStatement = lastStatementPhrases.some(phrase => judgeResponse.includes(phrase))
        const endKeywords = ['休庭', '评议', '结束', '合议庭', '尾声', '作出裁判', '依法作出裁判', '依法对本案作出裁判', '作出公正判决', '作出判决', '庭审结束', '辩论结束', '法庭辩论结束']
        const hasEndKeyword = endKeywords.some(keyword => judgeResponse.includes(keyword))
        
        if (hasLastStatement) {
          console.warn('[辩论流程] 检测到AI错误地提到了"最后陈述环节"（系统不存在此环节）')
          if (hasEndKeyword) {
            // 如果同时包含结束关键词，说明AI想结束，但错误地提到了最后陈述
            // 过滤掉最后陈述相关内容，保留结束相关内容
            console.warn('[辩论流程] 同时包含结束关键词，过滤掉"最后陈述"相关内容，保留结束内容')
            const sentences = judgeResponse.split(/[。！？\n]/)
            judgeResponse = sentences
              .filter(s => !lastStatementPhrases.some(fp => s.includes(fp)))
              .join('。')
              .trim()
            // 如果过滤后为空或太短，说明没有有效的结束内容，需要添加总结
            if (!judgeResponse || judgeResponse.length < 50) {
              console.warn('[辩论流程] 过滤后内容过短，说明缺少总结，需要重新生成或添加总结')
              // 这种情况下，如果包含结束关键词，应该结束，但需要提醒缺少总结
              // 为了不影响流程，我们保留一个简短的结束语
              judgeResponse = '综合全案事实、证据及双方辩论意见，本庭认为案件事实清楚，证据确实充分。现宣布法庭辩论结束，将择日宣判。'
            }
          } else {
            // 只包含最后陈述，不包含结束关键词，说明AI想进入不存在的环节
            // 过滤掉最后陈述相关内容
            console.warn('[辩论流程] 过滤掉"最后陈述"相关内容')
            const sentences = judgeResponse.split(/[。！？\n]/)
            judgeResponse = sentences
              .filter(s => !lastStatementPhrases.some(fp => s.includes(fp)))
              .join('。')
              .trim()
            // 如果过滤后为空，则设置为不需要发言
            if (!judgeResponse) {
              judgeResponse = '不需要发言'
            }
          }
        } else {
          // 正常过滤其他禁止短语
          for (const phrase of forbiddenPhrases) {
            if (judgeResponse.includes(phrase)) {
              console.warn('[辩论流程] 检测到禁止的短语:', phrase, '，自动过滤')
              // 移除包含禁止短语的句子
              const sentences = judgeResponse.split(/[。！？\n]/)
              judgeResponse = sentences
                .filter(s => !forbiddenPhrases.some(fp => s.includes(fp)))
                .join('。')
                .trim()
              // 如果过滤后为空，则设置为不需要发言
              if (!judgeResponse) {
                judgeResponse = '不需要发言'
              }
              break
            }
          }
        }
      }
      
      // 判断审判员是否发言（如果包含"不需要发言"，则不发言）
      if (judgeResponse && !judgeResponse.includes('不需要发言')) {
        console.log('[辩论流程] 审判员决定发言，添加消息')
        // 审判员发言
        addMessage('judge', '审判员', judgeResponse, parseFloat(duration))
        
        // 检查是否应该结束庭审（法官决定结束）
        // 检测更多表示结束的关键词：休庭、评议、结束、合议庭、尾声、作出裁判、依法作出裁判等
        const endKeywords = ['休庭', '评议', '结束', '合议庭', '尾声', '作出裁判', '依法作出裁判', '依法对本案作出裁判', '作出公正判决', '作出判决', '庭审结束', '辩论结束', '法庭辩论结束']
        const shouldEndDebate = endKeywords.some(keyword => judgeResponse.includes(keyword))
        
        if (shouldEndDebate) {
          console.log('[辩论流程] 检测到法官决定结束庭审，标记辩论结束')
          isDebateEnded.value = true
          debateCompleted.value = true
          // 保存对话历史到localStorage，供判决书生成使用
          localStorage.setItem('debateMessages', JSON.stringify(messages.value))
          // 标记辩论完成
          localStorage.setItem('debateCompleted', 'true')
          localStorage.setItem('isDebateEnded', 'true')
          // 立即保存到数据库（不等待防抖）
          if (caseStore.caseId) {
            clearTimeout(saveDebateMessagesTimer)
            await saveDebateMessages()
          }
          // 触发完成事件
          emit('complete')
          ElMessage.info('法官已决定结束辩论，庭审现场已锁定，请点击"生成庭后宣判"按钮')
          // 重置状态并返回，不再继续流程
          isGenerating.value = false
          currentSpeakingRole.value = ''
          return
        }
        
        console.log('[辩论流程] 审判员发言完成，继续正常的发言顺序')
        // 审判员发言后，继续正常的发言顺序
        // 注意：在extractNextSpeakerFromJudgeSpeech中可能会调用generateAiResponse，会设置新的状态
        await extractNextSpeakerFromJudgeSpeech(judgeResponse)
        console.log('[辩论流程] 继续正常发言顺序完成')
      } else {
        console.log('[辩论流程] 审判员决定不发言，继续轮流发言')
        // 审判员不发言，由公诉人和辩护人轮流发言
        // 确保状态正确重置
        isGenerating.value = false
        currentSpeakingRole.value = ''
        await continueAlternatingDebate()
      }
    } else {
      console.error('[辩论流程] AI服务返回错误:', response.message)
    }
  } catch (error) {
    console.error('[辩论流程] 审判员判断失败:', error)
    // 如果判断失败，默认继续轮流发言
    // 确保状态正确重置
    isGenerating.value = false
    currentSpeakingRole.value = ''
    await continueAlternatingDebate()
  } finally {
    // 重置生成状态和发言角色
    // 注意：如果extractNextSpeakerFromJudgeSpeech中调用了generateAiResponse，那个函数会设置新的状态
    // 所以这里需要确保状态被正确重置
    // 但如果已经调用了continueAlternatingDebate，状态可能已经被重置，这里再次确保
    if (isGenerating.value) {
      console.log('[辩论流程] 重置审判员发言状态')
      isGenerating.value = false
      currentSpeakingRole.value = ''
    }
    console.log('[辩论流程] 检查审判员是否应该发言 - 结束，状态已重置')
  }
}

// 从审判员发言中提取下一个发言人（支持"请XX发言"格式）
const extractNextSpeakerFromJudgeSpeech = async (judgeSpeech) => {
  console.log('[辩论流程] 审判员发言完成，解析发言人指令 - 开始')
  console.log('[辩论流程] 审判员发言内容预览:', judgeSpeech.substring(0, 200))
  console.log('[辩论流程] 用户身份:', userIdentity.value)
  
  // 如果辩论已结束，不再继续
  if (isDebateEnded.value || debateCompleted.value) {
    console.log('[辩论流程] 辩论已结束，不再继续发言流程')
    return
  }
  
  // 确保状态已重置
  isGenerating.value = false
  currentSpeakingRole.value = ''
  console.log('[辩论流程] 重置状态 - isGenerating:', isGenerating.value, ', currentSpeakingRole:', currentSpeakingRole.value)
  
  // 解析审判员发言中的"请XX发言"指令
  // 匹配格式：请公诉人发言、请辩护人发言
  const speechPattern = /请(公诉人|辩护人)发言/g
  const matches = judgeSpeech.match(speechPattern)
  
  if (matches && matches.length > 0) {
    // 取最后一个匹配（如果有多处提到）
    const lastMatch = matches[matches.length - 1]
    let targetRole = null
    
    if (lastMatch.includes('公诉人')) {
      targetRole = 'plaintiff'
      console.log('[辩论流程] 检测到审判员指定：请公诉人发言')
    } else if (lastMatch.includes('辩护人')) {
      targetRole = 'defendant'
      console.log('[辩论流程] 检测到审判员指定：请辩护人发言')
    }
    
    if (targetRole) {
      // 执行审判员的指定
      await nextTick() // 确保状态更新已生效
      
      if (userIdentity.value === targetRole) {
        // 指定的是用户，等待用户发言
        console.log('[辩论流程] 审判员指定用户发言，等待用户输入')
        return
      } else {
        // 指定的是AI，生成AI回复
        console.log('[辩论流程] 审判员指定AI发言，生成回复')
        await generateAiResponse(targetRole, '', false, false)
        return
      }
    }
  }
  
  // 如果没有检测到明确的"请XX发言"指令，按照正常发言顺序继续
  console.log('[辩论流程] 未检测到明确的发言人指定，按照正常发言顺序继续')
  await nextTick() // 确保状态更新已生效
  await continueAlternatingDebate()
  console.log('[辩论流程] 继续正常发言顺序 - 结束')
}

// 决定下一个发言人（审判员发言后调用）
const decideNextSpeaker = async () => {
  // 获取最后一条消息的角色
  const lastMessage = messages.value[messages.value.length - 1]
  const lastRole = lastMessage.role
  
  // 如果最后是审判员发言，根据对话历史决定下一个发言人
  if (lastRole === 'judge') {
    // 简单逻辑：如果最后是公诉人发言，下一个是辩护人；反之亦然
    const plaintiffMessages = messages.value.filter(m => m.role === 'plaintiff')
    const defendantMessages = messages.value.filter(m => m.role === 'defendant')
    
    if (plaintiffMessages.length <= defendantMessages.length) {
      // 公诉人发言次数少，下一个是公诉人
      if (userIdentity.value === 'plaintiff') {
        // 轮到用户发言，不需要生成AI回复
        return
      } else {
        // 用户是辩护人，下一个是公诉人（AI发言）
        // 审判员发言后，AI回复后不检查审判员，等待用户发言
        await generateAiResponse('plaintiff', '', false, false)
      }
    } else {
      // 辩护人发言次数少，下一个是辩护人
      if (userIdentity.value === 'defendant') {
        // 轮到用户发言，不需要生成AI回复
        return
      } else {
        // 用户是公诉人，下一个是辩护人（AI发言）
        // 审判员发言后，AI回复后不检查审判员，等待用户发言
        await generateAiResponse('defendant', '', false, false)
      }
    }
  }
}

// 继续公诉人和辩护人轮流发言
const continueAlternatingDebate = async () => {
  console.log('[辩论流程] 继续公诉人和辩护人轮流发言 - 开始')
  
  // 如果辩论已结束，不再继续
  if (isDebateEnded.value || debateCompleted.value) {
    console.log('[辩论流程] 辩论已结束，不再继续发言流程')
    return
  }
  
  // 获取最后一条非审判员消息的角色
  const lastNonJudgeMessage = [...messages.value].reverse().find(m => m.role !== 'judge')
  
  if (!lastNonJudgeMessage) {
    console.log('[辩论流程] 没有非审判员消息，判断下一个发言人')
    // 如果没有非审判员消息，判断下一个应该是谁
    // 如果用户是公诉人，下一个应该是公诉人（用户发言）
    if (userIdentity.value === 'plaintiff') {
      console.log('[辩论流程] 轮到用户（公诉人）发言，等待用户输入')
      // 确保状态正确，让 isUserTurn 能正确计算
      isGenerating.value = false
      currentSpeakingRole.value = ''
      console.log('[辩论流程] 状态已重置，等待用户发言')
      // 轮到用户发言，不需要生成AI回复
      return
    } else {
      console.log('[辩论流程] 用户是辩护人，下一个是公诉人（AI发言）')
      // 用户是辩护人，下一个是公诉人（AI发言）
      // 审判员不发言，继续轮流发言，AI回复后需要检查审判员（因为已经完成一轮）
      await generateAiResponse('plaintiff', '', false, false)
      return
    }
  }
  
  console.log('[辩论流程] 最后一条非审判员消息 - 角色:', lastNonJudgeMessage.role)
  
  // 如果最后是公诉人发言，下一个是辩护人；反之亦然
  if (lastNonJudgeMessage.role === 'plaintiff') {
    console.log('[辩论流程] 最后是公诉人发言，下一个是辩护人')
    // 下一个是辩护人
    if (userIdentity.value === 'defendant') {
      console.log('[辩论流程] 轮到用户（辩护人）发言，等待用户输入')
      // 确保状态正确，让 isUserTurn 能正确计算
      isGenerating.value = false
      currentSpeakingRole.value = ''
      console.log('[辩论流程] 状态已重置，等待用户发言')
      // 轮到用户发言，不需要生成AI回复
      return
    } else {
      console.log('[辩论流程] 用户是公诉人，下一个是辩护人（AI发言）')
      // 用户是公诉人，下一个是辩护人（AI发言）
      // 审判员不发言，继续轮流发言，AI回复后会自动检查审判员
      await generateAiResponse('defendant', '', false, false)
    }
  } else {
    console.log('[辩论流程] 最后是辩护人发言，下一个是公诉人')
    // 下一个是公诉人
    if (userIdentity.value === 'plaintiff') {
      console.log('[辩论流程] 轮到用户（公诉人）发言，等待用户输入')
      // 确保状态正确，让 isUserTurn 能正确计算
      isGenerating.value = false
      currentSpeakingRole.value = ''
      console.log('[辩论流程] 状态已重置，等待用户发言')
      // 轮到用户发言，不需要生成AI回复
      return
    } else {
      console.log('[辩论流程] 用户是辩护人，下一个是公诉人（AI发言）')
      // 用户是辩护人，下一个是公诉人（AI发言）
      // 审判员不发言，继续轮流发言，AI回复后需要检查审判员（因为已经完成一轮）
      await generateAiResponse('plaintiff', '', false, false)
    }
  }
  console.log('[辩论流程] 继续公诉人和辩护人轮流发言 - 结束')
}

// 生成AI回复
const generateAiResponse = async (role, prompt, isFirstJudgeSpeech = false, shouldCheckJudgeAfter = false) => {
  console.log('[辩论流程] 生成AI回复 - 开始')
  console.log('[辩论流程] 参数 - role:', role, ', isFirstJudgeSpeech:', isFirstJudgeSpeech, ', shouldCheckJudgeAfter:', shouldCheckJudgeAfter)
  console.log('[辩论流程] 当前状态 - isGenerating:', isGenerating.value, ', currentSpeakingRole:', currentSpeakingRole.value)
  
  // 如果辩论已结束，不再生成AI回复
  if (isDebateEnded.value || debateCompleted.value) {
    console.log('[辩论流程] 辩论已结束，不再生成AI回复')
    isGenerating.value = false
    currentSpeakingRole.value = ''
    return
  }
  
  if (isGenerating.value) {
    console.log('[辩论流程] 正在生成中，跳过')
    return
  }
  
  isGenerating.value = true
  
  // 更新当前发言角色
  const roleName = role === 'judge' ? '审判员' : (role === 'plaintiff' ? '公诉人' : '辩护人')
  currentSpeakingRole.value = roleName
  console.log('[辩论流程] 设置发言角色:', roleName)
  
  // 用于保存首次审判员发言的文本，以便在 finally 块中使用
  let firstJudgeSpeechText = null
  
  // 记录开始时间
  const startTime = Date.now()
  
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
        name: role === 'judge' ? '审判员' : (role === 'plaintiff' ? '公诉人' : '辩护人'),
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
      userStrategy: userStrategy.value || 'balanced', // 用户自己的辩论策略
      isFirstJudgeSpeech: isFirstJudgeSpeech // 标记是否为首次审判员发言
    }, {
      timeout: 0 // 取消超时限制，允许AI生成长时间运行
    })
    
    // 计算耗时
    const endTime = Date.now()
    const duration = ((endTime - startTime) / 1000).toFixed(2) // 转换为秒，保留2位小数
    
    if (response.code === 200 && response.data) {
      const aiText = response.data
      const roleName = role === 'judge' ? '审判员' : (role === 'plaintiff' ? '公诉人' : '辩护人')
      console.log('[辩论流程] AI生成成功，角色:', roleName, ', 内容长度:', aiText.length, ', 耗时:', duration, '秒, 预览:', aiText.substring(0, 100))
      
      addMessage(role, roleName, aiText, parseFloat(duration))
      
      // 确保消息已添加到响应式数组，等待Vue更新DOM
      await nextTick()
      console.log('[辩论流程] 消息已添加，当前消息数量:', messages.value.length)
      
      // 如果是首次审判员发言，保存文本以便后续处理
      if (isFirstJudgeSpeech && role === 'judge') {
        firstJudgeSpeechText = aiText
        console.log('[辩论流程] 保存首次审判员发言文本')
      }
      
      // 检查是否应该结束庭审（法官决定结束）
      // 检测更多表示结束的关键词：休庭、评议、结束、合议庭、尾声、作出裁判、依法作出裁判等
      const endKeywords = ['休庭', '评议', '结束', '合议庭', '尾声', '作出裁判', '依法作出裁判', '依法对本案作出裁判', '作出公正判决', '作出判决', '庭审结束', '辩论结束', '法庭辩论结束']
      const shouldEndDebate = role === 'judge' && endKeywords.some(keyword => aiText.includes(keyword))
      
      if (shouldEndDebate) {
        console.log('[辩论流程] 检测到法官决定结束庭审，标记辩论结束')
        isDebateEnded.value = true
        debateCompleted.value = true
        // 保存对话历史到localStorage，供判决书生成使用
        localStorage.setItem('debateMessages', JSON.stringify(messages.value))
        // 标记辩论完成
        localStorage.setItem('debateCompleted', 'true')
        localStorage.setItem('isDebateEnded', 'true')
        // 立即保存到数据库（不等待防抖）
        if (caseStore.caseId) {
          clearTimeout(saveDebateMessagesTimer)
          await saveDebateMessages()
        }
        // 触发完成事件
        emit('complete')
        ElMessage.info('法官已决定结束辩论，庭审现场已锁定，请点击"生成庭后宣判"按钮')
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
    
    // 如果是审判员发言（非首次），发言后继续正常发言顺序
    // 注意：首次审判员发言现在在 startDebate 中直接处理，不再调用 generateAiResponse
    if (role === 'judge' && !isFirstJudgeSpeech) {
      console.log('[辩论流程] 审判员发言完成（非首次），继续正常发言顺序')
      await nextTick()
      // 获取最后一条消息（应该是审判员发言）
      const lastMessage = messages.value[messages.value.length - 1]
      if (lastMessage && lastMessage.role === 'judge') {
        await extractNextSpeakerFromJudgeSpeech(lastMessage.text)
      }
    } else if (role === 'plaintiff' || role === 'defendant') {
      // 每次发言结束后，都检查审判员是否需要介入
      // checkJudgeShouldSpeak 内部会判断是否满足硬性条件（距离上次审判员发言后，至少完成一轮）
      console.log('[辩论流程] AI回复完成，检查审判员是否需要介入')
      await nextTick()
      await checkJudgeShouldSpeak()
    } else if (role === 'judge') {
      console.log('[辩论流程] 审判员发言完成（非首次），状态已重置')
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
const addMessage = (role, name, text, duration = null) => {
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  
  const newMessage = {
    role,
    name,
    text,
    time,
    duration // AI生成耗时（秒），null表示用户消息或没有耗时信息
  }
  
  messages.value.push(newMessage)
  console.log('[消息添加] 添加消息成功 - 角色:', name, ', 内容长度:', text.length, ', 当前消息总数:', messages.value.length, ', 内容预览:', text.substring(0, 50))
  
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
  if (!debateStarted.value || debateCompleted.value || isDebateEnded.value || isGenerating.value) {
    return false
  }
  
  // 获取最后一条消息
  if (messages.value.length === 0) {
    // 如果还没有消息，默认由审判员开始，用户等待
    return false
  }
  
  const lastMessage = messages.value[messages.value.length - 1]
  const lastRole = lastMessage.role
  
  // 如果最后是审判员发言，审判员不再有指定发言的权力，按照正常发言顺序判断
  if (lastRole === 'judge') {
    // 找到最后一条非审判员消息，按照正常发言顺序判断
    const lastNonJudgeMessage = [...messages.value].reverse().find(m => m.role !== 'judge')
    if (!lastNonJudgeMessage) {
      // 如果没有非审判员消息，默认由公诉人开始
      return userIdentity.value === 'plaintiff'
    }
    // 如果最后是对方发言，轮到用户发言
    const opponentRole = userIdentity.value === 'plaintiff' ? 'defendant' : 'plaintiff'
    if (lastNonJudgeMessage.role === opponentRole) {
      return true
    }
    // 如果最后是用户自己发言，需要等待对方
    if (lastNonJudgeMessage.role === userIdentity.value) {
      return false
    }
    return false
  }
  
  // 如果最后是对方发言，轮到用户发言
  const opponentRole = userIdentity.value === 'plaintiff' ? 'defendant' : 'plaintiff'
  if (lastRole === opponentRole) {
    return true
  }
  
  // 如果最后是用户自己发言，需要等待对方或审判员
  if (lastRole === userIdentity.value) {
    return false
  }
  
  return false
})

// 判断模型是否正在加载
const isModelLoading = computed(() => {
  return modelInitializing.value || (modelInitProgress.value && !modelLoaded.value)
})

// 获取下一个发言人的名称
const nextSpeakerName = computed(() => {
  if (!debateStarted.value || messages.value.length === 0) {
    return '审判员'
  }
  
  const lastMessage = messages.value[messages.value.length - 1]
  const lastRole = lastMessage.role
  
  // 如果最后是审判员发言，审判员不再有指定发言的权力，按照正常发言顺序判断
  if (lastRole === 'judge') {
    // 找到最后一条非审判员消息，按照正常发言顺序判断
    const lastNonJudgeMessage = [...messages.value].reverse().find(m => m.role !== 'judge')
    if (!lastNonJudgeMessage) {
      // 如果没有非审判员消息，默认由公诉人开始
      return '公诉人'
    }
    // 如果最后是公诉人发言，下一个是辩护人；反之亦然
    if (lastNonJudgeMessage.role === 'plaintiff') {
      return '辩护人'
    } else if (lastNonJudgeMessage.role === 'defendant') {
      return '公诉人'
    }
    return '审判员'
  }
  
  // 如果最后是用户发言，下一个是对方
  if (lastRole === userIdentity.value) {
    return userIdentity.value === 'plaintiff' ? '辩护人' : '公诉人'
  }
  
  // 如果最后是对方发言，下一个应该是用户
  const opponentRole = userIdentity.value === 'plaintiff' ? 'defendant' : 'plaintiff'
  if (lastRole === opponentRole) {
    return userIdentity.value === 'plaintiff' ? '公诉人' : '辩护人'
  }
  
  return '审判员'
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

// 复制辩论发言内容
const copyDebateContent = async () => {
  if (!messages.value || messages.value.length === 0) {
    ElMessage.warning('没有发言内容可复制')
    return
  }
  
  try {
    // 整理发言内容为发言格式
    let formattedContent = '【庭审辩论记录】\n\n'
    
    messages.value.forEach((message, index) => {
      // 添加角色名称和发言内容
      formattedContent += `${message.name}：${message.text}`
      
      // 添加时间信息
      if (message.time) {
        formattedContent += `\n[${message.time}]`
      }
      
      // 添加AI生成耗时（如果有）
      if (message.duration !== null && message.duration !== undefined) {
        formattedContent += ` (生成耗时: ${message.duration}s)`
      }
      
      // 每条消息之间添加空行
      formattedContent += '\n\n'
    })
    
    // 移除最后的空行
    formattedContent = formattedContent.trim()
    
    // 复制到剪贴板
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(formattedContent)
      ElMessage.success('发言内容已复制到剪贴板')
    } else {
      // 降级方案：使用传统的复制方法
      const textArea = document.createElement('textarea')
      textArea.value = formattedContent
      textArea.style.position = 'fixed'
      textArea.style.left = '-999999px'
      textArea.style.top = '-999999px'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      
      try {
        const successful = document.execCommand('copy')
        if (successful) {
          ElMessage.success('发言内容已复制到剪贴板')
        } else {
          ElMessage.error('复制失败，请手动复制')
        }
      } catch (err) {
        ElMessage.error('复制失败，请手动复制')
      } finally {
        document.body.removeChild(textArea)
      }
    }
  } catch (error) {
    console.error('复制发言内容失败:', error)
    ElMessage.error('复制失败，请重试')
  }
}

// 重置庭审对话
const handleResetDebate = async () => {
  // 清空消息历史
  messages.value = []
  
  // 重置状态（包括解除庭审结束状态）
  debateStarted.value = false
  debateCompleted.value = false
  isDebateEnded.value = false
  userInput.value = ''
  currentSpeakingRole.value = ''
  isGenerating.value = false
  judgeSkipCount.value = 0 // 重置跳过计数
  editingIndex.value = -1
  editingText.value = ''
  
  // 清除localStorage中的辩论记录
  try {
    localStorage.removeItem('debateMessages')
    localStorage.removeItem('debateCompleted')
    localStorage.removeItem('isDebateEnded')
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

// 监听路由变化，如果从其他页面进入且已选择审判员类型，自动开始
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
      const isEnded = localStorage.getItem('isDebateEnded') === 'true'
      if (isCompleted) {
        debateCompleted.value = true
      }
      if (isEnded) {
        isDebateEnded.value = true
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

// 监听路由变化，如果从其他页面进入且已选择审判员类型，自动开始
onMounted(async () => {
  // 如果有案件ID，从数据库加载案件信息（包括审判员类型和策略）
  if (caseStore.caseId) {
    console.log('[Debate] 从数据库加载案件信息，caseId:', caseStore.caseId)
    const loaded = await caseStore.loadCaseFromDatabase(caseStore.caseId)
    if (loaded) {
      console.log('[Debate] 案件信息加载成功')
      // 更新本地状态（从 store 恢复）
      // 注意：即使值为空字符串也要设置，确保从数据库加载的值能正确恢复
      if (caseStore.selectedJudgeType !== undefined && caseStore.selectedJudgeType !== null) {
        selectedJudgeType.value = caseStore.selectedJudgeType || 'professional'
      }
      if (caseStore.opponentStrategy !== undefined && caseStore.opponentStrategy !== null) {
        opponentStrategy.value = caseStore.opponentStrategy || 'balanced'
      }
      console.log('[Debate] 恢复的数据:', {
        judgeType: selectedJudgeType.value,
        strategy: opponentStrategy.value,
        storeJudgeType: caseStore.selectedJudgeType,
        storeStrategy: caseStore.opponentStrategy
      })
    } else {
      console.warn('[Debate] 案件信息加载失败')
    }
  }
  
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
  gap: 18px;
}

/* 顶部信息卡片网格 */
.debate-info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

/* 统一的卡片视觉：贴合首页玻璃态风格 */
.debate-card {
  position: relative;
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(16px) saturate(1.18);
  -webkit-backdrop-filter: blur(16px) saturate(1.18);
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.7);
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
  padding: 14px 16px 12px;
  overflow: hidden;
  transition: transform var(--transition-hover) ease, box-shadow var(--transition-hover) ease,
    border-color var(--transition-hover) ease, background-color var(--transition-hover) ease;
}

.debate-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  background:
    radial-gradient(circle at 0 0, rgba(255, 255, 255, 0.9), transparent 55%),
    radial-gradient(circle at 100% 0, rgba(129, 140, 248, 0.16), transparent 55%);
  opacity: 0.8;
  mix-blend-mode: screen;
}

.debate-card > * {
  position: relative;
  z-index: 1;
}

.debate-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 40px rgba(15, 23, 42, 0.12);
  border-color: rgba(148, 163, 253, 0.6);
}

.section-title {
  font-size: 13px;
  color: var(--text-primary);
  margin: 0;
  font-weight: 600;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(148, 163, 253, 0.18);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.copy-debate-btn,
.reset-debate-btn {
  font-size: 12px;
  padding: 6px 12px;
  height: auto;
  border-radius: 999px;
}

.copy-debate-btn {
  background: rgba(99, 102, 241, 0.06);
  border-color: rgba(99, 102, 241, 0.3);
}

.copy-debate-btn:hover {
  background: rgba(99, 102, 241, 0.12);
  border-color: rgba(99, 102, 241, 0.5);
}

.reset-debate-btn {
  background: rgba(248, 113, 113, 0.04);
  border-color: rgba(248, 113, 113, 0.32);
}

.reset-debate-btn:hover {
  background: rgba(248, 113, 113, 0.12);
  border-color: rgba(248, 113, 113, 0.6);
}

/* 身份 / 材料 / 审判员 / 策略四块信息区：使用统一卡片视觉，无额外样式覆盖 */

.identity-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.identity-label {
  font-size: 15px;
  font-weight: 600;
  color: var(--primary-purple);
}

/* 庭前准备材料查看 */
.pretrial-materials-section {
  margin-bottom: 8px;
}

.materials-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.toggle-btn {
  font-size: 12px;
  color: var(--primary-purple);
  padding: 2px 4px;
}

.materials-content {
  margin-top: 8px;
  padding-top: 4px;
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
  color: var(--text-primary);
  min-width: 72px;
  flex-shrink: 0;
}

.material-value {
  font-size: 12px;
  color: var(--text-secondary);
  flex: 1;
  line-height: 1.6;
}

.case-description {
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 200px;
  overflow-y: auto;
  padding: 8px 10px;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
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

.material-empty {
  font-size: 12px;
  color: #9ca3af;
}

/* 审判员类型显示 */
.judge-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.judge-label {
  font-size: 15px;
  font-weight: 600;
  color: var(--primary-purple);
}

.judge-desc {
  font-size: 14px;
  color: var(--text-secondary);
}

/* 诉讼策略显示 */
.strategy-card {
  padding: 10px 12px;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
}

.plaintiff-strategy {
  border-left: 3px solid var(--primary-purple);
}


.strategy-label {
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 4px;
  color: var(--text-primary);
}

.plaintiff-strategy .strategy-label {
  color: var(--primary-purple-dark);
}

.defendant-strategy .strategy-label {
  color: var(--accent-green-dark);
}

.strategy-content {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.6;
}

/* 庭审对话区域 */
.debate-chat-section {
  background: rgba(248, 250, 252, 0.92);
  border-radius: 20px;
  padding: 18px 18px 14px;
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 400px;
  border: 1px solid rgba(148, 163, 253, 0.16);
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.09);
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 14px 14px 10px;
  background: linear-gradient(
    135deg,
    rgba(15, 23, 42, 0.02),
    rgba(129, 140, 248, 0.04)
  );
  border-radius: 14px;
  max-height: 600px;
  min-height: 380px;
}

.empty-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #9ca3af;
  font-size: 13px;
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
  margin-bottom: 12px;
  animation: fadeIn 0.24s ease-out;
  display: flex;
  width: 100%;
  box-sizing: border-box;
  position: relative;
}

/* 鼠标悬停时显示编辑按钮和重新生成按钮 */
.message-item:hover .edit-btn-wrapper,
.message-item:hover .regenerate-btn-wrapper {
  opacity: 1;
  visibility: visible;
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

/* 公诉人：左边布局 */
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
  font-size: 11px;
  color: #6b7280;
  margin-bottom: 3px;
}

.message-plaintiff .message-time {
  font-size: 10px;
  color: #9ca3af;
  margin-top: 3px;
  align-self: flex-start;
}

.message-duration {
  margin-left: 4px;
  color: #67c23a;
  font-weight: 500;
  font-size: 11px;
}

/* 审判员：中间布局 */
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
  font-size: 11px;
  color: #6b7280;
  margin-bottom: 3px;
}

.message-time-center {
  font-size: 10px;
  color: #9ca3af;
  margin-top: 3px;
}

.message-time-center .message-duration {
  margin-left: 4px;
  color: #67c23a;
  font-weight: 500;
}

/* 辩护人：右边布局 */
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
  font-size: 11px;
  color: #6b7280;
  margin-bottom: 3px;
  text-align: right;
}

.message-defendant-wrapper .message-time-right {
  font-size: 10px;
  color: #9ca3af;
  margin-top: 3px;
  text-align: right;
}

.message-time-right .message-duration {
  margin-left: 4px;
  color: #67c23a;
  font-weight: 500;
}

/* 头像样式 */
.avatar {
  width: 28px;
  height: 28px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 4px 10px rgba(15, 23, 42, 0.18);
}

.avatar-judge {
  background: rgba(234, 179, 8, 0.9);
}

.avatar-plaintiff {
  background: rgba(59, 130, 246, 0.9);
}

.avatar-defendant {
  background: rgba(248, 113, 113, 0.9);
}

/* 消息气泡 */
.message-bubble {
  padding: 8px 10px;
  border-radius: 10px;
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.5;
  word-wrap: break-word;
  position: relative;
  max-width: 100%;
  display: inline-block;
}

.message-bubble-left {
  background: rgba(129, 140, 248, 0.12);
  border-radius: 12px 12px 12px 4px;
  align-self: flex-start;
}

.message-bubble-center {
  background: #fff7e6;
  border-radius: 10px;
  text-align: center;
  display: block;
  margin: 0 auto;
}

.message-bubble-right {
  background: #ffffff;
  border-radius: 12px 12px 4px 12px;
  align-self: flex-end;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.16);
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
  text-align: left;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.2s ease, visibility 0.2s ease;
  position: relative;
  z-index: 1;
}

.message-content-wrapper .edit-btn-wrapper {
  text-align: left;
}

.message-content-right .edit-btn-wrapper {
  text-align: right;
}

.edit-btn {
  font-size: 12px;
  padding: 6px 12px;
  height: auto;
  min-height: 28px;
  font-weight: 500;
}

/* 重新生成功能 */
.regenerate-btn-wrapper {
  margin-top: 4px;
  text-align: left;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.2s ease, visibility 0.2s ease;
  position: relative;
  z-index: 1;
}

.message-content-wrapper .regenerate-btn-wrapper {
  text-align: left;
}

.message-content-right .regenerate-btn-wrapper {
  text-align: right;
}

.regenerate-btn-center {
  text-align: center;
}

.regenerate-btn {
  font-size: 12px;
  padding: 6px 12px;
  height: auto;
  min-height: 28px;
  font-weight: 500;
}

.edit-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 4px;
}

.edit-action-btn {
  font-size: 12px;
  padding: 6px 16px;
  height: auto;
  min-height: 28px;
}

:deep(.edit-textarea .el-textarea__inner) {
  font-size: 12px;
  padding: 8px 10px;
  line-height: 1.5;
  overflow-y: visible !important;
  resize: none;
}

/* 用户输入区域 */
.input-section {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid #e5e7eb;
}

/* AI代理和策略选择 */
.ai-proxy-section {
  margin-bottom: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
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
  color: #4b5563;
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
  margin-bottom: 10px;
  padding: 9px 14px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.03);
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
  color: #6366f1;
}

.status-user-turn .status-text {
  color: #6366f1;
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
  padding: 16px 0 10px;
}

.start-btn,
.generate-btn {
  width: 200px;
  height: 48px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 999px;
}

.start-btn {
  background: var(--primary-purple);
  border-color: var(--primary-purple);
}

.start-btn:hover {
  background: #4f46e5;
  border-color: #4f46e5;
  transform: translateY(-1px);
  box-shadow: 0 8px 22px rgba(79, 70, 229, 0.35);
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
  background: #16a34a;
  border-color: #16a34a;
}

.generate-btn:hover {
  background: #15803d;
  border-color: #15803d;
  transform: translateY(-1px);
  box-shadow: 0 8px 22px rgba(22, 163, 74, 0.3);
}

/* 辩论结束后的样式 */
.debate-chat-section.debate-ended {
  position: relative;
}

.debate-ended-notice {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  margin-bottom: 16px;
  background: rgba(255, 243, 205, 0.92);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-radius: 8px;
  border-left: 4px solid #ffc107;
  animation: fadeIn 0.3s ease-in;
}

.notice-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.notice-text {
  flex: 1;
  font-size: 14px;
  color: #856404;
  font-weight: 500;
  line-height: 1.5;
}

/* 响应式微调：较窄屏幕上减小留白 */
@media (max-width: 768px) {
  .debate-info-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .debate-card {
    border-radius: var(--radius-md);
    box-shadow: none;
  }

  .identity-display-section,
  .pretrial-materials-section,
  .judge-display-section,
  .strategy-display-section,
  .debate-chat-section {
    padding: 12px 12px;
  }

  .chat-container {
    padding: 12px;
    min-height: 320px;
  }

  .action-section {
    padding: 14px 0 8px;
  }
}
</style>

