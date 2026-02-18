import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCaseStore = defineStore('case', () => {
  // 身份选择
  const selectedIdentity = ref('')
  
  // 文件列表
  const fileList = ref([])
  
  // 文件是否已确认
  const filesConfirmed = ref(false)
  
  // 案件描述
  const caseDescription = ref('')
  
  // 案件ID
  const caseId = ref(null)
  
  // 法官类型
  const selectedJudgeType = ref('')
  
  // 对方AI律师的辩论策略
  const opponentStrategy = ref('')
  
  // 设置身份
  const setIdentity = (identity) => {
    selectedIdentity.value = identity
  }
  
  // 设置案件ID
  const setCaseId = (id) => {
    caseId.value = id
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
  
  // 重置所有状态
  const reset = () => {
    selectedIdentity.value = ''
    fileList.value = []
    filesConfirmed.value = false
    caseDescription.value = ''
    caseId.value = null
    selectedJudgeType.value = ''
    opponentStrategy.value = ''
  }
  
  return {
    selectedIdentity,
    fileList,
    filesConfirmed,
    caseDescription,
    caseId,
    selectedJudgeType,
    opponentStrategy,
    setIdentity,
    setFileList,
    confirmFiles,
    resetConfirm,
    setCaseDescription,
    setCaseId,
    setJudgeType,
    setOpponentStrategy,
    reset
  }
})

