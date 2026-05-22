"""
视频通话业务逻辑服务
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import json
import logging

from app.models.video_call import VideoCallSession, VideoCallEvent
from app.models.counselor import Appointment
from app.models.user import User
from app.models.counselor import Counselor
from app.core.webrtc import (
    generate_room_id,
    CALL_STATUS_PENDING,
    CALL_STATUS_RINGING,
    CALL_STATUS_IN_PROGRESS,
    CALL_STATUS_ENDED,
    CALL_STATUS_REJECTED,
    CALL_STATUS_FAILED,
    END_REASON_USER_ENDED,
    END_REASON_CALLER_CANCELLED,
    END_REASON_TIMEOUT,
    END_REASON_NETWORK_ERROR
)

logger = logging.getLogger(__name__)


class VideoCallService:
    """视频通话服务"""

    @staticmethod
    def verify_call_permission(
        db: Session,
        appointment_id: int,
        user_id: int,
        user_type: str
    ) -> bool:
        """
        验证用户是否有权限加入通话

        Args:
            db: 数据库会话
            appointment_id: 预约ID
            user_id: 用户ID
            user_type: 用户类型（user/counselor）

        Returns:
            bool: 是否有权限
        """
        # 获取预约信息
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()

        if not appointment:
            logger.warning(f"预约不存在: {appointment_id}")
            return False

        # 验证预约状态
        if appointment.status not in ['confirmed', 'in_progress']:
            logger.warning(f"预约状态不允许通话: {appointment.status}")
            return False

        # 验证用户是否为预约参与者
        if user_type == 'user':
            has_permission = appointment.user_id == user_id
        elif user_type == 'counselor':
            # 获取咨询师ID
            counselor = db.query(Counselor).filter(
                Counselor.user_id == user_id,
                Counselor.is_deleted == False
            ).first()
            has_permission = counselor and appointment.counselor_id == counselor.id
        else:
            has_permission = False

        return has_permission

    @staticmethod
    async def initiate_call(
        db: Session,
        appointment_id: int,
        caller_id: int,
        caller_type: str,
        call_type: str
    ) -> Dict:
        """
        发起通话

        Args:
            db: 数据库会话
            appointment_id: 预约ID
            caller_id: 发起者ID
            caller_type: 发起者类型（user/counselor）
            call_type: 通话类型（video/voice）

        Returns:
            Dict: 通话会话信息
        """
        try:
            # 验证权限
            if not VideoCallService.verify_call_permission(db, appointment_id, caller_id, caller_type):
                raise ValueError("无权限发起通话")

            # 检查是否已有进行中的通话
            existing_call = db.query(VideoCallSession).filter(
                and_(
                    VideoCallSession.appointment_id == appointment_id,
                    VideoCallSession.call_status.in_([
                        CALL_STATUS_PENDING,
                        CALL_STATUS_RINGING,
                        CALL_STATUS_IN_PROGRESS
                    ])
                )
            ).first()

            if existing_call:
                logger.info(f"预约 {appointment_id} 已有进行中的通话: {existing_call.id}")
                return {
                    "session_id": existing_call.id,
                    "room_id": existing_call.room_id,
                    "call_status": existing_call.call_status,
                    "call_type": existing_call.call_type,
                    "is_new": False
                }

            # 创建新的通话会话
            room_id = generate_room_id()
            call_session = VideoCallSession(
                appointment_id=appointment_id,
                caller_id=caller_id,
                caller_type=caller_type,
                call_type=call_type,
                call_status=CALL_STATUS_PENDING,
                room_id=room_id
            )

            db.add(call_session)
            db.commit()
            db.refresh(call_session)

            # 更新预约信息
            appointment = db.query(Appointment).filter(
                Appointment.id == appointment_id
            ).first()
            if appointment:
                appointment.call_enabled = True
                appointment.last_call_id = call_session.id
                appointment.call_count = (appointment.call_count or 0) + 1
                db.commit()

            # 记录事件
            event = VideoCallEvent(
                call_session_id=call_session.id,
                event_type="initiated",
                event_data=json.dumps({
                    "caller_id": caller_id,
                    "caller_type": caller_type,
                    "call_type": call_type
                })
            )
            db.add(event)
            db.commit()

            logger.info(f"通话已创建: {call_session.id}, room_id: {room_id}")

            return {
                "session_id": call_session.id,
                "room_id": room_id,
                "call_status": call_session.call_status,
                "call_type": call_session.call_type,
                "is_new": True
            }

        except Exception as e:
            logger.error(f"发起通话失败: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    async def join_call(
        db: Session,
        session_id: int,
        user_id: int,
        user_type: str
    ) -> Dict:
        """
        加入通话

        Args:
            db: 数据库会话
            session_id: 会话ID
            user_id: 用户ID
            user_type: 用户类型

        Returns:
            Dict: 通话信息
        """
        try:
            # 获取通话会话
            call_session = db.query(VideoCallSession).filter(
                VideoCallSession.id == session_id
            ).first()

            if not call_session:
                raise ValueError("通话会话不存在")

            # 验证权限
            if not VideoCallService.verify_call_permission(
                db, call_session.appointment_id, user_id, user_type
            ):
                raise ValueError("无权限加入通话")

            # 更新通话状态
            if call_session.call_status == CALL_STATUS_PENDING:
                call_session.call_status = CALL_STATUS_RINGING
                call_session.start_time = datetime.now()
            elif call_session.call_status == CALL_STATUS_RINGING:
                call_session.call_status = CALL_STATUS_IN_PROGRESS

            db.commit()

            # 记录加入事件
            event = VideoCallEvent(
                call_session_id=session_id,
                event_type="joined",
                event_data=json.dumps({
                    "user_id": user_id,
                    "user_type": user_type
                })
            )
            db.add(event)
            db.commit()

            return {
                "session_id": call_session.id,
                "room_id": call_session.room_id,
                "call_status": call_session.call_status,
                "call_type": call_session.call_type
            }

        except Exception as e:
            logger.error(f"加入通话失败: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    async def end_call(
        db: Session,
        session_id: int,
        user_id: int,
        end_reason: str = END_REASON_USER_ENDED
    ) -> bool:
        """
        结束通话

        Args:
            db: 数据库会话
            session_id: 会话ID
            user_id: 用户ID
            end_reason: 结束原因

        Returns:
            bool: 是否成功
        """
        try:
            # 获取通话会话
            call_session = db.query(VideoCallSession).filter(
                VideoCallSession.id == session_id
            ).first()

            if not call_session:
                logger.warning(f"通话会话不存在: {session_id}")
                return False

            # 如果已经结束，直接返回
            if call_session.call_status == CALL_STATUS_ENDED:
                return True

            # 计算通话时长
            if call_session.start_time:
                duration = (datetime.now() - call_session.start_time).seconds
            else:
                duration = 0

            # 更新通话状态
            call_session.call_status = CALL_STATUS_ENDED
            call_session.end_time = datetime.now()
            call_session.duration = duration
            call_session.end_reason = end_reason

            db.commit()

            # 记录结束事件
            event = VideoCallEvent(
                call_session_id=session_id,
                event_type="ended",
                event_data=json.dumps({
                    "user_id": user_id,
                    "reason": end_reason,
                    "duration": duration
                })
            )
            db.add(event)
            db.commit()

            logger.info(f"通话已结束: {session_id}, 时长: {duration}秒")

            return True

        except Exception as e:
            logger.error(f"结束通话失败: {str(e)}")
            db.rollback()
            return False

    @staticmethod
    async def update_call_status(
        db: Session,
        session_id: int,
        status: str
    ) -> bool:
        """
        更新通话状态

        Args:
            db: 数据库会话
            session_id: 会话ID
            status: 新状态

        Returns:
            bool: 是否成功
        """
        try:
            call_session = db.query(VideoCallSession).filter(
                VideoCallSession.id == session_id
            ).first()

            if not call_session:
                return False

            call_session.call_status = status
            db.commit()

            return True

        except Exception as e:
            logger.error(f"更新通话状态失败: {str(e)}")
            db.rollback()
            return False

    @staticmethod
    def get_call_status(
        db: Session,
        session_id: int,
        user_id: int
    ) -> Optional[Dict]:
        """
        获取通话状态

        Args:
            db: 数据库会话
            session_id: 会话ID
            user_id: 用户ID

        Returns:
            Optional[Dict]: 通话状态信息
        """
        try:
            call_session = db.query(VideoCallSession).filter(
                VideoCallSession.id == session_id
            ).first()

            if not call_session:
                return None

            # 计算实时时长
            if call_session.start_time and call_session.call_status == CALL_STATUS_IN_PROGRESS:
                duration = (datetime.now() - call_session.start_time).seconds
            else:
                duration = call_session.duration or 0

            return {
                "session_id": call_session.id,
                "call_status": call_session.call_status,
                "call_type": call_session.call_type,
                "room_id": call_session.room_id,
                "duration": duration,
                "start_time": call_session.start_time,
                "end_time": call_session.end_time
            }

        except Exception as e:
            logger.error(f"获取通话状态失败: {str(e)}")
            return None

    @staticmethod
    def get_call_history(
        db: Session,
        appointment_id: int,
        user_id: int
    ) -> List[Dict]:
        """
        获取通话历史

        Args:
            db: 数据库会话
            appointment_id: 预约ID
            user_id: 用户ID

        Returns:
            List[Dict]: 通话历史列表
        """
        try:
            calls = db.query(VideoCallSession).filter(
                VideoCallSession.appointment_id == appointment_id
            ).order_by(VideoCallSession.created_at.desc()).all()

            return [
                {
                    "session_id": call.id,
                    "call_type": call.call_type,
                    "call_status": call.call_status,
                    "duration": call.duration,
                    "start_time": call.start_time,
                    "end_time": call.end_time,
                    "end_reason": call.end_reason,
                    "created_at": call.created_at
                }
                for call in calls
            ]

        except Exception as e:
            logger.error(f"获取通话历史失败: {str(e)}")
            return []

    @staticmethod
    def save_sdp(
        db: Session,
        session_id: int,
        sdp: str,
        user_type: str
    ) -> bool:
        """
        保存 SDP 信息

        Args:
            db: 数据库会话
            session_id: 会话ID
            sdp: SDP 内容
            user_type: 用户类型

        Returns:
            bool: 是否成功
        """
        try:
            call_session = db.query(VideoCallSession).filter(
                VideoCallSession.id == session_id
            ).first()

            if not call_session:
                return False

            if user_type == call_session.caller_type:
                call_session.caller_sdp = sdp
            else:
                call_session.callee_sdp = sdp

            db.commit()
            return True

        except Exception as e:
            logger.error(f"保存 SDP 失败: {str(e)}")
            db.rollback()
            return False
