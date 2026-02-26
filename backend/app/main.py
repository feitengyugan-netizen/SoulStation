"""
SoulStation - 心理咨询服务平台
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="心理咨询服务平台 API"
)

# CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由注册
@app.get("/")
async def root():
    return {
        "message": "Welcome to SoulStation API",
        "version": settings.APP_VERSION
    }

# 认证路由
from app.api.auth import router as auth_router
app.include_router(auth_router, prefix="/api")

# 开发人员 A 的路由
# from app.api.member_a.chat import router as chat_router
# from app.api.member_a.test import router as test_router
# from app.api.member_a.profile import router as profile_router

# 开发人员 B 的路由
# from app.api.member_b.consultation import router as consultation_router
# from app.api.member_b.dialogue import router as dialogue_router
# from app.api.member_b.admin import router as admin_router
# from app.api.member_b.public import router as public_router

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
