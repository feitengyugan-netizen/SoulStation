"""
后台管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db
from app.core.security import create_access_token
from app.models.admin import Admin
from app.schemas.admin import (
    AdminResponse, AdminTokenResponse, DashboardStats, ChartResponse,
    CounselorReviewResponse, ReviewCounselorRequest,
    ArticleSaveRequest, AdminUserResponse, BanUserRequest,
    AdminOrderResponse
)
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["后台管理"])
security = HTTPBearer()
logger = logging.getLogger(__name__)


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Admin:
    """获取当前管理员"""
    from app.core.security import decode_access_token

    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload or payload.get("type") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的管理员令牌"
        )

    admin_id = payload.get("sub")
    if not admin_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的管理员令牌"
        )

    admin = db.query(Admin).filter(
        Admin.id == int(admin_id),
        Admin.deleted_at.is_(None)
    ).first()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="管理员不存在"
        )

    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理员账号已被禁用"
        )

    return admin


# ==================== 管理员认证 ====================

@router.post("/login", summary="管理员登录")
async def admin_login(
    username: str = Query(..., description="用户名"),
    password: str = Query(..., description="密码"),
    db: Session = Depends(get_db)
):
    """
    管理员登录

    返回访问令牌和管理员信息
    """
    try:
        admin = AdminService.authenticate_admin(db, username, password)

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )

        # 生成token（type为admin）
        token_data = {
            "sub": str(admin.id),
            "type": "admin",
            "role": admin.role
        }
        access_token = create_access_token(token_data)

        admin_data = AdminResponse.model_validate(admin)

        return {
            "code": 200,
            "message": "登录成功",
            "data": AdminTokenResponse(
                access_token=access_token,
                admin=admin_data
            )
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"管理员登录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败"
        )


# ==================== 仪表盘接口 ====================

@router.get("/dashboard/stats", summary="获取仪表盘统计数据")
async def get_dashboard_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取仪表盘统计数据

    包括：
    - 用户总数、今日新增
    - 咨询师总数、待审核数
    - 订单总数、今日新增
    - 文章总数
    - 总收入
    """
    try:
        stats = AdminService.get_dashboard_stats(db)
        return {
            "code": 200,
            "message": "获取成功",
            "data": stats
        }
    except Exception as e:
        logger.error(f"获取统计数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计数据失败: {str(e)}"
        )


