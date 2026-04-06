<template>
  <div class="privacy-settings">
    <PageHeader />

    <div class="container">
      <!-- 顶部导航 -->
      <div class="page-header">
        <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
        <h2>隐私设置</h2>
      </div>

      <!-- 隐私设置卡片 -->
      <el-card v-loading="loading" class="settings-card">
        <!-- 对话隐私 -->
        <div class="setting-section">
          <h3>
            <el-icon><ChatDotSquare /></el-icon>
            对话隐私
          </h3>
          <p class="section-desc">控制您的AI对话记录的保存和可见性</p>

          <div class="setting-list">
            <div class="setting-item">
              <div class="setting-info">
                <span class="setting-label">保存对话历史</span>
                <span class="setting-desc">开启后，您的对话记录将被保存</span>
              </div>
              <el-switch
                v-model="settings.saveChatHistory"
                @change="handleSettingChange"
              />
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <span class="setting-label">允许AI学习我的对话数据</span>
                <span class="setting-desc">对话数据已脱敏处理</span>
              </div>
              <el-switch
                v-model="settings.allowAIAnalysis"
                @change="handleSettingChange"
              />
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <span class="setting-label">对话内容仅自己可见</span>
                <span class="setting-desc">关闭后，对话内容可用于改善服务</span>
              </div>
              <el-switch
                v-model="settings.chatOnlyVisible"
                @change="handleSettingChange"
              />
            </div>
          </div>
        </div>

        <el-divider />

        <!-- 测试隐私 -->
        <div class="setting-section">
          <h3>
            <el-icon><DocumentCopy /></el-icon>
            测试隐私
          </h3>
          <p class="section-desc">控制您的心理测试记录的保存和可见性</p>

          <div class="setting-list">
            <div class="setting-item">
              <div class="setting-info">
                <span class="setting-label">保存测试记录</span>
                <span class="setting-desc">开启后，您的测试记录将被保存</span>
              </div>
              <el-switch
                v-model="settings.saveTestRecords"
                @change="handleSettingChange"
              />
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <span class="setting-label">测试结果仅自己可见</span>
                <span class="setting-desc">关闭后，可用于生成统计数据</span>
              </div>
              <el-switch
                v-model="settings.testOnlyVisible"
                @change="handleSettingChange"
              />
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <span class="setting-label">允许查看测试趋势分析</span>
                <span class="setting-desc">需要保存测试记录才能查看</span>
              </div>
              <el-switch
                v-model="settings.allowTrendAnalysis"
                @change="handleSettingChange"
              />
            </div>
          </div>
        </div>

        <el-divider />

        <!-- 数据安全 -->
        <div class="setting-section">
          <h3>
            <el-icon><Lock /></el-icon>
            数据安全
          </h3>
          <p class="section-desc">管理您的个人数据</p>

          <div class="action-list">
            <div class="action-item">
              <div class="action-info">
                <span class="action-label">清除所有对话记录</span>
                <span class="action-desc">此操作不可恢复</span>
              </div>
              <el-button
                type="danger"
                :icon="Delete"
                @click="handleClearChat"
              >
                清除
              </el-button>
            </div>

            <div class="action-item">
              <div class="action-info">
                <span class="action-label">清除所有测试记录</span>
                <span class="action-desc">此操作不可恢复</span>
              </div>
              <el-button
                type="danger"
                :icon="Delete"
                @click="handleClearTest"
              >
                清除
              </el-button>
            </div>

            <div class="action-item">
              <div class="action-info">
                <span class="action-label">注销账号</span>
                <span class="action-desc">永久删除账号和所有数据</span>
              </div>
              <el-button
                type="danger"
                :icon="WarningFilled"
                @click="handleDeleteAccount"
              >
                注销账号
              </el-button>
            </div>
          </div>
        </div>

        <!-- 保存按钮 -->
        <div class="save-section">
          <el-button
            type="primary"
            size="large"
            :loading="saving"
            @click="saveSettings"
          >
            保存设置
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  ChatDotSquare,
  DocumentCopy,
  Lock,
  Delete,
  WarningFilled
} from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getPrivacySettings, updatePrivacySettings } from '@/api/user'
import { clearChatHistory, clearTestRecords } from '@/api/user'

