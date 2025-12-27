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
          <p>请先选择法官类型，庭审将自动开始</p>
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
                <div class="message-text">{{ message.text }}</div>
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
            <div class="message-content-wrapper message-content-right">
              <div class="message-name message-name-right">{{ message.name }}</div>
              <div class="message-bubble message-bubble-right">
                <div class="message-text">{{ message.text }}</div>
              </div>
              <div class="message-time message-time-right">{{ message.time }}</div>
            </div>
            <div class="message-avatar">
              <div class="avatar avatar-defendant">被</div>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- 生成判决结果按钮 -->
    <div class="action-section" v-if="debateCompleted">
      <el-button
        type="primary"
        size="large"
        class="generate-btn"
        @click="generateVerdict"
      >
        生成判决结果
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

// 获取身份信息
const userIdentity = ref(route.query.identity || 'plaintiff')

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

const onJudgeTypeChange = () => {
  if (selectedJudgeType.value && messages.value.length === 0) {
    startDebate()
  }
}

// 诉讼策略
const plaintiffStrategy = ref('均衡策略：主张返还已支付款项30万元，违约金主张适中，约5-7万元，可协商。准备充分的证据，但不过度激化矛盾。')
const defendantStrategy = ref('保守策略：优先考虑通过调解解决争议，主张返还已支付款项，但可适当让步。违约金主张较为温和，可协商调整。')

// 对话消息
const messages = ref([])
const debateCompleted = ref(false)
const chatContainer = ref(null)

// 开始庭审
const startDebate = () => {
  messages.value = []
  debateCompleted.value = false
  
  // 法官宣布开始
  addMessage('judge', '法官', '现在开庭。请原告陈述诉讼请求和事实理由。')
  
  // 延迟添加后续对话
  setTimeout(() => {
    addMessage('plaintiff', '原告', '尊敬的法官，我方请求法院判令被告返还已支付的服务费30万元，并支付违约金10万元。事实和理由如下：我方与被告于2023年1月签订技术服务合同，约定被告提供技术服务，合同金额50万元。我方已按约定支付首付款30万元，但被告未能按合同约定提供服务，构成违约。')
  }, 1000)
  
  setTimeout(() => {
    addMessage('defendant', '被告', '尊敬的法官，我方对原告的陈述有异议。我方确实与原告签订了合同，但原告未能提供必要的配合条件，导致我方无法正常履行合同。且原告主张的违约金过高，不符合法律规定。')
  }, 2000)
  
  setTimeout(() => {
    addMessage('judge', '法官', '请双方就争议焦点进行辩论。争议焦点一：被告是否存在违约行为？')
  }, 3000)
  
  setTimeout(() => {
    addMessage('plaintiff', '原告', '我方认为被告存在明显违约行为。合同明确约定了服务内容和时间节点，但被告在收到首付款后，未能按约定时间提供任何服务。我方多次催促，被告均以各种理由推脱。')
  }, 4000)
  
  setTimeout(() => {
    addMessage('defendant', '被告', '我方不认可原告的说法。合同履行需要双方配合，原告未能提供合同约定的工作环境和资料，导致我方无法开展工作。这属于原告的违约行为，而非我方违约。')
  }, 5000)
  
  setTimeout(() => {
    addMessage('judge', '法官', '请原告提供相关证据材料。')
  }, 6000)
  
  setTimeout(() => {
    addMessage('plaintiff', '原告', '我方提交了以下证据：1. 双方签订的服务合同原件；2. 银行转账凭证，证明已支付30万元；3. 与被告的沟通记录，显示被告承认无法履行合同。')
  }, 7000)
  
  setTimeout(() => {
    addMessage('judge', '法官', '请被告质证。')
  }, 8000)
  
  setTimeout(() => {
    addMessage('defendant', '被告', '我方对证据的真实性无异议，但对证明目的有异议。沟通记录显示的是我方在尝试解决问题，而非承认违约。')
  }, 9000)
  
  setTimeout(() => {
    addMessage('judge', '法官', '关于违约金的问题，请双方发表意见。')
  }, 10000)
  
  setTimeout(() => {
    addMessage('plaintiff', '原告', '合同约定的违约金为合同金额的20%，即10万元，符合法律规定。且被告的违约行为给我方造成了实际损失。')
  }, 11000)
  
  setTimeout(() => {
    addMessage('defendant', '被告', '我方认为违约金过高。根据《民法典》相关规定，违约金不应超过实际损失的30%。原告未能证明其实际损失达到10万元，因此违约金应当调整。')
  }, 12000)
  
  setTimeout(() => {
    addMessage('judge', '法官', '法庭调查和辩论结束。现在休庭，合议庭将进行评议。')
    debateCompleted.value = true
  }, 13000)
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
  font-size: 16px;
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

.judge-option {
  display: flex;
  flex-direction: column;
}

.judge-name {
  font-weight: 600;
  color: #333;
}

.judge-desc {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
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
  font-size: 14px;
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
  font-size: 13px;
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
  align-items: flex-end;
}

.message-defendant .message-content-wrapper {
  flex: 1;
  max-width: 70%;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  margin-right: 6px;
}

.message-defendant .message-avatar {
  flex-shrink: 0;
}

.message-defendant .message-name-right {
  font-size: 7px;
  color: #999;
  margin-bottom: 3px;
  text-align: right;
}

.message-defendant .message-time-right {
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
  font-size: 8px;
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

/* 操作按钮 */
.action-section {
  text-align: center;
  padding: 20px 0;
}

.generate-btn {
  width: 200px;
  height: 50px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 6px;
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

