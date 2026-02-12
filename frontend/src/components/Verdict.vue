<template>
  <div class="verdict-container">
    <!-- 主标题 -->
    <div class="verdict-header">
      <h1 class="verdict-title">民事判决书</h1>
      <el-button 
        v-if="!loading && !verdictText" 
        type="primary" 
        @click="generateVerdict"
        :loading="loading"
      >
        生成判决书
      </el-button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-section">
      <ElIcon class="is-loading"><Loading /></ElIcon>
      <p>正在生成判决书，请稍候...</p>
    </div>

    <!-- 判决书内容 -->
    <div v-else-if="verdictText" class="verdict-content">
      <!-- 如果解析成功，显示结构化内容 -->
      <template v-if="verdictInfo.basicInfo || verdictInfo.facts">
        <!-- 案件基本信息 -->
        <div v-if="verdictInfo.basicInfo" class="verdict-section">
          <h2 class="section-title">案件基本信息</h2>
          <div class="section-content">
            {{ verdictInfo.basicInfo }}
          </div>
        </div>

    <!-- 审理经过 -->
    <div class="verdict-section">
      <h2 class="section-title">审理经过</h2>
      <div class="section-content">
        <div class="content-item">
          <h3 class="item-title">起诉时间和事实</h3>
          <p>{{ verdictInfo.proceedings.filingTime }}</p>
        </div>
        <div class="content-item">
          <h3 class="item-title">审理过程概述</h3>
          <p>{{ verdictInfo.proceedings.process }}</p>
        </div>
        <div class="content-item">
          <h3 class="item-title">当事人主要争议点</h3>
          <p>{{ verdictInfo.proceedings.disputes }}</p>
        </div>
      </div>
    </div>

    <!-- 当事人诉讼请求和答辩 -->
    <div class="verdict-section">
      <h2 class="section-title">当事人诉讼请求和答辩</h2>
      <div class="section-content">
        <div class="content-item">
          <h3 class="item-title">原告诉讼请求</h3>
          <p>{{ verdictInfo.requests.plaintiff }}</p>
        </div>
        <div class="content-item">
          <h3 class="item-title">被告的答辩意见</h3>
          <p>{{ verdictInfo.requests.defendant }}</p>
        </div>
        <div class="content-item">
          <h3 class="item-title">争议的主要问题</h3>
          <p>{{ verdictInfo.requests.mainIssues }}</p>
        </div>
      </div>
    </div>

    <!-- 本院查明的事实 -->
    <div class="verdict-section">
      <h2 class="section-title">本院查明的事实</h2>
      <div class="section-content">
        {{ verdictInfo.facts }}
      </div>
    </div>

        <!-- 本院认为 -->
        <div v-if="verdictInfo.opinion.lawAnalysis" class="verdict-section">
          <h2 class="section-title">本院认为</h2>
          <div class="section-content">
            <div class="content-item">
              <h3 class="item-title">法律适用分析</h3>
              <p>{{ verdictInfo.opinion.lawAnalysis }}</p>
            </div>
            <div v-if="verdictInfo.opinion.legalJudgment" class="content-item">
              <h3 class="item-title">对争议问题的法律判断</h3>
              <p>{{ verdictInfo.opinion.legalJudgment }}</p>
            </div>
            <div v-if="verdictInfo.opinion.liability" class="content-item">
              <h3 class="item-title">责任认定和理由</h3>
              <p>{{ verdictInfo.opinion.liability }}</p>
            </div>
          </div>
        </div>
      </template>
      
      <!-- 如果解析失败，直接显示全文 -->
      <div v-else class="verdict-section">
        <div class="section-content" style="white-space: pre-line;">
          {{ verdictText }}
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-section">
      <p>点击"生成判决书"按钮生成判决书</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useCaseStore } from '@/stores/case'
import request from '@/utils/request'
import { ElMessage, ElButton, ElIcon } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'

const route = useRoute()
const caseStore = useCaseStore()

// 获取案件信息
const caseDescription = ref(caseStore.caseDescription || route.query.description || '')
const identity = ref(caseStore.selectedIdentity || route.query.identity || 'plaintiff')
const messages = ref([]) // 庭审对话历史，从Debate组件获取

// 判决书内容
const verdictInfo = ref({
  basicInfo: '',
  proceedings: {
    filingTime: '',
    process: '',
    disputes: ''
  },
  requests: {
    plaintiff: '',
    defendant: '',
    mainIssues: ''
  },
  facts: '',
  opinion: {
    lawAnalysis: '',
    legalJudgment: '',
    liability: ''
  }
})

