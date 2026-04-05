<template>
  <div class="voice-recorder">
    <!-- 录音按钮 -->
    <div class="microphone-wrapper">
      <el-select
        v-if="availableDevices.length > 1 && !isRecording"
        v-model="selectedDeviceId"
        placeholder="选择麦克风"
        size="small"
        class="device-selector"
        @change="handleDeviceChange"
      >
        <el-option
          v-for="device in availableDevices"
          :key="device.deviceId"
          :label="device.label"
          :value="device.deviceId"
        />
      </el-select>

      <el-button
        :icon="microphoneIcon"
        :type="isRecording ? 'danger' : 'default'"
        :disabled="isProcessing"
        @click="toggleRecording"
        circle
        size="large"
      />
    </div>

    <!-- 录音时长提示 -->
    <div v-if="isRecording" class="recording-info">
      <span class="recording-dot"></span>
      <span>{{ formattedDuration }}</span>
      <span v-if="volumeLevel > 0" class="volume-indicator">
        音量: {{ Math.round(volumeLevel * 100) }}%
      </span>
    </div>

    <!-- 音量条 -->
    <div v-if="isRecording" class="volume-bar-container">
      <div class="volume-bar" :style="{ width: `${volumeLevel * 100}%` }"></div>
    </div>

    <!-- 音量过低警告 -->
    <div v-if="isRecording && lowVolumeWarning" class="low-volume-warning">
      ⚠️ 检测不到声音，请靠近麦克风说话
    </div>

    <!-- 音频预览弹窗 -->
    <el-dialog
      v-model="previewVisible"
      title="录音预览"
      width="400px"
      :close-on-click-modal="false"
    >
      <div class="preview-content">
        <div class="recording-tip">
          <el-icon><InfoFilled /></el-icon>
          <span>请先播放音频确认录音清晰，然后点击"识别文字"</span>
        </div>

        <audio v-if="audioBlob" :src="audioUrl" controls class="audio-player"></audio>

        <div class="recording-info-detail">
          <span>时长: {{ formattedDuration }}</span>
          <span>大小: {{ (audioBlob?.size / 1024).toFixed(1) }} KB</span>
        </div>

        <div class="preview-actions">
          <el-button @click="cancelRecording">重录</el-button>
          <el-button type="primary" :loading="isTranscribing" @click="transcribeAudio">
            识别文字
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Microphone, Loading, InfoFilled } from '@element-plus/icons-vue'
import { getToken } from '@/utils/storage'

// Props
const props = defineProps({
  // 最大录音时长（秒）
  maxDuration: {
    type: Number,
    default: 60
  }
})

// Emits
const emit = defineEmits(['transcription-result'])

// 状态
const isRecording = ref(false)
const isProcessing = ref(false)
const isTranscribing = ref(false)
const previewVisible = ref(false)
const audioBlob = ref(null)
const recordingDuration = ref(0)
const volumeLevel = ref(0) // 音量级别 0-1
const lowVolumeWarning = ref(false) // 音量过低警告
const availableDevices = ref([]) // 可用的麦克风设备列表
const selectedDeviceId = ref('') // 当前选中的麦克风设备ID

// MediaRecorder 实例
let mediaRecorder = null
let audioChunks = []
let recordingTimer = null
let startTime = null
let selectedMimeType = 'audio/webm' // 记录实际使用的格式
let audioContext = null
let analyser = null
let microphone = null
let animationFrame = null

// 计算属性
const microphoneIcon = computed(() => {
  if (isProcessing.value || isTranscribing.value) {
    return Loading
  }
  return Microphone
})

const formattedDuration = computed(() => {
  const seconds = Math.floor(recordingDuration.value / 1000)
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
})

const audioUrl = computed(() => {
  if (!audioBlob.value) return ''
  return URL.createObjectURL(audioBlob.value)
})

// 获取可用的音频设备
const getAudioDevices = async () => {
  try {
    // 先请求一次权限以获取完整的设备列表
    await navigator.mediaDevices.getUserMedia({ audio: true })

    const devices = await navigator.mediaDevices.enumerateDevices()
    const audioInputs = devices.filter(device => device.kind === 'audioinput')

    availableDevices.value = audioInputs

    if (audioInputs.length > 0) {
      selectedDeviceId.value = audioInputs[0].deviceId
      console.log('🎤 检测到音频设备:', audioInputs.map(d => ({
        label: d.label,
        id: d.deviceId
      })))
    }

    // 关闭临时流
    // 注意：不要在这里关闭，否则会导致权限失效

  } catch (error) {
    console.error('❌ 获取音频设备失败:', error)
  }
}

// 处理设备切换
const handleDeviceChange = () => {
  console.log('🔄 切换麦克风设备:', selectedDeviceId.value)
  ElMessage.success('麦克风已切换')
}

// 组件挂载时获取设备列表
import { onMounted } from 'vue'
onMounted(() => {
  getAudioDevices()
})

