"""
咨询评价 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.models.counselor import Counselor, ConsultationReview, Appointment
from pydantic import BaseModel, Field

router = APIRouter(prefix="/reviews", tags=["咨询评价"])
security = HTTPBearer()
logger = logging.getLogger(__name__)


class ReviewSubmitRequest(BaseModel):
    """评价提交请求"""
    rating: int = Field(..., ge=1, le=5, description="评分1-5星")
    tags: list[str] = Field(default_factory=list, description="评价标签")
    content: Optional[str] = Field(None, description="评价内容")
    is_anonymous: bool = Field(True, description="是否匿名")


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """从token中获取用户ID"""
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )
    return int(user_id)


@router.post("/{appointment_id}", summary="提交咨询评价")
async def submit_review(
    appointment_id: int,
    review_data: ReviewSubmitRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    提交咨询评价

    - **rating**: 评分（1-5星）
    - **tags**: 评价标签（如：专业、耐心、有效等）
    - **content**: 详细评价内容
    - **is_anonymous**: 是否匿名显示
    """
    try:
        # 验证预约
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()

        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="预约不存在"
            )

        # 验证权限
        if appointment.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能评价自己的预约"
            )

        # 验证状态（只有已完成的咨询才能评价）
        if appointment.status != 'completed':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能评价已完成的咨询"
            )

        # 检查是否已评价
        existing_review = db.query(ConsultationReview).filter(
            ConsultationReview.appointment_id == appointment_id
        ).first()

        if existing_review and existing_review.rating is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您已经评价过该咨询"
            )

        # 创建或更新评价
        if existing_review:
            existing_review.rating = review_data.rating
            existing_review.tags = review_data.tags
            existing_review.content = review_data.content
            existing_review.is_anonymous = review_data.is_anonymous
            existing_review.status = 'completed'
        else:
            review = ConsultationReview(
                appointment_id=appointment_id,
                user_id=user_id,
                counselor_id=appointment.counselor_id,
                rating=review_data.rating,
                tags=review_data.tags,
                content=review_data.content,
                is_anonymous=review_data.is_anonymous,
                status='completed'
            )
            db.add(review)

        db.commit()

        return {
            "code": 200,
            "message": "评价提交成功",
            "data": {
                "appointment_id": appointment_id,
                "rating": review_data.rating
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"提交评价失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交评价失败: {str(e)}"
        )


@router.get("/{appointment_id}", summary="获取预约评价")
async def get_review(
    appointment_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取指定预约的评价信息"""
    try:
        # 验证预约
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()

        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="预约不存在"
            )

        # 验证权限
        if appointment.user_id != user_id and appointment.counselor_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看该评价"
            )

        review = db.query(ConsultationReview).filter(
            ConsultationReview.appointment_id == appointment_id
        ).first()

        if not review:
            return {
                "code": 200,
                "message": "暂无评价",
                "data": None
            }

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "id": review.id,
                "rating": review.rating,
                "tags": review.tags or [],
                "content": review.content,
                "is_anonymous": review.is_anonymous,
                "status": review.status,
                "created_at": review.created_at.isoformat() if review.created_at else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取评价失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取评价失败: {str(e)}"
        )


@router.get("/pending/list", summary="获取待评价列表")
async def get_pending_reviews(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取当前用户待评价的预约列表"""
    try:
        # 查询已完成但未评价的预约
        appointments = db.query(Appointment).filter(
            Appointment.user_id == user_id,
            Appointment.status == 'completed'
        ).all()

        pending_reviews = []
        for apt in appointments:
            # 检查是否已评价
            review = db.query(ConsultationReview).filter(
                ConsultationReview.appointment_id == apt.id
            ).first()

            if not review or review.rating is None:
                counselor = db.query(Counselor).filter(
                    Counselor.id == apt.counselor_id
                ).first()

                pending_reviews.append({
                    "appointment_id": apt.id,
                    "counselor_name": counselor.name if counselor else "未知",
                    "completed_at": apt.completed_at.isoformat() if apt.completed_at else None,
                    "consultation_type": apt.consultation_type
                })

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "total": len(pending_reviews),
                "list": pending_reviews
            }
        }
    except Exception as e:
        logger.error(f"获取待评价列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取待评价列表失败: {str(e)}"
        )
