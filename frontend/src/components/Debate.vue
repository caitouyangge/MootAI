<template>
  <div class="debate-container">
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
          <div class="material-item">
            <div class="material-label">身份：</div>
            <div class="material-value">{{ userIdentity === 'plaintiff' ? '原告' : '被告' }}</div>
          </div>
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

    <!-- 法官类型选择 -->
    <div class="judge-select-section">
      <h3 class="section-title">选择法官类型</h3>
      <el-select
        v-model="selectedJudgeType"
        placeholder="请选择法官类型"
        class="judge-select"
        @change="onJudgeTypeChange"
      >
        <el-option
          v-for="judge in judgeTypes"
          :key="judge.value"
          :label="judge.label"
          :value="judge.value"
        >
          <div class="judge-option">
            <span class="judge-name">{{ judge.label }}</span>
            <span class="judge-desc">：{{ judge.description }}</span>
          </div>
        </el-option>
      </el-select>
    </div>

    <!-- 诉讼策略显示 -->
    <div class="strategy-display-section">
      <h3 class="section-title">诉讼策略</h3>
      <div class="strategy-cards">
        <div class="strategy-card plaintiff-strategy">
          <div class="strategy-label">原告策略</div>
          <div class="strategy-content">{{ plaintiffStrategy }}</div>
        </div>
        <div class="strategy-card defendant-strategy">
          <div class="strategy-label">被告策略</div>
          <div class="strategy-content">{{ defendantStrategy }}</div>
        </div>
      </div>
    </div>

    <!-- 庭审对话区域 -->
    <div class="debate-chat-section">
      <h3 class="section-title">庭审现场</h3>
      <div class="chat-container" ref="chatContainer">
        <div v-if="messages.length === 0" class="empty-tip">
          <p>请先选择法官类型，然后点击"开始庭审"按钮</p>
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
        
        <div class="input-wrapper">
          <el-input
            v-model="userInput"
            type="textarea"
            :rows="3"
            :placeholder="isUserTurn ? `请输入您的发言（作为${userIdentity === 'plaintiff' ? '原告' : '被告'}）...` : '请等待其他角色发言...'"
            class="user-input"
            :disabled="!isUserTurn || isGenerating"
            @keydown.ctrl.enter="sendMessage"
          />
          <div class="input-actions">
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
        :disabled="!selectedJudgeType"
        @click="startDebate"
      >
        开始庭审
      </el-button>
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
import { ref, onMounted, nextTick, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
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

// 法官类型
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

const selectedJudgeType = ref('')
const debateStarted = ref(false)
const isGenerating = ref(false)
const userInput = ref('')
const currentSpeakingRole = ref('') // 当前正在发言的角色

const onJudgeTypeChange = () => {
  // 法官类型改变时不做任何操作，等待用户点击"开始庭审"
}

// 诉讼策略
const plaintiffStrategy = ref('均衡策略：主张返还已支付款项30万元，违约金主张适中，约5-7万元，可协商。准备充分的证据，但不过度激化矛盾。')
const defendantStrategy = ref('保守策略：优先考虑通过调解解决争议，主张返还已支付款项，但可适当让步。违约金主张较为温和，可协商调整。')

// 对话消息
const messages = ref([])
const debateCompleted = ref(false)
const chatContainer = ref(null)

// 编辑相关
const editingIndex = ref(-1)
const editingText = ref('')

// 开始编辑
const startEdit = (index, text) => {
  editingIndex.value = index
  editingText.value = text
}

// 保存编辑
const saveEdit = (index) => {
  if (editingIndex.value === index && editingText.value.trim()) {
    messages.value[index].text = editingText.value.trim()
    // TODO: 基于修改重新生成后续对话（AI部分暂时没有）
    ElMessage.success('内容已更新')
  }
  editingIndex.value = -1
  editingText.value = ''
}

// 开始庭审
const startDebate = async () => {
  if (!selectedJudgeType.value) {
    ElMessage.warning('请先选择法官类型')
    return
  }
  
  messages.value = []
  debateCompleted.value = false
  debateStarted.value = true
  
  // 法官宣布开始（开庭时必须发言引导原告发言）
  const judgePrompt = '现在开庭。请原告陈述诉讼请求和事实理由。'
  
  await generateAiResponse('judge', judgePrompt, true)
}

// 发送用户消息
const sendMessage = async () => {
  if (!userInput.value.trim() || isGenerating.value || !isUserTurn.value) {
    return
  }
  
  const userText = userInput.value.trim()
  userInput.value = ''
  
  // 更新当前发言角色为用户
  currentSpeakingRole.value = userIdentity.value === 'plaintiff' ? '原告' : '被告'
  
  // 添加用户消息
  addMessage(userIdentity.value, userIdentity.value === 'plaintiff' ? '原告' : '被告', userText)
  
  // 用户发言结束
  currentSpeakingRole.value = ''
  
  // 生成对方律师的回复
  const opponentRole = userIdentity.value === 'plaintiff' ? 'defendant' : 'plaintiff'
  await generateAiResponse(opponentRole, userText, false)
  
  // 每发言一轮后（用户发言 + 对方律师回复），法官AI判断是否应该发言
  // 如果法官发言，发言完应该决定下一个发言人的身份
  // 如果法官不发言，由原告和被告轮流发言
  await checkJudgeShouldSpeak()
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
    background += `原告策略：${plaintiffStrategy.value}\n`
    background += `被告策略：${defendantStrategy.value}\n`
  } else {
    background += `被告策略：${defendantStrategy.value}\n`
    background += `原告策略：${plaintiffStrategy.value}\n`
  }
  
  return background
}

