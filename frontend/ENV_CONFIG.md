# 环境变量配置说明

## 开发环境 (.env.development)

```env
# API服务器地址
VITE_API_BASE_URL=http://localhost:8000/api

# WebSocket服务器地址
VITE_WS_BASE_URL=ws://localhost:8000
```

## 生产环境 (.env.production)

生产环境需要根据实际部署地址修改：

```env
# 示例：如果部署在 https://example.com
VITE_API_BASE_URL=https://example.com/api
VITE_WS_BASE_URL=wss://example.com
```

## 配置说明

1. **VITE_API_BASE_URL**: 后端API服务器地址，用于HTTP请求
2. **VITE_WS_BASE_URL**: WebSocket服务器地址，用于视频通话信令

## 注意事项

- 开发环境WebSocket使用 `ws://` 协议
- 生产环境WebSocket使用 `wss://` 协议（安全的WebSocket）
- 确保WebSocket地址与API服务器地址一致
- 如果使用代理，需要相应配置代理设置

## 修改环境变量后

修改环境变量后需要重启开发服务器：

```bash
# 停止当前服务器 (Ctrl+C)
# 然后重新启动
npm run dev
```