const router = useRouter()

// 加载状态
const loading = ref(true)
const saving = ref(false)

// 设置项
const settings = reactive({
  saveChatHistory: true,
  allowAIAnalysis: false,
  chatOnlyVisible: false,
  saveTestRecords: true,
  testOnlyVisible: false,
  allowTrendAnalysis: true
})

// 加载隐私设置
const loadSettings = async () => {
  try {
    loading.value = true
    const res = await getPrivacySettings()
    Object.assign(settings, res.data)
  } catch (error) {
    console.error('加载设置失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 设置项变化（自动保存）
const handleSettingChange = () => {
  // 可以在这里实现自动保存逻辑
  ElMessage.success('设置已更新')
}

// 保存设置
const saveSettings = async () => {
  try {
    saving.value = true
    await updatePrivacySettings(settings)
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 清除对话记录
const handleClearChat = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清除所有对话记录吗？此操作不可恢复。',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await clearChatHistory()
    ElMessage.success('清除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清除失败:', error)
      ElMessage.error('清除失败')
    }
  }
}

// 清除测试记录
const handleClearTest = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清除所有测试记录吗？此操作不可恢复。',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await clearTestRecords()
    ElMessage.success('清除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清除失败:', error)
      ElMessage.error('清除失败')
    }
  }
}

// 注销账号
const handleDeleteAccount = async () => {
  try {
    await ElMessageBox.confirm(
      '注销后，您的账号和所有数据将被永久删除，无法恢复。确定要注销吗？',
      '警告',
      {
        confirmButtonText: '确定注销',
        cancelButtonText: '取消',
        type: 'error',
        inputPlaceholder: '请输入"确认注销"以确认',
        inputPattern: /确认注销/,
        inputErrorMessage: '请输入"确认注销"以确认',
        beforeClose: async (action, instance, done) => {
          if (action === 'confirm') {
            instance.confirmButtonLoading = true
            try {
              // 这里应该调用注销账号的API
              // await deleteAccount()
              done()
            } catch (error) {
              done()
            }
          } else {
            done()
          }
        }
      }
    )

    ElMessage.success('账号注销成功')
    // 跳转到首页
    router.push('/')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('注销失败:', error)
    }
  }
}

// 返回
const goBack = () => {
  router.push('/profile')
}

// 组件挂载
onMounted(() => {
  loadSettings()
})
</script>


<style lang="scss" scoped>
@use "@/styles/variables.scss" as *;

.privacy-settings-page {
  min-height: 100vh;
  background: $bg-page;
  padding-top: $header-height;
}

.container {
  max-width: 700px;
  margin: 0 auto;
  padding: 40px 24px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 28px;

  h2 { margin: 0; font-size: 24px; font-weight: 700; color: $text-primary; }
}

.settings-card {
  border-radius: 20px !important;
  border: 1px solid $border-lighter !important;
  box-shadow: 0 4px 20px rgba(107,82,68,0.08) !important;
  margin-bottom: 20px;

  :deep(.el-card__header) {
    font-weight: 600;
    color: $text-primary;
    border-bottom: 1px solid $border-lighter;
    padding: 18px 24px;
  }

  :deep(.el-card__body) { padding: 28px 24px; }
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0;
  border-bottom: 1px solid $border-lighter;

  &:last-child { border-bottom: none; }

  .setting-info {
    flex: 1;

    .setting-label { font-weight: 500; color: $text-primary; margin-bottom: 4px; font-size: 15px; }
    .setting-desc { font-size: 13px; color: $text-secondary; }
  }
}

.danger-zone {
  border-color: rgba(230, 80, 60, 0.2) !important;

  .danger-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 0;
    border-bottom: 1px solid $border-lighter;

    &:last-child { border-bottom: none; }

    .item-info {
      .item-label { font-weight: 500; color: #c0392b; margin-bottom: 4px; }
      .item-desc { font-size: 13px; color: $text-secondary; }
    }
  }
}

.save-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
