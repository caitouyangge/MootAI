<template>
  <div class="debate-container">
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
        <div class="input-wrapper">
          <el-input
            v-model="userInput"
            type="textarea"
            :rows="3"
            placeholder="请输入您的发言..."
            class="user-input"
            :disabled="isGenerating"
            @keydown.ctrl.enter="sendMessage"
          />
          <div class="input-actions">
            <el-button
              type="primary"
              :loading="isGenerating"
              :disabled="!userInput.trim() || isGenerating"
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
import { ref, onMounted, nextTick, watch } from 'vue'
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
  
  // 法官宣布开始
  const judgePrompt = userIdentity.value === 'plaintiff' 
    ? '现在开庭。请原告陈述诉讼请求和事实理由。'
    : '现在开庭。请被告针对原告的指控进行答辩。'
  
  await generateAiResponse('judge', judgePrompt)
}

// 发送用户消息
const sendMessage = async () => {
  if (!userInput.value.trim() || isGenerating.value) {
    return
  }
  
  const userText = userInput.value.trim()
  userInput.value = ''
  
  // 添加用户消息
  addMessage(userIdentity.value, userIdentity.value === 'plaintiff' ? '原告' : '被告', userText)
  
  // 生成对方律师的回复
  const opponentRole = userIdentity.value === 'plaintiff' ? 'defendant' : 'plaintiff'
  await generateAiResponse(opponentRole, userText)
  
  // 生成法官的回复（可选，根据对话流程决定）
  // 这里可以根据对话轮次决定是否生成法官回复
  if (messages.value.length % 4 === 0) {
    await generateAiResponse('judge', '请继续辩论。')
  }
}

// 生成AI回复
const generateAiResponse = async (role, prompt) => {
  if (isGenerating.value) return
  
  isGenerating.value = true
  
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
    
    const response = await request.post('/debate/generate', {
      userIdentity: userIdentity.value,
      currentRole: role,
      messages: messageHistory,
      judgeType: selectedJudgeType.value || 'neutral',
      caseDescription: caseDescription.value || ''
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