// 检查法官是否应该发言
const checkJudgeShouldSpeak = async () => {
  if (isGenerating.value) return
  
  // 构建判断提示词
  const judgeCheckPrompt = `根据当前的庭审对话历史，请判断作为审判员，你是否需要发言。
  
要求：
1. 如果需要发言，请直接发言，发言内容要符合审判员的角色定位。
2. 如果不需要发言，请只输出"不需要发言"，然后由原告和被告继续轮流发言。
3. 如果你发言了，请在发言的最后明确指定下一个发言人的身份（"请原告继续"或"请被告继续"）。`
  
  try {
    const messageHistory = messages.value.map(msg => ({
      role: msg.role,
      name: msg.name,
      text: msg.text
    }))
    
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
      
      // 判断法官是否发言（如果包含"不需要发言"，则不发言）
      if (judgeResponse && !judgeResponse.includes('不需要发言')) {
        // 法官发言
        addMessage('judge', '法官', judgeResponse)
        
        // 法官发言后，从发言内容中提取下一个发言人
        await extractNextSpeakerFromJudgeSpeech(judgeResponse)
      } else {
        // 法官不发言，由原告和被告轮流发言
        await continueAlternatingDebate()
      }
    }
  } catch (error) {
    console.error('法官判断失败:', error)
    // 如果判断失败，默认继续轮流发言
    await continueAlternatingDebate()
  }
}

// 从法官发言中提取下一个发言人
const extractNextSpeakerFromJudgeSpeech = async (judgeSpeech) => {
  // 检查发言中是否指定了下一个发言人
  if (judgeSpeech.includes('请原告') || judgeSpeech.includes('原告继续') || judgeSpeech.includes('原告发言')) {
    // 如果用户是原告，轮到用户发言，不需要生成AI回复
    if (userIdentity.value === 'plaintiff') {
      return
    } else {
      // 用户是被告，下一个是原告（AI发言）
      await generateAiResponse('plaintiff', '', false)
    }
  } else if (judgeSpeech.includes('请被告') || judgeSpeech.includes('被告继续') || judgeSpeech.includes('被告发言')) {
    // 如果用户是被告，轮到用户发言，不需要生成AI回复
    if (userIdentity.value === 'defendant') {
      return
    } else {
      // 用户是原告，下一个是被告（AI发言）
      await generateAiResponse('defendant', '', false)
    }
  } else {
    // 如果没有明确指定，根据对话历史决定
    await decideNextSpeaker()
  }
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
        await generateAiResponse('plaintiff', '', false)
      }
    } else {
      // 被告发言次数少，下一个是被告
      if (userIdentity.value === 'defendant') {
        // 轮到用户发言，不需要生成AI回复
        return
      } else {
        // 用户是原告，下一个是被告（AI发言）
        await generateAiResponse('defendant', '', false)
      }
    }
  }
}