// 开始录音
const startRecording = async () => {
  try {
    console.log('🎤 请求麦克风权限...')

    // 构建音频约束
    const audioConstraints = {
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true,
      sampleRate: 48000,
      channelCount: 1
    }

    // 如果有选中的设备，指定使用该设备
    if (selectedDeviceId.value) {
      audioConstraints.deviceId = {
        exact: selectedDeviceId.value
      }
      console.log('🎤 使用指定设备:', selectedDeviceId.value)
    }

    // 请求麦克风权限 - 使用更高的音频质量设置
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: audioConstraints
    })

    console.log('✅ 麦克风权限获取成功', {
      tracks: stream.getAudioTracks().length,
      trackSettings: stream.getAudioTracks()[0]?.getSettings(),
      trackEnabled: stream.getAudioTracks()[0]?.enabled,
      trackMuted: stream.getAudioTracks()[0]?.muted,
      trackLabel: stream.getAudioTracks()[0]?.label
    })

    // 创建 AudioContext 用于音量分析
    audioContext = new (window.AudioContext || window.webkitAudioContext)()
    console.log('🎵 AudioContext 已创建', {
      state: audioContext.state,
      sampleRate: audioContext.sampleRate
    })

    // 如果 AudioContext 被挂起，尝试恢复
    if (audioContext.state === 'suspended') {
      await audioContext.resume()
      console.log('🎵 AudioContext 已恢复')
    }

    analyser = audioContext.createAnalyser()
    analyser.fftSize = 256
    microphone = audioContext.createMediaStreamSource(stream)
    microphone.connect(analyser)
    console.log('🎤 音频分析器已连接')

    // 开始监测音量
    const dataArray = new Uint8Array(analyser.frequencyBinCount)
    let lowVolumeCount = 0
    let debugCounter = 0

    const checkVolume = () => {
      analyser.getByteFrequencyData(dataArray)

      // 计算平均音量
      const average = dataArray.reduce((a, b) => a + b) / dataArray.length
      const maxVolume = Math.max(...dataArray)
      volumeLevel.value = Math.min(average / 50, 1) // 降低阈值，提高灵敏度

      // 调试输出（每秒一次）
      debugCounter++
      if (debugCounter % 60 === 0) {
        console.log('🔊 音量数据:', {
          average: average.toFixed(2),
          max: maxVolume,
          volumeLevel: volumeLevel.value.toFixed(2),
          dataPreview: Array.from(dataArray.slice(0, 10))
        })
      }

      // 检测音量是否过低（连续3秒）- 降低阈值
      if (volumeLevel.value < 0.02) {
        lowVolumeCount++
        if (lowVolumeCount > 30) { // 约3秒
          lowVolumeWarning.value = true
          console.warn('⚠️ 音量过低，当前音量:', volumeLevel.value.toFixed(3))
        }
      } else {
        lowVolumeCount = 0
        lowVolumeWarning.value = false
      }

      animationFrame = requestAnimationFrame(checkVolume)
    }
    checkVolume()

    // 创建 MediaRecorder - 尝试使用更好的音频格式
    let options = { mimeType: 'audio/webm' }

    // 检查支持的格式，优先选择高质量格式
    const types = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/ogg;codecs=opus',
      'audio/mp4',
      'audio/mp3' // 部分浏览器支持
    ]

    for (const type of types) {
      if (MediaRecorder.isTypeSupported(type)) {
        options = {
          mimeType: type,
          audioBitsPerSecond: 128000 // 128kbps 音频比特率
        }
        selectedMimeType = type
        console.log('🎵 使用音频格式:', type)
        break
      }
    }

    mediaRecorder = new MediaRecorder(stream, options)
    console.log('📼 MediaRecorder 已创建', {
      state: mediaRecorder.state,
      mimeType: mediaRecorder.mimeType
    })

    audioChunks = []

    // 收集音频数据
    mediaRecorder.ondataavailable = (event) => {
      console.log('📦 收集音频数据:', event.data.size, 'bytes')
      if (event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }

    // 录音结束
    mediaRecorder.onstop = () => {
      console.log('⏹️ 录音停止，总数据块:', audioChunks.length)
      const blob = new Blob(audioChunks, { type: selectedMimeType })
      console.log('📄 音频 Blob 已创建:', {
        size: blob.size,
        type: blob.type
      })
      audioBlob.value = blob
      previewVisible.value = true

      // 停止音量监测
      if (animationFrame) {
        cancelAnimationFrame(animationFrame)
        animationFrame = null
      }
      volumeLevel.value = 0

      // 停止所有音频轨道
      stream.getTracks().forEach(track => track.stop())
      if (audioContext) {
        audioContext.close()
        audioContext = null
      }
    }

    // 开始录音
    mediaRecorder.start(100) // 每100ms收集一次数据
    console.log('🔴 MediaRecorder 已启动')

    // 延迟1秒后测试麦克风是否真的在工作
    setTimeout(() => {
      if (volumeLevel.value === 0) {
        console.warn('⚠️ 麦克风可能未正常工作，请检查:')
        console.warn('  1. 是否选择了正确的麦克风设备')
        console.warn('  2. 麦克风音量是否开启')
        console.warn('  3. 麦克风是否被其他应用占用')
        ElMessage.warning({
          message: '检测不到麦克风声音，请检查设备设置',
          duration: 5000
        })
      } else {
        console.log('✅ 麦克风工作正常，当前音量:', volumeLevel.value.toFixed(2))
      }
    }, 1000)

    startTime = Date.now()
    isRecording.value = true

    // 更新录音时长
    recordingTimer = setInterval(() => {
      const elapsed = Date.now() - startTime
      recordingDuration.value = elapsed

      // 检查是否超过最大时长
      if (elapsed >= props.maxDuration * 1000) {
        stopRecording()
        ElMessage.warning(`已达到最大录音时长 ${props.maxDuration} 秒`)
      }
    }, 100)

    ElMessage.success('开始录音...')

  } catch (error) {
    console.error('❌ 录音失败:', error)
    ElMessage.error(`无法访问麦克风: ${error.message}`)
  }
}

