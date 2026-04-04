"""
用户预约订单 API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.models.counselor import Appointment, Counselor
from sqlalchemy import desc, and_

router = APIRouter(prefix="/user", tags=["用户预约"])
security = HTTPBearer()
logger = logging.getLogger(__name__)


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


@router.get("/orders", summary="获取用户订单列表")
async def get_user_orders(
    status_filter: Optional[str] = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取用户的预约订单列表

    支持状态筛选：
    - **pending**: 待确认
    - **confirmed**: 已确认
    - **in_progress**: 进行中
    - **completed**: 已完成
    - **cancelled**: 已取消
    """
    try:
        # 构建查询
        query = db.query(Appointment).filter(
            Appointment.user_id == user_id
        )

        if status_filter:
            query = query.filter(Appointment.status == status_filter)

        # 按创建时间倒序
        query = query.order_by(desc(Appointment.created_at))

        # 分页
        total = query.count()
        appointments = query.offset((page - 1) * page_size).limit(page_size).all()

        # 统计各状态数量
        stats = {}
        for status in ['pending', 'confirmed', 'in_progress', 'completed', 'cancelled']:
            count = db.query(Appointment).filter(
                and_(
                    Appointment.user_id == user_id,
                    Appointment.status == status
                )
            ).count()
            stats[status] = count

        # 格式化订单数据
        order_list = []
        for apt in appointments:
            # 获取咨询师信息
            counselor = db.query(Counselor).filter(
                Counselor.id == apt.counselor_id
            ).first()

            order_list.append({
                "id": apt.id,
                "appointment_no": apt.appointment_no,
                "counselorId": apt.counselor_id,
                "counselorName": counselor.name if counselor else "未知咨询师",
                "counselorTitle": counselor.title if counselor else None,
                "counselorAvatar": counselor.avatar if counselor else "",
                "consultation_type": apt.consultation_type,
                "appointment_date": apt.appointment_date.isoformat() if apt.appointment_date else None,
                "problem_description": apt.problem_description,
                "price": apt.price,
                "status": apt.status,
                "created_at": apt.created_at.isoformat() if apt.created_at else None,
                "reviewed": False  # TODO: 查询评价表
            })

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "list": order_list,
                "total": total,
                "page": page,
                "page_size": page_size,
                "stats": stats
            }
        }
    except Exception as e:
        logger.error(f"获取用户订单失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取订单列表失败: {str(e)}"
        )
