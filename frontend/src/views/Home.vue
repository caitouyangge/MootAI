<template>
  <div class="courtroom-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">AI模拟法庭</h1>
      <p class="page-subtitle">智能诉讼审判模拟系统</p>
    </div>
    
    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 身份选择区域 -->
      <div class="identity-section">
        <h2 class="section-title">选择身份</h2>
        <div class="identity-buttons">
          <el-button
            :type="selectedIdentity === 'plaintiff' ? 'primary' : ''"
            :class="{ 'selected': selectedIdentity === 'plaintiff' }"
            @click="selectIdentity('plaintiff')"
            class="identity-btn"
          >
            原告
          </el-button>
          <el-button
            :type="selectedIdentity === 'defendant' ? 'primary' : ''"
            :class="{ 'selected': selectedIdentity === 'defendant' }"
            @click="selectIdentity('defendant')"
            class="identity-btn"
          >
            被告
          </el-button>
        </div>
        <div v-if="selectedIdentity" class="identity-tip">
          当前身份：{{ selectedIdentity === 'plaintiff' ? '原告' : '被告' }}
        </div>
      </div>

      <!-- 文件上传区域 -->
      <div class="upload-section">
        <h2 class="section-title">上传案件资料</h2>
        <div class="upload-buttons">
          <el-button
            type="primary"
            class="upload-btn"
            @click="triggerUpload"
          >
            选择文件上传
          </el-button>
          <el-button
            v-if="fileList.length > 0 && !filesConfirmed"
            type="success"
            class="confirm-btn"
            @click="confirmFiles"
          >
            确认文件
          </el-button>
        </div>
        <input
          ref="fileInput"
          type="file"
          multiple
          style="display: none"
          @change="handleFileChange"
        />
        <div v-if="fileList.length > 0" class="file-list">
          <div v-for="(file, index) in fileList" :key="index" class="file-item">
            <span>{{ file.name }}</span>
            <el-button
              v-if="!filesConfirmed"
              text
              type="danger"
              @click="removeFile(index)"
              class="remove-btn"
            >
              删除
            </el-button>
          </div>
        </div>
      </div>

      <!-- 案件描述区域 -->
      <div class="case-description-section">
        <h2 class="section-title">案件描述</h2>
        <el-input
          v-model="caseDescription"
          type="textarea"
          :rows="3"
          placeholder="案件描述将由系统自动生成或后续添加..."
          :readonly="!filesConfirmed"
          class="description-textarea"
        />
        <div v-if="!filesConfirmed" class="description-tip">
          请先确认文件，系统将自动生成案件描述
        </div>
        <div v-else class="description-tip">
          您可以编辑上述内容进行调整
        </div>
        <el-button
          v-if="filesConfirmed && caseDescription"
          type="primary"
          class="start-btn"
          @click="startSimulation"
        >
          开始模拟
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 身份选择
const selectedIdentity = ref('')

const selectIdentity = (identity) => {
  selectedIdentity.value = identity
  ElMessage.success(`已选择身份：${identity === 'plaintiff' ? '原告' : '被告'}`)
}

// 文件上传
const fileList = ref([])
const fileInput = ref(null)
const filesConfirmed = ref(false)

const triggerUpload = () => {
  fileInput.value?.click()
}

const handleFileChange = (event) => {
  const files = Array.from(event.target.files)
  files.forEach(file => {
    fileList.value.push({
      name: file.name,
      raw: file
    })
  })
  ElMessage.success(`已添加 ${files.length} 个文件`)
  // 清空input，允许重复选择同一文件
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const removeFile = (index) => {
  fileList.value.splice(index, 1)
  ElMessage.info('文件已移除')
}

// 确认文件并生成案件描述
const confirmFiles = () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先上传文件')
    return
  }
  
  // 模拟AI处理，生成案件描述
  ElMessage.info('正在分析文件，生成案件描述...')
  
  setTimeout(() => {
    // 使用固定的默认描述文字
    caseDescription.value = `案件基本情况：
本案涉及一起合同纠纷案件。原告与被告于2023年1月签订了一份服务合同，约定被告向原告提供技术服务，合同金额为50万元。合同签订后，原告按约定支付了首付款30万元，但被告未能按合同约定提供服务，导致原告遭受经济损失。

争议焦点：
1. 被告是否存在违约行为
2. 原告的经济损失如何计算
3. 合同解除后的责任承担问题

相关法条：
《中华人民共和国民法典》第五百七十七条：当事人一方不履行合同义务或者履行合同义务不符合约定的，应当承担继续履行、采取补救措施或者赔偿损失等违约责任。
《中华人民共和国民法典》第五百六十三条：有下列情形之一的，当事人可以解除合同：（一）因不可抗力致使不能实现合同目的；（二）在履行期限届满前，当事人一方明确表示或者以自己的行为表明不履行主要债务；（三）当事人一方迟延履行主要债务，经催告后在合理期限内仍未履行；（四）当事人一方迟延履行债务或者有其他违约行为致使不能实现合同目的；（五）法律规定的其他情形。

案件要素：
- 合同类型：技术服务合同
- 合同金额：50万元
- 已支付金额：30万元
- 争议金额：30万元及违约金
- 合同签订时间：2023年1月
- 违约发生时间：2023年3月`
    
    filesConfirmed.value = true
    ElMessage.success('案件描述已生成，您可以进行编辑调整')
  }, 1500)
}

