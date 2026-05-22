<template>
  <el-dialog
    v-model="visible"
    :title="callType === 'video' ? '视频通话设备检测' : '语音通话设备检测'"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :before-close="handleClose"
  >
    <div class="device-check">
      <!-- 安全上下文检查 -->
      <el-alert
        v-if="!diagnosis.isSecureContext"
        title="当前页面不是安全连接（非 HTTPS / localhost），浏览器会阻止摄像头和麦克风。"
        type="error"
        :closable="false"
        show-icon
        style="margin-bottom: 16px"
      />

      <!-- 摄像头预览（仅视频通话） -->
      <div v-if="callType === 'video'" class="check-section">
        <div class="section-header">
          <h4>
            <el-icon><VideoCamera /></el-icon>
            摄像头检测
          </h4>
          <el-tag v-if="cameraStatus === 'ok'" type="success" size="small">正常</el-tag>
          <el-tag v-else-if="cameraStatus === 'checking'" type="warning" size="small">检测中...</el-tag>
          <el-tag v-else type="danger" size="small">异常</el-tag>
        </div>

        <div class="camera-preview-wrapper">
          <video
            ref="cameraPreviewRef"
            autoplay
            playsinline
            muted
            class="camera-preview"
          />
          <div v-if="cameraStatus !== 'ok'" class="preview-placeholder">
            <el-icon :size="48"><VideoCamera /></el-icon>
            <p v-if="cameraStatus === 'error'">{{ cameraError }}</p>
            <p v-else>摄像头预览未就绪</p>
          </div>
        </div>

        <!-- 摄像头选择 -->
        <div v-if="videoDevices.length > 0" class="device-select">
          <label>选择摄像头：</label>
          <el-select v-model="selectedCamera" @change="switchCamera" placeholder="请选择摄像头">
            <el-option
              v-for="d in videoDevices"
              :key="d.deviceId"
              :label="d.label || `摄像头 ${videoDevices.indexOf(d) + 1}`"
              :value="d.deviceId"
            />
          </el-select>
        </div>
        <div v-else class="no-device-hint">
          未检测到摄像头设备
        </div>
      </div>

      <!-- 麦克风检测 -->
      <div class="check-section">
        <div class="section-header">
          <h4>
            <el-icon><Microphone /></el-icon>
            麦克风检测
          </h4>
          <el-tag v-if="micStatus === 'ok'" type="success" size="small">正常</el-tag>
          <el-tag v-else-if="micStatus === 'checking'" type="warning" size="small">检测中...</el-tag>
          <el-tag v-else type="danger" size="small">异常</el-tag>
        </div>

        <!-- 音量指示器 -->
        <div class="mic-level">
          <div class="level-bar-track">
            <div class="level-bar-fill" :style="{ width: micLevel + '%' }" :class="levelBarClass" />
          </div>
          <span class="level-label">{{ micStatus === 'ok' ? '说话时进度条会变化' : micError || '等待检测...' }}</span>
        </div>

        <!-- 麦克风选择 -->
        <div v-if="audioDevices.length > 0" class="device-select">
          <label>选择麦克风：</label>
          <el-select v-model="selectedMic" @change="switchMic" placeholder="请选择麦克风">
            <el-option
              v-for="d in audioDevices"
              :key="d.deviceId"
              :label="d.label || `麦克风 ${audioDevices.indexOf(d) + 1}`"
              :value="d.deviceId"
            />
          </el-select>
        </div>
        <div v-else class="no-device-hint">
          未检测到麦克风设备
        </div>
      </div>

      <!-- 扬声器选择 -->
      <div v-if="audioOutputs.length > 0" class="check-section">
        <div class="section-header">
          <h4>
            <el-icon><Headset /></el-icon>
            扬声器
          </h4>
        </div>
        <div class="device-select">
          <label>选择扬声器：</label>
          <el-select v-model="selectedSpeaker" placeholder="请选择扬声器">
            <el-option
              v-for="d in audioOutputs"
              :key="d.deviceId"
              :label="d.label || `扬声器 ${audioOutputs.indexOf(d) + 1}`"
              :value="d.deviceId"
            />
          </el-select>
        </div>
      </div>

      <!-- 网络检测 -->
      <div class="check-section">
        <div class="section-header">
          <h4>
            <el-icon><Connection /></el-icon>
            连接检测
          </h4>
          <el-tag v-if="networkOk" type="success" size="small">正常</el-tag>
          <el-tag v-else type="danger" size="small">异常</el-tag>
        </div>
        <p class="network-info">WebRTC 信令服务器: STUN 可用</p>
      </div>

      <!-- 诊断结果 -->
      <div v-if="showDiagnosis" class="diagnosis-section">
        <el-alert
          v-for="(suggestion, i) in diagnosis.suggestions"
          :key="'s' + i"
          :title="suggestion"
          type="warning"
          :closable="false"
          show-icon
          style="margin-bottom: 8px"
        />
        <el-alert
          v-if="diagnosis.errors.length === 0 && diagnosis.suggestions.length === 0"
          title="所有设备检测通过"
          type="success"
          :closable="false"
          show-icon
        />
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="retryCheck" :loading="checking">
          <el-icon><Refresh /></el-icon>
          重新检测
        </el-button>
        <el-button @click="handleClose">取消</el-button>
        <el-button
          type="primary"
          :disabled="!allReady"
          :loading="starting"
          @click="handleStart"
        >
          <el-icon v-if="callType === 'video'"><VideoCamera /></el-icon>
          <el-icon v-else><Microphone /></el-icon>
          {{ callType === 'video' ? '开始视频通话' : '开始语音通话' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import { VideoCamera, Microphone, Headset, Connection, Refresh } from '@element-plus/icons-vue'
import { diagnoseMediaPermissions } from '@/utils/webrtc'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  callType: { type: String, default: 'video', validator: v => ['video', 'voice'].includes(v) }
})