// 继续原告和被告轮流发言
const continueAlternatingDebate = async () => {
  // 获取最后一条非法官消息的角色
  const lastNonJudgeMessage = [...messages.value].reverse().find(m => m.role !== 'judge')
  
  if (!lastNonJudgeMessage) {
    // 如果没有非法官消息，判断下一个应该是谁
    // 如果用户是原告，下一个应该是原告（用户发言）
    if (userIdentity.value === 'plaintiff') {
      // 轮到用户发言，不需要生成AI回复
      return
    } else {
      // 用户是被告，下一个是原告（AI发言）
      await generateAiResponse('plaintiff', '', false)
      return
    }
  }
  
  // 如果最后是原告发言，下一个是被告；反之亦然
  if (lastNonJudgeMessage.role === 'plaintiff') {
    // 下一个是被告
    if (userIdentity.value === 'defendant') {
      // 轮到用户发言，不需要生成AI回复
      return
    } else {
      // 用户是原告，下一个是被告（AI发言）
      await generateAiResponse('defendant', '', false)
    }
  } else {
    // 下一个是原告
    if (userIdentity.value === 'plaintiff') {
      // 轮到用户发言，不需要生成AI回复
      return
    } else {
      // 用户是被告，下一个是原告（AI发言）
      await generateAiResponse('plaintiff', '', false)
    }
  }
}

// 生成AI回复
const generateAiResponse = async (role, prompt, isFirstJudgeSpeech = false) => {
  if (isGenerating.value) return
  
  isGenerating.value = true
  
  // 更新当前发言角色
  const roleName = role === 'judge' ? '法官' : (role === 'plaintiff' ? '原告' : '被告')
  currentSpeakingRole.value = roleName
  
  try {
    // 准备消息历史（包含当前prompt作为上下文）
    const messageHistory = messages.value.map(msg => ({
      role: msg.role,
      name: msg.name,
      text: msg.text
    }))
    
    // 如果prompt不为空，添加一个临时消息作为上下文
    if (prompt) {
      messageHistory.push({
        role: role,
        name: role === 'judge' ? '法官' : (role === 'plaintiff' ? '原告' : '被告'),
        text: prompt
      })
    }
    
    // 构建完整的background（包含所有庭前准备资料）
    const background = buildBackground()
    
    const response = await request.post('/debate/generate', {
      userIdentity: userIdentity.value,
      currentRole: role,
      messages: messageHistory,
      judgeType: selectedJudgeType.value || 'neutral',
      caseDescription: background, // 使用完整的background，包含所有庭前准备资料
      isFirstJudgeSpeech: isFirstJudgeSpeech // 标记是否为首次法官发言
    }, {
      timeout: 0 // 取消超时限制，允许AI生成长时间运行
    })
    
    if (response.code === 200 && response.data) {
      const aiText = response.data
      const roleName = role === 'judge' ? '法官' : (role === 'plaintiff' ? '原告' : '被告')
      addMessage(role, roleName, aiText)
      
      // 检查是否应该结束庭审
      if (aiText.includes('休庭') || aiText.includes('评议') || aiText.includes('结束') || aiText.includes('合议庭')) {
        debateCompleted.value = true
        // 保存对话历史到localStorage，供判决书生成使用
        localStorage.setItem('debateMessages', JSON.stringify(messages.value))
        // 标记辩论完成
        localStorage.setItem('debateCompleted', 'true')
        // 触发完成事件
        emit('complete')
      }
    } else {
      ElMessage.error(response.message || '生成失败')
    }
  } catch (error) {
    console.error('生成AI回复失败:', error)
    ElMessage.error('生成失败，请重试: ' + (error.message || '未知错误'))
  } finally {
    isGenerating.value = false
    currentSpeakingRole.value = '' // 发言结束，清空当前发言角色
  }
}

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

// 监听路由变化，如果从其他页面进入且已选择法官类型，自动开始
onMounted(() => {
  // 可以在这里添加自动开始逻辑
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
  margin: 0 0 15px 0;
  font-weight: 600;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
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

/* 法官类型选择 */
.judge-select-section {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 15px;
}

.judge-select {
  width: 100%;
}

/* 选择器输入框字体大小 */
:deep(.judge-select .el-input__inner) {
  font-size: 12px;
  height: 28px;
  line-height: 28px;
}

/* 选择器下拉选项字体大小 */
:deep(.judge-select .el-select-dropdown__item) {
  font-size: 12px;
  height: auto;
  padding: 6px 12px;
}

.judge-option {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 4px;
}

.judge-name {
  font-weight: 600;
  color: #333;
  font-size: 12px;
}

.judge-desc {
  font-size: 12px;
  color: #666;
}

/* 诉讼策略显示 */
.strategy-display-section {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 15px;
}

.strategy-cards {
  display: flex;
  gap: 15px;
}

.strategy-card {
  flex: 1;
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

