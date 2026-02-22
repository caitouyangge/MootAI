import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '@/utils/request'

// localStorage 键名
const CASE_ID_KEY = 'caseId'

// 从 localStorage 加载 caseId
const loadCaseIdFromStorage = () => {
  try {
    if (typeof localStorage !== 'undefined') {
      const stored = localStorage.getItem(CASE_ID_KEY)
      if (stored) {
        const id = parseInt(stored, 10)
        return isNaN(id) ? null : id
      }
    }
  } catch (error) {
    console.error('从 localStorage 加载 caseId 失败:', error)
  }
  return null
}

// 保存 caseId 到 localStorage
const saveCaseIdToStorage = (id) => {
  try {
    if (typeof localStorage !== 'undefined') {
      if (id) {
        localStorage.setItem(CASE_ID_KEY, String(id))
      } else {
        localStorage.removeItem(CASE_ID_KEY)
      }
    }
  } catch (error) {
    console.error('保存 caseId 到 localStorage 失败:', error)
  }
}

// 初始化 caseId（从 localStorage 恢复）
const initCaseId = loadCaseIdFromStorage()

export const useCaseStore = defineStore('case', () => {
  // 身份选择
  const selectedIdentity = ref('')
  
  // 文件列表
  const fileList = ref([])
  
  // 文件是否已确认
  const filesConfirmed = ref(false)
  
  // 案件描述
  const caseDescription = ref('')
  
  // 案件ID（从 localStorage 初始化）
  const caseId = ref(initCaseId)
  
  // 法官类型
  const selectedJudgeType = ref('')
  
  // 对方AI律师的辩论策略
  const opponentStrategy = ref('')
  
  // 是否正在加载案件信息
  const loading = ref(false)
  
  // 设置身份
  const setIdentity = (identity) => {
    selectedIdentity.value = identity
  }
  
  // 设置案件ID（同时保存到 localStorage）
  const setCaseId = (id) => {
    caseId.value = id
    saveCaseIdToStorage(id)
  }
  
  // 设置文件列表
  const setFileList = (files) => {
    fileList.value = files
  }
  
  // 确认文件
  const confirmFiles = () => {
    filesConfirmed.value = true
  }
  
  // 重置确认状态
  const resetConfirm = () => {
    filesConfirmed.value = false
  }
  
  // 设置案件描述
  const setCaseDescription = (description) => {
    caseDescription.value = description
  }
  
  // 设置法官类型
  const setJudgeType = (judgeType) => {
    selectedJudgeType.value = judgeType
  }
  
  // 设置对方AI律师的辩论策略
  const setOpponentStrategy = (strategy) => {
    opponentStrategy.value = strategy
  }
  
  // 从数据库加载案件信息
  const loadCaseFromDatabase = async (id) => {
    if (!id) {
      console.warn('案件ID为空，无法加载案件信息')
      return false
    }
    
    loading.value = true
    try {
      const response = await request.get(`/cases/${id}`)
      if (response.code === 200 && response.data) {
        const caseData = response.data
        
        // 恢复案件信息
        if (caseData.identity) {
          selectedIdentity.value = caseData.identity
        }
        if (caseData.caseDescription) {
          caseDescription.value = caseData.caseDescription
        }
        if (caseData.judgeType) {
          selectedJudgeType.value = caseData.judgeType
        }
        if (caseData.opponentStrategy) {
          opponentStrategy.value = caseData.opponentStrategy
        }
        
        // 恢复文件列表（从文件名列表重建）
        if (caseData.fileNames && caseData.fileNames.length > 0) {
          // 文件已经上传到服务器，所以标记为已上传
          fileList.value = caseData.fileNames.map(fileName => ({
            name: fileName,
            uploaded: true,
            uploading: false,
            content: null,
            raw: null // File 对象无法恢复
          }))
        }
        
        caseId.value = caseData.id
        return true
      } else {
        console.error('加载案件信息失败:', response.message)
        return false
      }
    } catch (error) {
      console.error('加载案件信息异常:', error)
      return false
    } finally {
      loading.value = false
    }
  }
  
  // 重置所有状态
  const reset = () => {
    selectedIdentity.value = ''
    fileList.value = []
    filesConfirmed.value = false
    caseDescription.value = ''
    caseId.value = null
    selectedJudgeType.value = ''
    opponentStrategy.value = ''
    // 清除 localStorage 中的 caseId
    saveCaseIdToStorage(null)
  }
  
  return {
    selectedIdentity,
    fileList,
    filesConfirmed,
    caseDescription,
    caseId,
    selectedJudgeType,
    opponentStrategy,
    loading,
    setIdentity,
    setFileList,
    confirmFiles,
    resetConfirm,
    setCaseDescription,
    setCaseId,
    setJudgeType,
    setOpponentStrategy,
    loadCaseFromDatabase,
    reset
  }
})

