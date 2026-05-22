<template>
  <div class="call-controls">
    <div class="timer">
      <el-icon><Timer /></el-icon>
      <span>{{ formattedDuration }}</span>
    </div>

    <div class="control-buttons">
      <!-- 静音按钮 -->
      <el-button
        circle
        size="large"
        :type="isMuted ? 'danger' : 'default'"
        @click="$emit('toggleMute')"
        title="静音/取消静音"
      >
        <el-icon>
          <Microphone v-if="!isMuted" />
          <Mute v-else />
        </el-icon>
      </el-button>

      <!-- 视频开关按钮（仅视频通话显示） -->
      <el-button
        v-if="callType === 'video'"
        circle
        size="large"
        :type="isVideoOff ? 'danger' : 'default'"
        @click="$emit('toggleVideo')"
        title="开启/关闭视频"
      >
        <el-icon>
          <VideoCamera v-if="!isVideoOff" />
          <VideoCameraFilled v-else />
        </el-icon>
      </el-button>

      <!-- 挂断按钮 -->
      <el-button
        circle
        size="large"
        type="danger"
        @click="$emit('endCall')"
        title="结束通话"
      >
        <el-icon>
          <PhoneFilled />
        </el-icon>
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Timer, Microphone, Mute, VideoCamera, VideoCameraFilled, PhoneFilled } from '@element-plus/icons-vue'
import { formatDuration } from '@/utils/webrtc'

const props = defineProps({
  duration: {
    type: Number,
    default: 0
  },
  isMuted: {
    type: Boolean,
    default: false
  },
  isVideoOff: {
    type: Boolean,
    default: false
  },
  callType: {
    type: String,
    default: 'video'
  }
})

defineEmits(['toggleMute', 'toggleVideo', 'endCall'])

const formattedDuration = computed(() => formatDuration(props.duration))
</script>

<style lang="scss" scoped>
.call-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.8), transparent);
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  z-index: 10;

  .timer {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #fff;
    font-size: 18px;
    font-weight: 600;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
  }

  .control-buttons {
    display: flex;
    gap: 12px;

    :deep(.el-button) {
      width: 50px;
      height: 50px;
      font-size: 20px;
      transition: all 0.3s;

      &:hover {
        transform: scale(1.1);
      }
    }
  }
}
</style>