const loading = ref(false)
const verdictText = ref('')

// 解析判决书文本
const parseVerdict = (text) => {
  // 尝试解析AI生成的判决书文本
  // 如果AI返回的是结构化文本，尝试解析；否则直接显示
  verdictText.value = text
  
  // 简单的文本解析逻辑（可以根据实际AI返回格式调整）
  const lines = text.split('\n')
  let currentSection = ''
  let currentContent = []
  
  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed) continue
    
    // 识别章节
    if (trimmed.includes('案件基本信息') || trimmed.includes('基本信息')) {
      currentSection = 'basicInfo'
      currentContent = []
    } else if (trimmed.includes('审理经过')) {
      if (currentSection === 'basicInfo') {
        verdictInfo.value.basicInfo = currentContent.join('\n')
      }
      currentSection = 'proceedings'
      currentContent = []
    } else if (trimmed.includes('当事人诉讼请求') || trimmed.includes('诉讼请求')) {
      if (currentSection === 'proceedings') {
        verdictInfo.value.proceedings.filingTime = currentContent.join('\n')
      }
      currentSection = 'requests'
      currentContent = []
    } else if (trimmed.includes('本院查明') || trimmed.includes('查明的事实')) {
      if (currentSection === 'requests') {
        verdictInfo.value.requests.plaintiff = currentContent.join('\n')
      }
      currentSection = 'facts'
      currentContent = []
    } else if (trimmed.includes('本院认为')) {
      if (currentSection === 'facts') {
        verdictInfo.value.facts = currentContent.join('\n')
      }
      currentSection = 'opinion'
      currentContent = []
    } else {
      currentContent.push(trimmed)
    }
  }
  
  // 保存最后一部分
  if (currentSection === 'opinion' && currentContent.length > 0) {
    verdictInfo.value.opinion.lawAnalysis = currentContent.join('\n')
  } else if (currentSection === 'basicInfo' && currentContent.length > 0) {
    verdictInfo.value.basicInfo = currentContent.join('\n')
  }
  
  // 如果解析失败，直接显示全文
  if (!verdictInfo.value.basicInfo && !verdictInfo.value.facts) {
    verdictInfo.value.basicInfo = text
  }
}

// 生成判决书
const generateVerdict = async () => {
  if (!caseDescription.value) {
    ElMessage.warning('缺少案件描述信息')
    return
  }
  
  loading.value = true
  
  try {
    // 尝试从localStorage或sessionStorage获取庭审对话历史
    const debateMessages = JSON.parse(localStorage.getItem('debateMessages') || '[]')
    
    const response = await request.post('/debate/verdict', {
      caseDescription: caseDescription.value,
      messages: debateMessages,
      identity: identity.value
    })
    
    if (response.code === 200 && response.data) {
      parseVerdict(response.data)
      ElMessage.success('判决书生成成功')
    } else {
      throw new Error(response.message || '生成判决书失败')
    }
  } catch (error) {
    console.error('生成判决书失败:', error)
    ElMessage.error(error.response?.data?.message || error.message || '生成判决书失败，请重试')
  } finally {
    loading.value = false
  }
}

// 组件挂载时自动生成判决书
onMounted(() => {
  generateVerdict()
})
</script>

<style scoped>
.verdict-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.verdict-header {
  text-align: center;
  padding: 12px 0;
  border-bottom: 2px solid #409eff;
  margin-bottom: 10px;
}

.verdict-title {
  font-size: 12px;
  color: #333;
  margin: 0;
  font-weight: 700;
}

.verdict-section {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 12px;
}

.section-title {
  font-size: 12px;
  color: #409eff;
  margin: 0 0 8px 0;
  font-weight: 600;
  padding-bottom: 6px;
  border-bottom: 2px solid #e0e0e0;
}

.section-content {
  font-size: 12px;
  color: #333;
  line-height: 1.8;
  white-space: pre-line;
}

.content-item {
  margin-bottom: 8px;
}

.content-item:last-child {
  margin-bottom: 0;
}

.item-title {
  font-size: 12px;
  color: #409eff;
  margin: 0 0 6px 0;
  font-weight: 600;
}

.content-item p {
  margin: 0;
  padding-left: 15px;
  line-height: 1.8;
}

.loading-section {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

.loading-section .el-icon {
  font-size: 32px;
  margin-bottom: 16px;
}

.empty-section {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

.verdict-content {
  margin-top: 16px;
}
</style>

