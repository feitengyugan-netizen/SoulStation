<template>
  <div class="video-call-button">
    <el-dropdown trigger="click" @command="handlePreCheck">
      <el-button type="primary" :loading="calling" :disabled="!canCall">
        <el-icon><VideoCamera /></el-icon>
        <span>{{ calling ? '连接中...' : '开始通话' }}</span>
        <el-icon class="el-icon--right"><ArrowDown /></el-icon>
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="video">
            <el-icon><VideoCamera /></el-icon>
            视频通话
          </el-dropdown-item>
          <el-dropdown-item command="voice">
            <el-icon><Microphone /></el-icon>
            语音通话
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>

    <!-- 设备检测弹窗 -->
    <DeviceCheck
      v-if="showDeviceCheck"
      v-model="showDeviceCheck"
      :call-type="pendingCallType"
      @start="handleDeviceConfirmed"
      @cancel="handleDeviceCancelled"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoCamera, Microphone, ArrowDown } from '@element-plus/icons-vue'
import { useVideoCallStore } from '@/stores/videoCall'
import { useUserStore } from '@/stores/user'
import DeviceCheck from './DeviceCheck.vue'

const props = defineProps({
  appointmentId: { type: Number, required: true },
  canCall: { type: Boolean, default: true }
})

const emit = defineEmits(['call-started'])

const videoCallStore = useVideoCallStore()

const showDeviceCheck = ref(false)
const pendingCallType = ref('video')

const calling = computed(() =>
  videoCallStore.callStatus === 'initiating' || videoCallStore.callStatus === 'calling'
)

// 第一步：选择通话类型后打开设备检测
function handlePreCheck(callType) {
  if (!props.canCall) {
    ElMessage.warning('当前状态无法发起通话')
    return
  }
  pendingCallType.value = callType
  showDeviceCheck.value = true
}

// 第二步：设备检测通过后，真正发起通话
async function handleDeviceConfirmed(devicePrefs) {
  try {
    // 保存设备偏好到 store
    videoCallStore.setDevicePreferences(devicePrefs)
    await videoCallStore.initiateVideoCall(props.appointmentId, pendingCallType.value)
    ElMessage.success('通话已发起')
    emit('call-started', {
      sessionId: videoCallStore.sessionId,
      callType: pendingCallType.value
    })
  } catch (error) {
    ElMessage.error(error.message || '发起通话失败')
  }
}

// 取消设备检测
function handleDeviceCancelled() {
  pendingCallType.value = 'video'
}
</script>

<style lang="scss" scoped>
.video-call-button {
  display: inline-block;
}
</style>