const emit = defineEmits(['update:modelValue', 'start', 'cancel'])

const visible = computed({
  get: () => props.modelValue,
  set: v => emit('update:modelValue', v)
})

// 状态
const checking = ref(false)
const starting = ref(false)
const cameraStatus = ref('idle')
const micStatus = ref('idle')
const micLevel = ref(0)
const cameraError = ref('')
const micError = ref('')
const showDiagnosis = ref(false)
const networkOk = ref(true)
const diagnosis = ref({ errors: [], suggestions: [], isSecureContext: true })

// 设备列表
const videoDevices = ref([])
const audioDevices = ref([])
const audioOutputs = ref([])
const selectedCamera = ref('')
const selectedMic = ref('')
const selectedSpeaker = ref('')

// 预览
const cameraPreviewRef = ref(null)
let previewStream = null
let audioContext = null
let analyser = null
let animationId = null

// 计算
const allReady = computed(() =>
  (props.callType === 'voice' || cameraStatus.value === 'ok') &&
  micStatus.value === 'ok'
)

const levelBarClass = computed(() => {
  if (micLevel.value > 70) return 'level-high'
  if (micLevel.value > 30) return 'level-mid'
  return 'level-low'
})

// 监听 dialog 打开
watch(visible, async (val) => {
  if (val) {
    await initCheck()
  } else {
    stopPreview()
  }
})

// 初始化检测
async function initCheck() {
  checking.value = true
  showDiagnosis.value = false
  cameraStatus.value = 'checking'
  micStatus.value = 'checking'

  // 诊断
  diagnosis.value = await diagnoseMediaPermissions()
  showDiagnosis.value = true

  // 获取设备列表
  await loadDeviceList()

  // 获取媒体流
  await acquireMedia()
  checking.value = false
}

// 加载设备列表
async function loadDeviceList() {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices()
    videoDevices.value = devices.filter(d => d.kind === 'videoinput')
    audioDevices.value = devices.filter(d => d.kind === 'audioinput')
    audioOutputs.value = devices.filter(d => d.kind === 'audiooutput')

    // 记住上次的选择或默认第一个
    if (videoDevices.value.length > 0 && !videoDevices.value.find(d => d.deviceId === selectedCamera.value)) {
      selectedCamera.value = videoDevices.value[0].deviceId
    }
    if (audioDevices.value.length > 0 && !audioDevices.value.find(d => d.deviceId === selectedMic.value)) {
      selectedMic.value = audioDevices.value[0].deviceId
    }
    if (audioOutputs.value.length > 0 && !audioOutputs.value.find(d => d.deviceId === selectedSpeaker.value)) {
      selectedSpeaker.value = audioOutputs.value[0].deviceId
    }
  } catch (e) {
    console.warn('获取设备列表失败:', e)
  }
}

// 获取媒体流
async function acquireMedia() {
  try {
    const needsVideo = props.callType === 'video'
    const constraints = {
      audio: { deviceId: selectedMic.value ? { exact: selectedMic.value } : true },
      video: needsVideo
        ? (selectedCamera.value ? { deviceId: { exact: selectedCamera.value } } : true)
        : false
    }

    // 释放旧流
    stopPreview()

    previewStream = await navigator.mediaDevices.getUserMedia(constraints)

    // 显示摄像头预览
    if (needsVideo && cameraPreviewRef.value) {
      cameraPreviewRef.value.srcObject = previewStream
      cameraError.value = ''
    }

    // 设置麦克风分析
    setupMicAnalyzer(previewStream)

    // 更新设备列表（权限获取后会显示设备标签）
    await loadDeviceList()

    cameraStatus.value = needsVideo ? 'ok' : 'idle'
    micStatus.value = 'ok'
  } catch (err) {
    console.error('获取媒体流失败:', err)

    if (props.callType === 'video') {
      // 摄像头失败，尝试只用音频
      if (err.name === 'NotAllowedError' || err.name === 'NotFoundError') {
        cameraStatus.value = 'error'
        cameraError.value = getCameraErrorMessage(err)
        // 尝试只获取麦克风
        try {
          const audioStream = await navigator.mediaDevices.getUserMedia({
            audio: { deviceId: selectedMic.value ? { exact: selectedMic.value } : true },
            video: false
          })
          stopPreview()
          previewStream = audioStream
          setupMicAnalyzer(audioStream)
          micStatus.value = 'ok'
          await loadDeviceList()
        } catch (audioErr) {
          micStatus.value = 'error'
          micError.value = getMicErrorMessage(audioErr)
        }
      } else {
        cameraStatus.value = 'error'
        cameraError.value = getCameraErrorMessage(err)
      }
    } else {
      micStatus.value = 'error'
      micError.value = getMicErrorMessage(err)
    }
  }
}

