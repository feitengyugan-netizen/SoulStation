# 语音转文字功能集成指南

## 📋 功能概述

本项目已集成豆包大模型录音文件识别服务，实现语音转文字功能。

### 实现方式
- **后端**：豆包录音文件识别API（异步任务模式）
- **前端**：Web Audio API 录音 + 文件上传

---

## 🔧 配置步骤

### 1. 获取豆包API密钥

1. 访问[火山引擎控制台](https://console.volcengine.com/)
2. 开通"语音技术-音频自训练"服务
3. 在控制台获取 `API Key`（`X-Api-Key`）
4. 确认服务已开通"豆包录音文件识别模型2.0"（资源ID: `volc.seedasr.auc`）

### 2. 配置后端环境变量

编辑 `backend/.env` 文件，添加：

```env
# 豆包语音识别配置
DOUBAO_API_KEY=your-doubao-api-key-here
```

**注意**：`.env` 文件不会被提交到Git，`.env.example` 中保留了配置模板。

### 3. 安装Python依赖

```bash
cd backend
pip install httpx
```

`httpx` 库已包含在 `requirements.txt` 中，如果之前未安装请执行：

```bash
pip install -r requirements.txt
```

---

## 🎯 使用说明

### 前端使用

1. **启动后端服务**
   ```bash
   cd backend
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **启动前端服务**
   ```bash
   cd frontend
   npm run dev
   ```

3. **使用语音识别**
   - 进入聊天页面 (`/chat`)
   - 点击输入框工具栏的麦克风按钮 🎤
   - 允许浏览器访问麦克风
   - 开始录音（最长60秒）
   - 停止录音后预览音频
   - 点击"识别文字"按钮
   - 识别结果自动填充到输入框

### API接口

**请求**

```
POST /api/chat/voice-to-text
Authorization: Bearer <your_token>
Content-Type: multipart/form-data

audio_file: <audio_file>
language: "zh-CN"  // 可选，默认中文
```

**响应**

```json
{
  "code": 200,
  "message": "识别成功",
  "data": {
    "text": "这是识别出的文字内容"
  }
}
```

---

## 📂 文件结构

### 后端文件
```
backend/
├── app/
│   ├── services/
│   │   └── speech_service.py       # 语音识别服务
│   └── api/
│       └── chat/
│           └── router.py            # 聊天路由（含语音接口）
└── uploads/
    └── audio/                       # 音频文件临时存储
```

### 前端文件
```
frontend/
└── src/
    ├── components/
    │   └── VoiceRecorder.vue       # 语音录制组件
    └── views/
        └── chat/
            └── ChatIndex.vue        # 聊天主界面（集成录音）
```

---

## 🔍 核心实现逻辑

### 后端流程

```python
# 1. 接收音频文件
audio_file: UploadFile

# 2. 保存到本地（或对象存储）
audio_url = save_audio_file(audio_file)

# 3. 提交识别任务
task_id = submit_task(audio_url, format, language)

# 4. 轮询查询结果（最长30秒）
result = poll_result(task_id)

# 5. 返回识别文字
return result
```

### 前端流程

```javascript
// 1. 用户点击麦克风按钮
toggleRecording()

// 2. 请求麦克风权限并开始录音
navigator.mediaDevices.getUserMedia({ audio: true })

// 3. 停止录音后预览
mediaRecorder.stop()
showPreviewDialog()

// 4. 用户确认后上传并识别
transcribeAudio() {
  const formData = new FormData()
  formData.append('audio_file', audioBlob)
  // 发送到后端 API
}

// 5. 识别结果填充到输入框
handleTranscriptionResult(text) {
  inputMessage.value += text
}
```

---

## ⚙️ 配置参数

### 后端配置（`speech_service.py`）

```python
# 资源ID（模型）
RESOURCE_ID = "volc.seedasr.auc"  # 豆包录音文件识别模型2.0

# 音频格式支持
ALLOWED_FORMATS = ["mp3", "wav", "m4a", "ogg", "webm"]

# 文件大小限制
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB

# 轮询超时
POLL_TIMEOUT = 30  # 秒
```

### 前端配置（`VoiceRecorder.vue`）

```javascript
// 最大录音时长
maxDuration: 60  // 秒

// 音频格式
mimeType: 'audio/webm'  // Chrome默认，可改为其他格式

// 轮询间隔
pollInterval: 1-5  // 秒（动态增长）
```

---

## 🌐 支持的语言

豆包语音识别支持以下语言：

| 语言代码 | 语言 |
|---------|------|
| `zh-CN` | 中文普通话（默认） |
| `en-US` | 英语 |
| `ja-JP` | 日语 |
| `yue-CN` | 粤语 |
| `ko-KR` | 韩语 |
| `de-DE` | 德语 |
| `fr-FR` | 法语 |
| `es-MX` | 西班牙语 |
| 等等... | 更多语言见[官方文档](https://www.volcengine.com/docs/6561/79843) |

---

## 🚀 生产环境优化建议

### 1. 使用对象存储

开发环境使用本地文件存储，生产环境建议使用：

- **阿里云OSS**
- **腾讯云COS**
- **火山引擎TOS**

修改 `speech_service.py` 中的 `_save_audio_file` 方法：

```python
async def _save_audio_file(self, audio_file: UploadFile) -> str:
    # 上传到OSS
    url = await upload_to_oss(audio_file)
    return url  # 返回公网可访问的URL
```

### 2. 添加缓存

对已识别的音频进行缓存（使用音频文件hash作为key）：

```python
# 使用 Redis 缓存识别结果
cache_key = f"speech:{audio_hash}"
cached_result = await redis.get(cache_key)
if cached_result:
    return cached_result
```

### 3. 添加限流

防止用户频繁调用API：

```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@router.post("/voice-to-text", dependencies=[
    Depends(RateLimiter(times=10, seconds=60))  # 每分钟最多10次
])
async def voice_to_text(...):
    ...
```

### 4. 错误处理增强

```python
# 添加更详细的错误日志
logger.error(f"语音识别失败: user_id={user_id}, error={str(e)}")

# 返回用户友好的错误提示
if error_code == "45000151":
    return "音频格式不正确，请上传mp3或wav格式"
```

---

## 🐛 常见问题

### Q1: 麦克风权限被拒绝？

**A**: 检查浏览器设置，允许网站访问麦克风：
- Chrome: 设置 → 隐私和安全 → 网站设置 → 麦克风
- Firefox: 偏好设置 → 隐私与安全 → 权限 → 麦克风

### Q2: 识别一直失败？

**A**: 检查以下几点：
1. `.env` 文件中 `DOUBAO_API_KEY` 是否正确配置
2. 后端服务是否正常启动
3. 网络是否正常（需要访问豆包API）
4. 查看后端日志：`backend/app.log`

### Q3: 音频文件上传失败？

**A**: 检查：
1. 文件大小是否超过25MB
2. 文件格式是否支持（mp3/wav/m4a/ogg/webm）
3. `uploads/audio` 目录是否有写入权限

### Q4: 识别结果不准确？

**A**:
1. 确保录音环境安静
2. 靠近麦克风说话
3. 语速适中，吐字清晰
4. 设置正确的语言参数（`language`）

### Q5: 轮询超时？

**A**:
- 默认最长等待30秒
- 如音频较长，可修改 `POLL_TIMEOUT` 参数
- 或使用回调模式（需要配置公网可访问的回调地址）

---

## 📞 技术支持

如有问题，请查看：
- [豆包语音识别官方文档](https://www.volcengine.com/docs/6561/79843)
- [项目Issue](https://github.com/your-repo/issues)

---

## 📝 更新日志

### 2026-04-01
- ✅ 集成豆包录音文件识别API
- ✅ 实现前端语音录制组件
- ✅ 添加音频预览和重录功能
- ✅ 支持多种音频格式
- ✅ 添加错误处理和用户提示

---

**祝使用愉快！** 🎉
