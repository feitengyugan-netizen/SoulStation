<template>
  <div class="voice-recorder">
    <!-- 录音按钮 -->
    <el-button
      :icon="microphoneIcon"
      :type="isRecording ? 'danger' : 'default'"
      :disabled="isProcessing"
      @click="toggleRecording"
      circle
      size="large"
    />

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

// Props
const props = defineProps({
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
const volumeLevel = ref(0)

// MediaRecorder 实例
let mediaRecorder = null
let audioChunks = []
let recordingTimer = null
let startTime = null
let selectedMimeType = 'audio/webm'
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

// 开始录音
const startRecording = async () => {
  try {
    console.log('🎤 开始请求麦克风权限...')

    // 请求麦克风权限
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
        sampleRate: 48000,
        channelCount: 1
      }
    })

    console.log('✅ 麦克风权限获取成功', {
      tracks: stream.getAudioTracks().length,
      enabled: stream.getAudioTracks()[0]?.enabled,
      muted: stream.getAudioTracks()[0]?.muted,
      label: stream.getAudioTracks()[0]?.label
    })

    // 创建 AudioContext 用于音量分析
    audioContext = new (window.AudioContext || window.webkitAudioContext)()
    console.log('🎵 AudioContext 创建成功', {
      state: audioContext.state,
      sampleRate: audioContext.sampleRate
    })

    if (audioContext.state === 'suspended') {
      await audioContext.resume()
      console.log('🎵 AudioContext 已恢复')
    }

    analyser = audioContext.createAnalyser()
    analyser.fftSize = 256
    microphone = audioContext.createMediaStreamSource(stream)
    microphone.connect(analyser)
    console.log('🎤 音频分析器已连接')

    // 开始监测音量 - 添加详细日志
    const dataArray = new Uint8Array(analyser.frequencyBinCount)
    let checkCount = 0

    const checkVolume = () => {
      analyser.getByteFrequencyData(dataArray)
      const average = dataArray.reduce((a, b) => a + b) / dataArray.length
      const max = Math.max(...dataArray)
      volumeLevel.value = Math.min(average / 50, 1)

      // 每秒输出一次调试信息
      checkCount++
      if (checkCount % 60 === 0) {
        console.log('🔊 音量检测:', {
          average: average.toFixed(2),
          max: max,
          volumeLevel: volumeLevel.value.toFixed(2),
          hasSound: average > 0
        })
      }

      animationFrame = requestAnimationFrame(checkVolume)
    }
    checkVolume()

    // 创建 MediaRecorder - 选择最佳格式
    let options = { mimeType: 'audio/webm' }
    const types = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/ogg;codecs=opus'
    ]

    for (const type of types) {
      if (MediaRecorder.isTypeSupported(type)) {
        options = {
          mimeType: type,
          audioBitsPerSecond: 128000
        }
        selectedMimeType = type
        break
      }
    }

    mediaRecorder = new MediaRecorder(stream, options)
    console.log('📼 MediaRecorder 创建成功', {
      mimeType: mediaRecorder.mimeType,
      state: mediaRecorder.state
    })

    audioChunks = []

    // 收集音频数据
    mediaRecorder.ondataavailable = (event) => {
      console.log('📦 收集音频数据:', {
        size: event.data.size,
        type: event.data.type,
        totalChunks: audioChunks.length + 1
      })
      if (event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }

    // 录音结束
    mediaRecorder.onstop = () => {
      const totalSize = audioChunks.reduce((sum, chunk) => sum + chunk.size, 0)
      console.log('⏹️ 录音停止', {
        chunks: audioChunks.length,
        totalSize: totalSize,
        duration: recordingDuration.value
      })

      const blob = new Blob(audioChunks, { type: selectedMimeType })
      console.log('📄 音频 Blob 创建成功', {
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
    mediaRecorder.start(100)
    startTime = Date.now()
    isRecording.value = true

    // 更新录音时长
    recordingTimer = setInterval(() => {
      const elapsed = Date.now() - startTime
      recordingDuration.value = elapsed

      if (elapsed >= props.maxDuration * 1000) {
        stopRecording()
        ElMessage.warning(`已达到最大录音时长 ${props.maxDuration} 秒`)
      }
    }, 100)

    ElMessage.success('开始录音...')

    // 延迟测试麦克风是否工作
    setTimeout(() => {
      if (volumeLevel.value > 0) {
        console.log('✅ 麦克风工作正常，音量级别:', volumeLevel.value.toFixed(2))
      } else {
        console.warn('⚠️ 检测不到声音！请检查:')
        console.warn('  1. 系统音量设置')
        console.warn('  2. 麦克风设备是否被其他应用占用')
        console.warn('  3. 浏览器是否有麦克风权限')
        ElMessage.warning('检测不到麦克风声音，请检查设备设置')
      }
    }, 2000)

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
  const minDuration = 1000
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

    console.log(`上传音频: format=${selectedMimeType}, size=${audioBlob.value.size} bytes, duration=${recordingDuration.value}ms`)

    // 获取 token
    const token = localStorage.getItem('token')
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
