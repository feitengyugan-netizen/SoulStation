"""
视频通话 WebSocket 信令服务器
"""
from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Dict, Set
import json
import logging

from app.core.database import get_db
from app.core.security import decode_access_token
from app.services.video_call_service import VideoCallService
from app.core.webrtc import (
    MSG_TYPE_OFFER,
    MSG_TYPE_ANSWER,
    MSG_TYPE_ICE_CANDIDATE,
    MSG_TYPE_JOIN,
    MSG_TYPE_LEAVE,
    MSG_TYPE_END,
    MSG_TYPE_ERROR,
    CALL_STATUS_PENDING,
    CALL_STATUS_RINGING,
    CALL_STATUS_IN_PROGRESS
)

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # 房间ID -> WebSocket连接集合
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # SessionID -> WebSocket连接
        self.session_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, room_id: str, session_id: int):
        """连接到房间"""
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        self.active_connections[room_id].add(websocket)
        self.session_connections[session_id] = websocket
        logger.info(f"WebSocket 连接已建立: room_id={room_id}, session_id={session_id}")

    def disconnect(self, websocket: WebSocket, room_id: str, session_id: int):
        """断开连接"""
        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
        if session_id in self.session_connections:
            del self.session_connections[session_id]
        logger.info(f"WebSocket 连接已断开: room_id={room_id}, session_id={session_id}")

    async def broadcast_to_room(self, room_id: str, message: dict, exclude_ws: WebSocket = None):
        """向房间内所有客户端广播消息"""
        if room_id not in self.active_connections:
            logger.warning(f"房间不存在: {room_id}")
            return

        connections_to_remove = set()
        for connection in self.active_connections[room_id]:
            if connection != exclude_ws:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"发送消息失败: {str(e)}")
                    connections_to_remove.add(connection)

        # 清理失效的连接
        for connection in connections_to_remove:
            self.active_connections[room_id].discard(connection)

    async def send_to_session(self, session_id: int, message: dict):
        """向特定会话发送消息"""
        if session_id not in self.session_connections:
            logger.warning(f"会话连接不存在: {session_id}")
            return

        try:
            await self.session_connections[session_id].send_json(message)
        except Exception as e:
            logger.error(f"发送消息到会话失败: {str(e)}")


# 全局连接管理器
manager = ConnectionManager()


async def handle_offer(websocket: WebSocket, data: dict, db: Session):
    """处理 SDP Offer"""
    try:
        session_id = data.get("session_id")
        sdp = data.get("sdp")
        user_id = data.get("user_id")
        user_type = data.get("user_type")

        if not all([session_id, sdp, user_id, user_type]):
            await websocket.send_json({
                "type": MSG_TYPE_ERROR,
                "data": {"message": "缺少必要参数"}
            })
            return

        # 保存 Offer SDP
        VideoCallService.save_sdp(db, session_id, sdp, user_type)

        # 广播 Offer 到房间内的其他用户
        call_session = db.query(__import__('app.models.video_call', fromlist=['VideoCallSession']).VideoCallSession).filter(
            __import__('app.models.video_call', fromlist=['VideoCallSession']).VideoCallSession.id == session_id
        ).first()

        if call_session:
            await manager.broadcast_to_room(
                call_session.room_id,
                {
                    "type": MSG_TYPE_OFFER,
                    "data": {
                        "session_id": session_id,
                        "sdp": sdp,
                        "user_type": user_type
                    }
                },
                exclude_ws=websocket
            )

        logger.info(f"SDP Offer 已处理: session_id={session_id}")

    except Exception as e:
        logger.error(f"处理 Offer 失败: {str(e)}")
        await websocket.send_json({
            "type": MSG_TYPE_ERROR,
            "data": {"message": f"处理 Offer 失败: {str(e)}"}
        })


async def handle_answer(websocket: WebSocket, data: dict, db: Session):
    """处理 SDP Answer"""
    try:
        session_id = data.get("session_id")
        sdp = data.get("sdp")
        user_id = data.get("user_id")
        user_type = data.get("user_type")

        if not all([session_id, sdp, user_id, user_type]):
            await websocket.send_json({
                "type": MSG_TYPE_ERROR,
                "data": {"message": "缺少必要参数"}
            })
            return

        # 保存 Answer SDP
        VideoCallService.save_sdp(db, session_id, sdp, user_type)

        # 广播 Answer 到房间内的其他用户
        call_session = db.query(__import__('app.models.video_call', fromlist=['VideoCallSession']).VideoCallSession).filter(
            __import__('app.models.video_call', fromlist=['VideoCallSession']).VideoCallSession.id == session_id
        ).first()

        if call_session:
            await manager.broadcast_to_room(
                call_session.room_id,
                {
                    "type": MSG_TYPE_ANSWER,
                    "data": {
                        "session_id": session_id,
                        "sdp": sdp,
                        "user_type": user_type
                    }
                },
                exclude_ws=websocket
            )

        # 更新通话状态为进行中
        await VideoCallService.update_call_status(db, session_id, CALL_STATUS_IN_PROGRESS)

        logger.info(f"SDP Answer 已处理: session_id={session_id}")

    except Exception as e:
        logger.error(f"处理 Answer 失败: {str(e)}")
        await websocket.send_json({
            "type": MSG_TYPE_ERROR,
            "data": {"message": f"处理 Answer 失败: {str(e)}"}
        })


