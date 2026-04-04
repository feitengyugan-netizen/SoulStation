"""
心理知识 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db
from app.core.security import decode_access_token
from app.schemas.knowledge import (
    KnowledgeArticleResponse, KnowledgeListQuery,
    CommentResponse, CommentCreate
)
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge", tags=["心理知识"])
security = HTTPBearer()  # 需要认证的接口使用这个
logger = logging.getLogger(__name__)


async def get_optional_user_id(request) -> Optional[int]:
    """从请求中获取可选的用户ID（不需要认证也能访问）"""
    try:
        # 从请求头获取Authorization
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # 移除 "Bearer " 前缀
            from app.core.security import decode_access_token
            payload = decode_access_token(token)
            if payload and payload.get("sub"):
                return int(payload.get("sub"))
    except:
        pass
    return None


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(None)) -> Optional[int]:
    """从 token 中获取当前用户 ID（可选认证）"""
    if not credentials or not credentials.credentials:
        return None
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        if payload and payload.get("sub"):
            return int(payload.get("sub"))
        return None
    except:
        return None


def get_required_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """获取当前用户 ID（必须认证）"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌"
        )
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )
    return int(payload.get("sub"))


# ==================== 知识文章接口 ====================

@router.get("/list", summary="获取知识列表")
async def get_knowledge_list(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    category: Optional[str] = Query(None, description="分类筛选"),
    sort: Optional[str] = Query("latest", description="排序方式"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    authorization: Optional[str] = Header(None),  # 可选的Authorization头
    db: Session = Depends(get_db)
):
    # 手动解析token获取用户ID
    user_id = None
    if authorization and authorization.startswith("Bearer "):
        try:
            token = authorization[7:]
            payload = decode_access_token(token)
            if payload and payload.get("sub"):
                user_id = int(payload.get("sub"))
        except:
            pass
    """
    获取心理知识列表

    支持多维度筛选：
    - **keyword**: 搜索标题、摘要、内容、标签
    - **category**: 分类筛选（anxiety/depression/emotion/career/family等）
    - **sort**: 排序方式（latest最新/hot热门/popular推荐）

    返回分页列表数据，包含用户的点赞和收藏状态
    """
    try:
        query = KnowledgeListQuery(
            keyword=keyword,
            category=category,
            sort=sort,
            page=page,
            page_size=page_size
        )
        result = KnowledgeService.get_knowledge_list(db, query, user_id)
        return {
            "code": 200,
            "message": "获取成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"获取知识列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取知识列表失败: {str(e)}"
        )


@router.get("/{article_id}", summary="获取知识详情")
async def get_knowledge_detail(
    article_id: int,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    获取知识文章详情

    返回文章完整内容，包括：
    - 基本信息（标题、摘要、封面）
    - 文章内容（Markdown/HTML）
    - 分类和标签
    - 统计信息（浏览、点赞、收藏、评论）
    - 用户交互状态（是否已点赞、收藏）
    """
    # 手动解析token获取用户ID
    user_id = None
    if authorization and authorization.startswith("Bearer "):
        try:
            token = authorization[7:]
            payload = decode_access_token(token)
            if payload and payload.get("sub"):
                user_id = int(payload.get("sub"))
        except:
            pass
    try:
        article = KnowledgeService.get_knowledge_detail(db, article_id, user_id)
        return {
            "code": 200,
            "message": "获取成功",
            "data": article
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取知识详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取知识详情失败: {str(e)}"
        )


@router.get("/{article_id}/recommended", summary="获取推荐知识")
async def get_recommended_knowledge(
    article_id: int,
    limit: int = Query(5, ge=1, le=10, description="推荐数量"),
    db: Session = Depends(get_db)
):
    """
    获取推荐知识文章

    基于当前文章的分类和标签推荐相关内容
    优先推荐同分类的热门文章
    """
    try:
        articles = KnowledgeService.get_recommended_knowledge(db, article_id, limit)
        return {
            "code": 200,
            "message": "获取成功",
            "data": articles
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取推荐知识失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取推荐知识失败: {str(e)}"
        )


# ==================== 交互功能接口 ====================

@router.post("/{article_id}/favorite", summary="收藏知识")
async def favorite_knowledge(
    article_id: int,
    user_id: int = Depends(get_required_user_id),
    db: Session = Depends(get_db)
):
    """
    收藏知识文章

    如果已收藏则忽略，支持重复调用
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="请先登录"
            )

        KnowledgeService.toggle_favorite(db, article_id, user_id, "add")
        return {
            "code": 200,
            "message": "收藏成功",
            "data": {
                "article_id": article_id,
                "favorited": True
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"收藏失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"收藏失败: {str(e)}"
        )


@router.delete("/{article_id}/favorite", summary="取消收藏知识")
async def unfavorite_knowledge(
    article_id: int,
    user_id: int = Depends(get_required_user_id),
    db: Session = Depends(get_db)
):
    """
    取消收藏知识文章

    如果未收藏则忽略，支持重复调用
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="请先登录"
            )

        KnowledgeService.toggle_favorite(db, article_id, user_id, "remove")
        return {
            "code": 200,
            "message": "已取消收藏",
            "data": {
                "article_id": article_id,
                "favorited": False
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"取消收藏失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消收藏失败: {str(e)}"
        )


@router.post("/{article_id}/like", summary="点赞知识")
async def like_knowledge(
    article_id: int,
    user_id: int = Depends(get_required_user_id),
    db: Session = Depends(get_db)
):
    """
    点赞知识文章

    如果已点赞则忽略，支持重复调用
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="请先登录"
            )

        KnowledgeService.toggle_like(db, article_id, user_id, "add")
        return {
            "code": 200,
            "message": "点赞成功",
            "data": {
                "article_id": article_id,
                "liked": True
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"点赞失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"点赞失败: {str(e)}"
        )


@router.delete("/{article_id}/like", summary="取消点赞知识")
async def unlike_knowledge(
    article_id: int,
    user_id: int = Depends(get_required_user_id),
    db: Session = Depends(get_db)
):
    """
    取消点赞知识文章

    如果未点赞则忽略，支持重复调用
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="请先登录"
            )

        KnowledgeService.toggle_like(db, article_id, user_id, "remove")
        return {
            "code": 200,
            "message": "已取消点赞",
            "data": {
                "article_id": article_id,
                "liked": False
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"取消点赞失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消点赞失败: {str(e)}"
        )


# ==================== 评论接口 ====================

@router.get("/{article_id}/comments", summary="获取文章评论")
async def get_comments(
    article_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    获取文章评论列表

    返回顶级评论（不包含回复）
    按创建时间倒序排列
    """
    try:
        result = KnowledgeService.get_comments(db, article_id, page, page_size)
        return {
            "code": 200,
            "message": "获取成功",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取评论失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取评论失败: {str(e)}"
        )


@router.post("/{article_id}/comment", summary="提交评论")
async def create_comment(
    article_id: int,
    comment_data: CommentCreate,
    user_id: int = Depends(get_required_user_id),
    db: Session = Depends(get_db)
):
    """
    提交文章评论

    支持两种评论类型：
    - 直接评论（不提供parent_id）
    - 回复评论（提供parent_id）

    评论内容1-1000字符
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="请先登录"
            )

        comment = KnowledgeService.create_comment(db, article_id, user_id, comment_data)
        return {
            "code": 200,
            "message": "评论成功",
            "data": comment
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"提交评论失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交评论失败: {str(e)}"
        )


# ==================== 首页数据接口 ====================

@router.get("/home/categories", summary="获取首页分类数据")
async def get_home_categories(
    db: Session = Depends(get_db)
):
    """
    获取首页分类统计数据

    返回各分类的文章数量
    """
    try:
        from sqlalchemy import func
        from app.models.knowledge import KnowledgeArticle

        # 按分类统计文章数
        categories = db.query(
            KnowledgeArticle.category,
            func.count(KnowledgeArticle.id).label('count')
        ).filter(
            KnowledgeArticle.is_deleted == False,
            KnowledgeArticle.status == 'published'
        ).group_by(KnowledgeArticle.category).all()

        # 分类名称映射
        category_names = {
            'anxiety': '焦虑抑郁',
            'depression': '情绪管理',
            'emotion': '情感问题',
            'career': '职场压力',
            'family': '家庭关系',
            'growth': '个人成长',
            'other': '其他'
        }

        result = []
        for category, count in categories:
            result.append({
                'category': category,
                'name': category_names.get(category, category),
                'count': count
            })

        return {
            "code": 200,
            "message": "获取成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"获取分类数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分类数据失败: {str(e)}"
        )


@router.get("/home/hot", summary="获取首页热门知识")
async def get_home_hot_knowledge(
    limit: int = Query(6, ge=1, le=20, description="数量限制"),
    db: Session = Depends(get_db),
    user_id: Optional[int] = Depends(get_current_user_id)
):
    """
    获取首页热门知识推荐

    按浏览量、点赞数、收藏数综合排序
    返回最受欢迎的文章
    """
    try:
        query = KnowledgeListQuery(
            sort="hot",
            page=1,
            page_size=limit
        )
        result = KnowledgeService.get_knowledge_list(db, query, user_id)

        return {
            "code": 200,
            "message": "获取成功",
            "data": result['items']
        }
    except Exception as e:
        logger.error(f"获取热门知识失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取热门知识失败: {str(e)}"
        )


@router.get("/home/latest", summary="获取首页最新知识")
async def get_home_latest_knowledge(
    limit: int = Query(6, ge=1, le=20, description="数量限制"),
    db: Session = Depends(get_db),
    user_id: Optional[int] = Depends(get_current_user_id)
):
    """
    获取首页最新知识

    按发布时间倒序排列
    返回最新发布的文章
    """
    try:
        query = KnowledgeListQuery(
            sort="latest",
            page=1,
            page_size=limit
        )
        result = KnowledgeService.get_knowledge_list(db, query, user_id)

        return {
            "code": 200,
            "message": "获取成功",
            "data": result['items']
        }
    except Exception as e:
        logger.error(f"获取最新知识失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取最新知识失败: {str(e)}"
        )


# ==================== 用户收藏接口 ====================

@router.get("/user/favorites", summary="获取用户收藏列表")
async def get_user_favorites(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的收藏列表

    按收藏时间倒序排列
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="请先登录"
            )

        result = KnowledgeService.get_user_favorites(db, user_id, page, page_size)
        return {
            "code": 200,
            "message": "获取成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"获取收藏列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取收藏列表失败: {str(e)}"
        )
