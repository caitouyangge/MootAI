<template>
  <div class="courtroom-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">模拟法庭</h1>
    </div>
    
    <div class="courtroom-wrapper">
      <!-- 顶部导航 -->
      <div class="nav-tabs">
        <el-button
          :type="activeTab === 'pretrial' ? 'primary' : ''"
          :class="{ 'active': activeTab === 'pretrial' }"
          @click="activeTab = 'pretrial'"
          class="nav-btn"
        >
          庭前准备
        </el-button>
        <el-button
          :type="activeTab === 'debate' ? 'primary' : ''"
          :class="{ 'active': activeTab === 'debate' }"
          @click="activeTab = 'debate'"
          class="nav-btn"
        >
          庭中辩论
        </el-button>
        <el-button
          :type="activeTab === 'verdict' ? 'primary' : ''"
          :class="{ 'active': activeTab === 'verdict' }"
          @click="activeTab = 'verdict'"
          class="nav-btn"
        >
          庭后宣判
        </el-button>
      </div>

      <!-- 内容区域 -->
      <div class="content-area">
        <PreTrial v-if="activeTab === 'pretrial'" />
        <Debate v-else-if="activeTab === 'debate'" />
        <div v-else-if="activeTab === 'verdict'" class="coming-soon">
          <p>庭后宣判功能开发中...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import PreTrial from '@/components/PreTrial.vue'
import Debate from '@/components/Debate.vue'

const route = useRoute()
const activeTab = ref('pretrial')

// 如果路由中有tab参数，切换到对应标签
onMounted(() => {
  if (route.query.tab) {
    activeTab.value = route.query.tab
  }
})
</script>

<style scoped>
.courtroom-page {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
  color: white;
  margin: 0;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.courtroom-wrapper {
  max-width: 800px;
  margin: 0 auto;
}

.nav-tabs {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 20px;
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  width: 100%;
}

.nav-btn {
  flex: 1;
  height: 40px;
  font-size: 14px;
  border-radius: 6px;
  padding: 0 15px;
  transition: all 0.3s;
}

.nav-btn:hover {
  transform: translateY(-2px);
}

.nav-btn.active {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border-color: #409eff;
  color: white;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.content-area {
  background: white;
  border-radius: 8px;
  padding: 20px;
  width: 100%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  min-height: 400px;
}

.coming-soon {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: #909399;
  font-size: 16px;
  padding: 40px;
}
</style>