async def handle_ice_candidate(websocket: WebSocket, data: dict, db: Session):
    """处理 ICE 候选"""
    try:
        session_id = data.get("session_id")
        candidate = data.get("candidate")
        user_type = data.get("user_type")

        if not all([session_id, candidate, user_type]):
            return

        # 广播 ICE 候选到房间内的其他用户
        call_session = db.query(__import__('app.models.video_call', fromlist=['VideoCallSession']).VideoCallSession).filter(
            __import__('app.models.video_call', fromlist=['VideoCallSession']).VideoCallSession.id == session_id
        ).first()

        if call_session:
            await manager.broadcast_to_room(
                call_session.room_id,
                {
                    "type": MSG_TYPE_ICE_CANDIDATE,
                    "data": {
                        "session_id": session_id,
                        "candidate": candidate,
                        "user_type": user_type
                    }
                },
                exclude_ws=websocket
            )

    except Exception as e:
        logger.error(f"处理 ICE 候选失败: {str(e)}")


async def handle_join_call(websocket: WebSocket, data: dict, db: Session):
    """处理加入通话"""
    try:
        session_id = data.get("session_id")
        user_id = data.get("user_id")
        user_type = data.get("user_type")

        logger.info(f"收到加入通话请求: session_id={session_id} (type: {type(session_id)}), user_id={user_id} (type: {type(user_id)}), user_type={user_type} (type: {type(user_type)})")

        if not all([session_id, user_id, user_type]):
            logger.warning(f"缺少必要参数: session_id={session_id}, user_id={user_id}, user_type={user_type}")
            await websocket.send_json({
                "type": MSG_TYPE_ERROR,
                "data": {"message": "缺少必要参数"}
            })
            return

        # 加入通话
        result = await VideoCallService.join_call(db, session_id, user_id, user_type)

        # 通知房间内其他用户
        await manager.broadcast_to_room(
            result["room_id"],
            {
                "type": MSG_TYPE_JOIN,
                "data": {
                    "session_id": session_id,
                    "user_id": user_id,
                    "user_type": user_type
                }
            },
            exclude_ws=websocket
        )

        # 发送加入成功响应
        await websocket.send_json({
            "type": "joined",
            "data": result
        })

        logger.info(f"用户已加入通话: user_id={user_id}, session_id={session_id}")

    except Exception as e:
        logger.error(f"加入通话失败: {str(e)}")
        await websocket.send_json({
            "type": MSG_TYPE_ERROR,
            "data": {"message": f"加入通话失败: {str(e)}"}
        })


async def handle_leave_call(websocket: WebSocket, data: dict, room_id: str, db: Session):
    """处理离开通话"""
    try:
        session_id = data.get("session_id")
        user_id = data.get("user_id")

        if not all([session_id, user_id]):
            return

        # 通知房间内其他用户
        await manager.broadcast_to_room(
            room_id,
            {
                "type": MSG_TYPE_LEAVE,
                "data": {
                    "session_id": session_id,
                    "user_id": user_id
                }
            },
            exclude_ws=websocket
        )

        logger.info(f"用户已离开通话: user_id={user_id}, session_id={session_id}")

    except Exception as e:
        logger.error(f"离开通话失败: {str(e)}")


async def handle_end_call(websocket: WebSocket, data: dict, room_id: str, db: Session):
    """处理结束通话"""
    try:
        session_id = data.get("session_id")
        user_id = data.get("user_id")
        reason = data.get("reason", "user_ended")

        if not all([session_id, user_id]):
            return

        # 结束通话
        await VideoCallService.end_call(db, session_id, user_id, reason)

        # 通知房间内所有用户通话已结束
        await manager.broadcast_to_room(
            room_id,
            {
                "type": MSG_TYPE_END,
                "data": {
                    "session_id": session_id,
                    "reason": reason
                }
            }
        )

        logger.info(f"通话已结束: session_id={session_id}, reason={reason}")

    except Exception as e:
        logger.error(f"结束通话失败: {str(e)}")