@router.get("/dashboard/chart", summary="获取图表数据")
async def get_chart_data(
    type: str = Query(..., description="图表类型：user/trend/order/revenue"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取图表数据

    支持的图表类型：
    - **user**: 用户增长趋势（最近30天）
    - **trend**: 综合活动趋势（最近7天）
    - **order**: 订单趋势（最近30天）
    - **revenue**: 收入趋势（最近30天）
    """
    try:
        chart_data = AdminService.get_chart_data(db, type)
        return {
            "code": 200,
            "message": "获取成功",
            "data": chart_data
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取图表数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取图表数据失败: {str(e)}"
        )


# ==================== 咨询师审核接口 ====================

@router.get("/counselors/pending", summary="获取待审核咨询师列表")
async def get_pending_counselors(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取待审核的咨询师列表

    返回未认证的咨询师，按申请时间倒序排列
    """
    try:
        result = AdminService.get_pending_counselors(db, page, page_size)
        return {
            "code": 200,
            "message": "获取成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"获取待审核咨询师失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取待审核咨询师失败: {str(e)}"
        )


@router.post("/counselor/{counselor_id}/review", summary="审核咨询师")
async def review_counselor(
    counselor_id: int,
    review_data: ReviewCounselorRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    审核咨询师申请

    - **action**: approve（通过）/ reject（拒绝）
    - **reason**: 拒绝理由（拒绝时建议提供）

    通过后咨询师状态变为active，拒绝后标记为删除
    """
    try:
        AdminService.review_counselor(db, counselor_id, review_data)
        return {
            "code": 200,
            "message": "审核完成",
            "data": {
                "counselor_id": counselor_id,
                "action": review_data.action
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"审核咨询师失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"审核咨询师失败: {str(e)}"
        )


# ==================== 知识管理接口 ====================

@router.get("/knowledge/list", summary="获取知识文章列表")
async def get_knowledge_articles(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    category: Optional[str] = Query(None, description="分类"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取知识文章列表（后台管理）

    支持搜索和分类筛选
    包含所有状态的文章（draft/published/archived）
    """
    try:
        from app.services.knowledge_service import KnowledgeService
        from app.schemas.knowledge import KnowledgeListQuery

        query = KnowledgeListQuery(
            keyword=keyword,
            category=category,
            sort="latest",
            page=page,
            page_size=page_size
        )

        # 修改服务以返回所有状态的文章
        result = KnowledgeService.get_knowledge_list(db, query, None)

        return {
            "code": 200,
            "message": "获取成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"获取知识文章列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取知识文章列表失败: {str(e)}"
        )


@router.post("/knowledge/save", summary="保存知识文章")
async def save_knowledge_article(
    article_data: ArticleSaveRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    创建或更新知识文章

    提供id时更新文章，不提供id时创建新文章
    支持保存草稿或直接发布
    """
    try:
        article_id = AdminService.save_article(db, article_data)
        return {
            "code": 200,
            "message": "保存成功",
            "data": {
                "id": article_id
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"保存文章失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"保存文章失败: {str(e)}"
        )


@router.delete("/knowledge/{article_id}", summary="删除知识文章")
async def delete_knowledge_article(
    article_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    删除知识文章

    软删除操作，数据不会真正从数据库中删除
    """
    try:
        AdminService.delete_article(db, article_id)
        return {
            "code": 200,
            "message": "删除成功",
            "data": {
                "article_id": article_id
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"删除文章失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除文章失败: {str(e)}"
        )


# ==================== 用户管理接口 ====================

@router.get("/users", summary="获取用户列表")
async def get_users(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取用户列表（后台管理）

    支持按邮箱、昵称、手机号搜索
    包含用户的统计信息（测试、对话、订单数）
    """
    try:
        result = AdminService.get_users(db, keyword, page, page_size)
        return {
            "code": 200,
            "message": "获取成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"获取用户列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户列表失败: {str(e)}"
        )


@router.post("/user/{user_id}/ban", summary="封禁/解封用户")
async def ban_user(
    user_id: int,
    ban_data: BanUserRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    封禁或解封用户

    - **banned**: true 封禁 / false 解封
    - **reason**: 封禁理由（可选）

    封禁后用户无法登录和使用系统
    """
    try:
        AdminService.ban_user(db, user_id, ban_data)
        action = "封禁" if ban_data.banned else "解封"
        return {
            "code": 200,
            "message": f"{action}成功",
            "data": {
                "user_id": user_id,
                "banned": ban_data.banned
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"封禁用户失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"封禁用户失败: {str(e)}"
        )


# ==================== 订单管理接口 ====================

@router.get("/orders", summary="获取订单列表")
async def get_orders(
    status_filter: Optional[str] = Query(None, description="订单状态"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取订单列表（后台管理）

    支持按状态筛选
    包含用户和咨询师信息
    """
    try:
        result = AdminService.get_orders(db, status_filter, page, page_size)
        return {
            "code": 200,
            "message": "获取成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"获取订单列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取订单列表失败: {str(e)}"
        )


@router.get("/orders/export", summary="导出订单数据")
async def export_orders(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    导出订单数据为CSV文件

    包含完整的订单信息
    可用Excel或其他工具打开
    """
    try:
        csv_data = AdminService.export_orders(db)

        # 返回CSV文件
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=orders_export.csv"
            }
        )
    except Exception as e:
        logger.error(f"导出订单数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出订单数据失败: {str(e)}"
        )
