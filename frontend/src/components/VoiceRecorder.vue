<template>
  <div class="voice-recorder">
    <div class="microphone-wrapper">
      <el-button
        :icon="Microphone"
        :type="isRecording ? 'danger' : 'default'"
        :disabled="isProcessing"
        :loading="isProcessing"
        @click="toggleRecording"
        circle
        size="large"
      />
    </div>

    <!-- 录音时长 -->
    <div v-if="isRecording" class="recording-info">
      <span class="recording-dot"></span>
      <span>{{ formattedDuration }}</span>
    </div>

    <!-- 音量条 -->
    <div v-if="isRecording" class="volume-bar-container">
      <div class="volume-bar" :style="{ width: `${volumeLevel * 100}%` }"></div>
    </div>

    <!-- 音量过低警告 -->
    <div v-if="isRecording && lowVolumeWarning" class="low-volume-warning">
      ⚠️ 检测不到声音，请靠近麦克风说话
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Microphone } from '@element-plus/icons-vue'
import { getToken } from '@/utils/storage'

const props = defineProps({
  maxDuration: { type: Number, default: 60 }
})

const emit = defineEmits(['transcription-result'])

const isRecording = ref(false)
const isProcessing = ref(false)
const recordingDuration = ref(0)
const volumeLevel = ref(0)
const lowVolumeWarning = ref(false)

let mediaRecorder = null
let audioChunks = []
let recordingTimer = null
let startTime = null
let selectedMimeType = 'audio/webm'
let audioContext = null
let analyser = null
let microphone = null
let animationFrame = null

const formattedDuration = computed(() => {
  const s = Math.floor(recordingDuration.value / 1000)
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
})

const startRecording = async () => {
  try {
    const audioConstraints = {
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true,
      sampleRate: { ideal: 16000 },
      channelCount: { ideal: 1 }
    }

    const stream = await navigator.mediaDevices.getUserMedia({ audio: audioConstraints })
    const track = stream.getAudioTracks()[0]
    if (!track) throw new Error('未找到音频轨道，请检查麦克风设备')
    if (track.muted) ElMessage.warning('麦克风已被系统静音，请在系统设置中启用')

    audioContext = new (window.AudioContext || window.webkitAudioContext)()
    if (audioContext.state === 'suspended') await audioContext.resume()

    analyser = audioContext.createAnalyser()
    analyser.fftSize = 1024
    analyser.smoothingTimeConstant = 0.3
    microphone = audioContext.createMediaStreamSource(stream)
    microphone.connect(analyser)

    const timeData = new Uint8Array(analyser.frequencyBinCount)
    let lowVolumeCount = 0
    const checkVolume = () => {
      analyser.getByteTimeDomainData(timeData)
      let sumSq = 0
      for (let i = 0; i < timeData.length; i++) {
        const n = (timeData[i] - 128) / 128
        sumSq += n * n
      }
      volumeLevel.value = Math.min(Math.sqrt(sumSq / timeData.length) * 5, 1)
      if (volumeLevel.value < 0.01) {
        if (++lowVolumeCount > 50) lowVolumeWarning.value = true
      } else {
        lowVolumeCount = 0
        lowVolumeWarning.value = false
      }
      animationFrame = requestAnimationFrame(checkVolume)
    }
    checkVolume()

    const types = ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus', 'audio/mp4']
    let options = { mimeType: 'audio/webm' }
    for (const type of types) {
      if (MediaRecorder.isTypeSupported(type)) {
        options = { mimeType: type, audioBitsPerSecond: 128000 }
        selectedMimeType = type
        break
      }
    }

    mediaRecorder = new MediaRecorder(stream, options)
    audioChunks = []

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.push(e.data)
    }

    mediaRecorder.onstop = () => {
      if (animationFrame) { cancelAnimationFrame(animationFrame); animationFrame = null }
      volumeLevel.value = 0
      stream.getTracks().forEach(t => t.stop())
      if (audioContext) { audioContext.close(); audioContext = null }
      const blob = new Blob(audioChunks, { type: selectedMimeType })
      transcribeAudio(blob, recordingDuration.value)
    }

    track.onmute = () => ElMessage.warning('麦克风被系统静音，录音可能无声')
    track.onunmute = () => ElMessage.success('麦克风已恢复')

    mediaRecorder.start(250)
    startTime = Date.now()
    isRecording.value = true

    recordingTimer = setInterval(() => {
      recordingDuration.value = Date.now() - startTime
      if (recordingDuration.value >= props.maxDuration * 1000) {
        stopRecording()
        ElMessage.warning(`已达到最大录音时长 ${props.maxDuration} 秒`)
      }
    }, 100)

  } catch (error) {
    ElMessage.error(`无法访问麦克风: ${error.message}`)
  }
}

const stopRecording = () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
    isRecording.value = false
    clearInterval(recordingTimer)
    lowVolumeWarning.value = false
    isProcessing.value = true
  }
}

const toggleRecording = () => {
  isRecording.value ? stopRecording() : startRecording()
}

const getFileExtension = (mimeType) => {
  const map = {
    'audio/webm': 'webm', 'audio/webm;codecs=opus': 'webm',
    'audio/ogg': 'ogg', 'audio/ogg;codecs=opus': 'ogg',
    'audio/mp4': 'm4a', 'audio/mp3': 'mp3'
  }
  return map[mimeType] || 'webm'
}

const transcribeAudio = async (blob, duration) => {
  if (duration < 1000) {
    ElMessage.warning('录音时间太短（至少 1 秒）')
    isProcessing.value = false
    recordingDuration.value = 0
    return
  }
  if (blob.size < 1024) {
    ElMessage.warning('录音数据太小，请重新录制')
    isProcessing.value = false
    recordingDuration.value = 0
    return
  }

  try {
    const token = getToken()
    if (!token) throw new Error('未登录')

    const formData = new FormData()
    formData.append('audio_file', blob, `recording.${getFileExtension(selectedMimeType)}`)
    formData.append('language', 'zh-CN')

    const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
    const response = await fetch(`${base}/chat/voice-to-text`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData
    })

    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || '识别失败')
    }

    const result = await response.json()
    if (result.code === 200 && result.data?.text) {
      emit('transcription-result', result.data.text)
    } else {
      throw new Error('识别结果为空')
    }
  } catch (error) {
    ElMessage.error(error.message || '语音识别失败，请重试')
  } finally {
    isProcessing.value = false
    recordingDuration.value = 0
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
}

.recording-dot {
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}
</style>