// 案件描述
const caseDescription = ref('')

// 开始模拟
const startSimulation = () => {
  if (!selectedIdentity.value) {
    ElMessage.warning('请先选择身份')
    return
  }
  if (!caseDescription.value) {
    ElMessage.warning('请先确认文件并生成案件描述')
    return
  }
  
  // 跳转到模拟法庭界面
  router.push({
    name: 'courtroom',
    query: {
      identity: selectedIdentity.value,
      description: caseDescription.value
    }
  })
}
</script>

<style scoped>
.courtroom-container {
  width: 100%;
  min-height: 100vh;
  background: #ededed;
  padding: 20px;
  overflow: auto;
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px 0;
}

.page-title {
  font-size: 28px;
  color: #333;
  margin: 0 0 10px 0;
  font-weight: 600;
}

.page-subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* 主要内容 */
.main-content {
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 通用卡片样式 */
.identity-section,
.upload-section,
.case-description-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  width: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.section-title {
  font-size: 16px;
  color: #333;
  margin: 0 0 15px 0;
  font-weight: 600;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
}

/* 身份选择 */
.identity-buttons {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.identity-btn {
  flex: 1;
  height: 44px;
  font-size: 15px;
  border-radius: 6px;
  border: 2px solid #d9d9d9;
  background: white;
  color: #333;
  transition: all 0.3s;
}

.identity-btn:hover {
  border-color: #07c160;
  color: #07c160;
  transform: translateY(-2px);
}

.identity-btn.selected {
  background: #07c160;
  border-color: #07c160;
  color: white;
}

.identity-tip {
  text-align: center;
  color: #07c160;
  font-size: 13px;
  margin-top: 10px;
  padding: 8px;
  background: #f0f9ff;
  border-radius: 4px;
}

/* 文件上传 */
.upload-buttons {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.upload-btn {
  flex: 1;
  height: 44px;
  font-size: 15px;
  border-radius: 6px;
  background: #07c160;
  border-color: #07c160;
}

.upload-btn:hover {
  background: #06ad56;
  border-color: #06ad56;
}

.confirm-btn {
  flex: 1;
  height: 44px;
  font-size: 15px;
  border-radius: 6px;
  background: #07c160;
  border-color: #07c160;
}

.confirm-btn:hover {
  background: #06ad56;
  border-color: #06ad56;
}

.file-list {
  margin-top: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: #f7f7f7;
  border-radius: 6px;
  border-left: 4px solid #07c160;
  transition: all 0.3s;
}

.file-item:hover {
  background: #f0f0f0;
  transform: translateX(5px);
}

.file-item span {
  flex: 1;
  color: #333;
  font-size: 13px;
}

.remove-btn {
  margin-left: 10px;
  font-size: 13px;
  color: #fa5151;
}

/* 案件描述 */
.description-textarea {
  width: 100%;
  margin-bottom: 15px;
}

:deep(.description-textarea .el-textarea__inner) {
  background: #ffffff;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  color: #333;
  font-size: 14px;
  resize: vertical;
  padding: 12px;
  min-height: 120px;
  max-height: 400px;
  line-height: 1.6;
}

:deep(.el-button--primary) {
  background-color: #07c160;
  border-color: #07c160;
}

:deep(.el-button--primary:hover) {
  background-color: #06ad56;
  border-color: #06ad56;
}

:deep(.description-textarea .el-textarea__inner[readonly]) {
  background: #f7f7f7;
  color: #666;
  cursor: not-allowed;
}

.description-tip {
  color: #999;
  font-size: 12px;
  text-align: center;
  margin-top: 10px;
  padding: 8px;
  background: #f9f9f9;
  border-radius: 4px;
}

.start-btn {
  width: 100%;
  height: 50px;
  font-size: 16px;
  border-radius: 6px;
  margin-top: 15px;
  background: #07c160;
  border-color: #07c160;
  font-weight: 600;
  transition: all 0.3s;
}

.start-btn:hover {
  background: #06ad56;
  border-color: #06ad56;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(7, 193, 96, 0.3);
}
</style>