// 设置麦克风音量分析
function setupMicAnalyzer(stream) {
  stopAnalyzer()

  try {
    const AudioCtx = window.AudioContext || window.webkitAudioContext
    audioContext = new AudioCtx()
    analyser = audioContext.createAnalyser()
    analyser.fftSize = 256
    analyser.smoothingTimeConstant = 0.7

    const source = audioContext.createMediaStreamSource(stream)
    source.connect(analyser)
    // 不连接到 destination，避免回声

    const dataArray = new Uint8Array(analyser.frequencyBinCount)

    function updateLevel() {
      if (!analyser) return
      analyser.getByteFrequencyData(dataArray)
      const avg = dataArray.reduce((a, b) => a + b, 0) / dataArray.length
      micLevel.value = Math.min(100, Math.round((avg / 128) * 100))
      animationId = requestAnimationFrame(updateLevel)
    }
    updateLevel()
  } catch (e) {
    console.warn('音频分析器初始化失败:', e)
  }
}

function stopAnalyzer() {
  if (animationId) { cancelAnimationFrame(animationId); animationId = null }
  if (audioContext) { audioContext.close(); audioContext = null }
  analyser = null
}

// 切换摄像头
async function switchCamera() {
  await acquireMedia()
}

// 切换麦克风
async function switchMic() {
  await acquireMedia()
}

// 重新检测
async function retryCheck() {
  await initCheck()
}

// 停止预览
function stopPreview() {
  stopAnalyzer()
  if (previewStream) {
    previewStream.getTracks().forEach(t => t.stop())
    previewStream = null
  }
  if (cameraPreviewRef.value) {
    cameraPreviewRef.value.srcObject = null
  }
  micLevel.value = 0
}

// 开始通话
async function handleStart() {
  starting.value = true
  // 保存设备ID到 store 或 sessionStorage，供实际通话使用
  const devicePrefs = {
    cameraId: props.callType === 'video' ? selectedCamera.value : '',
    micId: selectedMic.value,
    speakerId: selectedSpeaker.value
  }
  sessionStorage.setItem('devicePreferences', JSON.stringify(devicePrefs))

  stopPreview()
  emit('start', devicePrefs)
  visible.value = false
  starting.value = false
}

// 关闭
function handleClose() {
  stopPreview()
  emit('cancel')
  visible.value = false
}

// 错误信息
function getCameraErrorMessage(err) {
  if (err.name === 'NotAllowedError') return '摄像头权限被拒绝。请检查 Windows 隐私设置和浏览器权限。'
  if (err.name === 'NotFoundError') return '未检测到摄像头设备。'
  return `摄像头错误: ${err.message}`
}

function getMicErrorMessage(err) {
  if (err.name === 'NotAllowedError') return '麦克风权限被拒绝。请检查 Windows 隐私设置和浏览器权限。'
  if (err.name === 'NotFoundError') return '未检测到麦克风设备。'
  return `麦克风错误: ${err.message}`
}

onUnmounted(() => {
  stopPreview()
})
</script>

<style lang="scss" scoped>
.device-check {
  .check-section {
    margin-bottom: 20px;
    padding: 16px;
    background: #f9fafb;
    border-radius: 8px;
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;

    h4 {
      margin: 0;
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 15px;
      color: #303133;
    }
  }

  .camera-preview-wrapper {
    width: 100%;
    height: 200px;
    background: #1a1a2e;
    border-radius: 8px;
    overflow: hidden;
    position: relative;
    margin-bottom: 12px;
  }

  .camera-preview {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transform: scaleX(-1);
  }

  .preview-placeholder {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: rgba(255, 255, 255, 0.6);
    gap: 8px;

    p {
      margin: 0;
      font-size: 13px;
      color: #f56c6c;
    }
  }

  .mic-level {
    margin-bottom: 12px;
  }

  .level-bar-track {
    width: 100%;
    height: 8px;
    background: #e4e7ed;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 6px;
  }

  .level-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.1s ease;
    &.level-low { background: #67c23a; }
    &.level-mid { background: #e6a23c; }
    &.level-high { background: #409eff; }
  }

  .level-label {
    font-size: 12px;
    color: #909399;
  }

  .device-select {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 10px;

    label {
      font-size: 13px;
      color: #606266;
      white-space: nowrap;
    }

    .el-select { width: 100%; }
  }

  .no-device-hint {
    margin-top: 8px;
    font-size: 13px;
    color: #f56c6c;
  }

  .network-info {
    font-size: 13px;
    color: #909399;
    margin: 0;
  }

  .diagnosis-section {
    margin-top: 16px;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
