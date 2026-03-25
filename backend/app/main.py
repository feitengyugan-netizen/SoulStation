"""
SoulStation - 心理咨询服务平台
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
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

# 心理测试路由
from app.api.test import router as test_router
app.include_router(test_router, prefix="/api")

# 用户路由
from app.api.user import router as user_router
app.include_router(user_router, prefix="/api")

# 智能问答路由
from app.api.chat.router import router as chat_router
app.include_router(chat_router, prefix="/api")

# 咨询师预约路由
from app.api.counselor import router as counselor_router, router_appointment as appointment_router
app.include_router(counselor_router, prefix="/api")
app.include_router(appointment_router, prefix="/api")

# 咨询对话路由
from app.api.consultation import router as consultation_router
app.include_router(consultation_router, prefix="/api")

# 心理知识路由
from app.api.knowledge import router as knowledge_router
app.include_router(knowledge_router, prefix="/api")

# 后台管理路由
from app.api.admin import router as admin_router
app.include_router(admin_router, prefix="/api")

# 静态文件服务 - 用于访问上传的头像等文件
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 开发人员 A 的路由
# from app.api.member_a.chat import router as chat_router
# from app.api.member_a.profile import router as profile_router

# 开发人员 B 的路由
# from app.api.member_b.consultation import router as consultation_router
# from app.api.member_b.dialogue import router as dialogue_router
# from app.api.member_b.admin import router as admin_router
# from app.api.member_b.public import router as public_router

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