// 停止录音
const stopRecording = () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
    isRecording.value = false
    clearInterval(recordingTimer)
    lowVolumeWarning.value = false
  }
}

// 切换录音状态
const toggleRecording = () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

// 取消录音
const cancelRecording = () => {
  audioBlob.value = null
  recordingDuration.value = 0
  previewVisible.value = false
  lowVolumeWarning.value = false
}

// 获取文件扩展名
const getFileExtension = (mimeType) => {
  const extensions = {
    'audio/webm': 'webm',
    'audio/webm;codecs=opus': 'webm',
    'audio/ogg': 'ogg',
    'audio/ogg;codecs=opus': 'ogg',
    'audio/mp4': 'm4a',
    'audio/mp3': 'mp3'
  }
  return extensions[mimeType] || 'webm'
}

// 识别音频
const transcribeAudio = async () => {
  if (!audioBlob.value) {
    ElMessage.error('没有可识别的音频')
    return
  }

  // 检查录音时长（至少1秒）
  const minDuration = 1000 // 1秒
  if (recordingDuration.value < minDuration) {
    ElMessage.warning(`录音时间太短，请至少录制 ${minDuration / 1000} 秒`)
    return
  }

  // 检查文件大小（至少1KB）
  if (audioBlob.value.size < 1024) {
    ElMessage.warning('录音数据太小，请重新录制')
    return
  }

  isTranscribing.value = true

  try {
    // 创建 FormData - 使用正确的文件扩展名
    const fileExtension = getFileExtension(selectedMimeType)
    const formData = new FormData()
    formData.append('audio_file', audioBlob.value, `recording.${fileExtension}`)
    formData.append('language', 'zh-CN')

    console.log(`Uploading audio: format=${selectedMimeType}, size=${audioBlob.value.size} bytes, duration=${recordingDuration.value}ms`)

    // 获取 token
    const token = getToken()
    if (!token) {
      throw new Error('未登录')
    }

    // 调用后端 API
    const response = await fetch('http://localhost:8000/api/chat/voice-to-text', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '识别失败')
    }

    const result = await response.json()

    if (result.code === 200 && result.data.text) {
      ElMessage.success('识别成功')
      emit('transcription-result', result.data.text)
      previewVisible.value = false
    } else {
      throw new Error('识别结果为空')
    }

  } catch (error) {
    console.error('语音识别失败:', error)
    ElMessage.error(error.message || '语音识别失败，请重试')
  } finally {
    isTranscribing.value = false
  }
}
</script>

<style lang="scss" scoped>
.voice-recorder {
  position: relative;
  display: inline-block;
}

.microphone-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}

.device-selector {
  width: 200px;
}

.recording-info {
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  background: #f56c6c;
  color: white;
  border-radius: 20px;
  font-size: 14px;
  white-space: nowrap;

  .volume-indicator {
    font-size: 12px;
    opacity: 0.9;
  }
}

.volume-bar-container {
  position: absolute;
  top: -45px;
  left: 50%;
  transform: translateX(-50%);
  width: 200px;
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  overflow: hidden;
}

.volume-bar {
  height: 100%;
  background: linear-gradient(90deg, #67c23a 0%, #e6a23c 70%, #f56c6c 100%);
  transition: width 0.1s ease;
}

.low-volume-warning {
  position: absolute;
  top: -70px;
  left: 50%;
  transform: translateX(-50%);
  padding: 6px 12px;
  background: #fef0f0;
  border: 1px solid #fbc4c4;
  border-radius: 4px;
  color: #f56c6c;
  font-size: 12px;
  white-space: nowrap;
  animation: shake 0.5s ease-in-out infinite;
}

@keyframes shake {
  0%, 100% { transform: translateX(-50%) translateX(0); }
  25% { transform: translateX(-50%) translateX(-2px); }
  75% { transform: translateX(-50%) translateX(2px); }
}

.recording-dot {
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
  }
}

.preview-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.recording-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #e7f3ff;
  border-left: 4px solid #409eff;
  border-radius: 4px;
  color: #606266;
  font-size: 14px;

  .el-icon {
    color: #409eff;
    font-size: 18px;
  }
}

.recording-info-detail {
  display: flex;
  justify-content: space-around;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
  color: #909399;
  font-size: 13px;
}

.audio-player {
  width: 100%;
  margin: 10px 0;
}

.preview-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}
</style>
