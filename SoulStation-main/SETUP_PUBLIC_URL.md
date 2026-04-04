# 配置公网URL（解决语音识别问题）

## 问题原因
豆包语音识别API需要能够访问你上传的音频文件URL。如果URL是 `http://localhost:8000`，豆包的服务器无法访问。

## 解决方案：使用内网穿透

### 步骤1：安装 ngrok

1. 访问 https://ngrok.com/download 下载 Windows 版本
2. 解压到某个目录，例如 `C:\ngrok`
3. 将该目录添加到系统PATH（可选）

### 步骤2：启动 ngrok

打开命令行（CMD或PowerShell）：

```bash
cd C:\ngrok
ngrok http 8000
```

### 步骤3：获取公网地址

ngrok 会显示类似以下信息：

```
Forwarding: https://abc123.ngrok-free.app -> http://localhost:8000
```

**复制这个 https 地址**，例如：`https://abc123.ngrok-free.app`

### 步骤4：更新配置

编辑 `backend/.env` 文件：

```env
# 将 https://abc123.ngrok-free.app 替换为你实际的 ngrok 地址
PUBLIC_URL=https://abc123.ngrok-free.app
```

### 步骤5：重启服务

```bash
# 先停止当前的后端服务（Ctrl+C）
# 重新启动
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 步骤6：测试语音识别

1. 访问 http://localhost:5173/chat
2. 点击麦克风按钮
3. 开始录音并识别
4. 应该可以正常工作了！

---

## 其他内网穿透工具（备选）

如果 ngrok 速度慢或无法使用，可以尝试：

### 1. Cloudflare Tunnel（推荐，免费）
```bash
# 下载 cloudflared
# 访问：https://github.com/cloudflare/cloudflared/releases

# 启动
cloudflared tunnel --url http://localhost:8000
```

### 2. localhost.run（最简单，无需安装）
```bash
# 直接运行（Windows上需要Git Bash）
ssh -R 80:localhost:8000 localhost.run
```

### 3. Frp（需要有自己的服务器）
需要配置 frps 和 frpc，适合有服务器的用户。

---

## 生产环境方案

上线后应该使用对象存储服务：

### 1. 阿里云OSS
```python
import oss2

auth = oss2.Auth('your-access-key-id', 'your-access-key-secret')
bucket = oss2.Bucket(auth, 'https://oss-cn-hangzhou.aliyuncs.com', 'your-bucket-name')

# 上传文件
bucket.put_object('audio/recording.webm', audio_data)
url = bucket.sign_url('GET', 'audio/recording.webm', 3600)
```

### 2. 腾讯云COS
```python
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

config = CosConfig(Region='ap-guangzhou', SecretId='xxx', SecretKey='xxx')
client = CosS3Client(config)

# 上传文件
response = client.upload_file(
    Bucket='your-bucket',
    LocalFilePath='/tmp/audio.webm',
    Key='audio/recording.webm'
)
url = f"https://{bucket}.cos.ap-guangzhou.myqcloud.com/audio/recording.webm"
```

### 3. 火山引擎TOS（与豆包同厂商）
```python
import tos

# 创建客户端
client = tos.TosClient(
    ak='your-access-key',
    sk='your-secret-key',
    endpoint='tos-cn-beijing.volces.com',
    region='cn-beijing',
    bucket_name='your-bucket'
)

# 上传文件
client.put_object_from_file('audio/recording.webm', '/tmp/audio.webm')
url = f"https://{bucket}.tos-cn-beijing.volces.com/audio/recording.webm"
```

---

## 常见问题

### Q1: ngrok 启动失败？
A: 检查 8000 端口是否被占用，确保后端服务已停止。

### Q2: ngrok 地址每次都变？
A: 免费版确实会变。可以注册 ngrok 账号获得固定域名，或使用 Cloudflare Tunnel。

### Q3: 还是不行？
A:
1. 确认 ngrok 正在运行
2. 确认 .env 中的 PUBLIC_URL 正确
3. 重启后端服务
4. 查看后端日志确认使用了正确的 URL

---

## 总结

开发环境推荐使用：
- ✅ ngrok（最简单）
- ✅ Cloudflare Tunnel（速度快）
- ✅ localhost.run（无需安装）

生产环境必须使用：
- ✅ 对象存储（OSS/COS/TOS）
