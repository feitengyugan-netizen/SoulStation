"""
视频通话 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db
from app.core.security import decode_access_token
from app.core.webrtc import (
    generate_call_token,
    get_webrtc_configuration,
    get_media_constraints
)
from app.schemas.video_call import (
    VideoCallCreateRequest,
    VideoCallResponse,
    VideoCallStatusResponse,
    VideoCallEndRequest,
    CallHistoryResponse
)
from app.services.video_call_service import VideoCallService
from app.models.video_call import VideoCallSession

router = APIRouter(prefix="/video-call", tags=["视频通话"])
security = HTTPBearer()
logger = logging.getLogger(__name__)


def get_current_user_info(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """从 token 中获取当前用户信息"""
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


def get_current_user_role(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> str:
    """获取当前用户角色"""
    from app.models.counselor import Counselor

    user_id = get_current_user_info(credentials)

    # 检查是否是咨询师
    counselor = db.query(Counselor).filter(
        Counselor.user_id == user_id,
        Counselor.is_deleted == False
    ).first()

    if counselor:
        return 'counselor'
    else:
        return 'user'


@router.get("/config", summary="获取 WebRTC 配置")
async def get_webrtc_config():
    """
    获取 WebRTC 连接配置

    返回 ICE 服务器配置和媒体约束
    """
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "iceServers": get_webrtc_configuration()["iceServers"],
            "mediaConstraints": {
                "video": get_media_constraints("video"),
                "voice": get_media_constraints("voice")
            }
        }
    }


@router.post("/call/initiate", summary="发起通话")
async def initiate_call(
    call_data: VideoCallCreateRequest,
    user_id: int = Depends(get_current_user_info),
    user_type: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """
    发起视频或语音通话

    - **appointment_id**: 预约ID
    - **call_type**: 通话类型（video/voice）
    """
    try:
        result = await VideoCallService.initiate_call(
            db,
            call_data.appointment_id,
            user_id,
            user_type,
            call_data.call_type
        )

        # 生成 WebSocket token
        ws_token = generate_call_token(
            call_data.appointment_id,
            user_id,
            user_type
        )

        return {
            "code": 200,
            "message": "通话已发起",
            "data": {
                **result,
                "ws_token": ws_token,
                "ws_url": f"/api/video-call/ws/video-call/{ws_token}"
            }
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"发起通话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发起通话失败"
        )


@router.post("/call/{session_id}/join", summary="加入通话")
async def join_call(
    session_id: int,
    user_id: int = Depends(get_current_user_info),
    user_type: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """
    加入已发起的通话

    - **session_id**: 通话会话ID
    """
    try:
        result = await VideoCallService.join_call(
            db,
            session_id,
            user_id,
            user_type
        )

        # 生成 WebSocket token
        call_session = db.query(VideoCallSession).filter(
            VideoCallSession.id == session_id
        ).first()

        if call_session:
            ws_token = generate_call_token(
                call_session.appointment_id,
                user_id,
                user_type
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="通话会话不存在"
            )

        return {
            "code": 200,
            "message": "已加入通话",
            "data": {
                **result,
                "ws_token": ws_token,
                "ws_url": f"/api/video-call/ws/video-call/{ws_token}"
            }
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"加入通话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="加入通话失败"
        )


@router.post("/call/{session_id}/end", summary="结束通话")
async def end_call(
    session_id: int,
    end_data: Optional[VideoCallEndRequest] = None,
    user_id: int = Depends(get_current_user_info),
    db: Session = Depends(get_db)
):
    """
    结束通话

    - **session_id**: 通话会话ID
    - **end_reason**: 结束原因（可选）
    """
    try:
        end_reason = end_data.end_reason if end_data else "user_ended"
        success = await VideoCallService.end_call(
            db,
            session_id,
            user_id,
            end_reason
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="通话会话不存在"
            )

        return {
            "code": 200,
            "message": "通话已结束",
            "data": {"session_id": session_id}
        }

    except Exception as e:
        logger.error(f"结束通话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="结束通话失败"
        )


@router.get("/call/{session_id}/status", summary="获取通话状态")
async def get_call_status(
    session_id: int,
    user_id: int = Depends(get_current_user_info),
    db: Session = Depends(get_db)
):
    """
    获取当前通话状态

    - **session_id**: 通话会话ID
    """
    try:
        status_data = VideoCallService.get_call_status(
            db,
            session_id,
            user_id
        )

        if not status_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="通话会话不存在"
            )

        return {
            "code": 200,
            "message": "获取成功",
            "data": status_data
        }

    except Exception as e:
        logger.error(f"获取通话状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取通话状态失败"
        )


@router.get("/appointment/{appointment_id}/call-history", summary="获取通话历史")
async def get_call_history(
    appointment_id: int,
    user_id: int = Depends(get_current_user_info),
    db: Session = Depends(get_db)
):
    """
    获取预约的通话历史记录

    - **appointment_id**: 预约ID
    """
    try:
        history = VideoCallService.get_call_history(
            db,
            appointment_id,
            user_id
        )

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "items": history,
                "total": len(history)
            }
        }

    except Exception as e:
        logger.error(f"获取通话历史失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取通话历史失败"
        )


@router.get("/appointment/{appointment_id}/active-call", summary="获取当前活跃通话")
async def get_active_call(
    appointment_id: int,
    user_id: int = Depends(get_current_user_info),
    db: Session = Depends(get_db)
):
    """
    获取预约当前活跃的通话会话

    - **appointment_id**: 预约ID
    """
    try:
        from app.models.video_call import VideoCallSession
        from sqlalchemy import and_

        active_call = db.query(VideoCallSession).filter(
            and_(
                VideoCallSession.appointment_id == appointment_id,
                VideoCallSession.call_status.in_(['pending', 'ringing', 'in_progress'])
            )
        ).order_by(VideoCallSession.created_at.desc()).first()

        if not active_call:
            return {
                "code": 200,
                "message": "暂无活跃通话",
                "data": None
            }

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "session_id": active_call.id,
                "room_id": active_call.room_id,
                "call_status": active_call.call_status,
                "call_type": active_call.call_type,
                "caller_id": active_call.caller_id,
                "caller_type": active_call.caller_type,
                "created_at": active_call.created_at.isoformat()
            }
        }
    except Exception as e:
        logger.error(f"获取活跃通话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取活跃通话失败"
        )


@router.websocket("/ws/video-call/{token}")
async def video_call_websocket(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    """
    视频通话 WebSocket 信令服务器

    处理 WebRTC 信令消息：
    - offer: SDP Offer
    - answer: SDP Answer
    - ice_candidate: ICE 候选
    - join: 加入通话
    - leave: 离开通话
    - end: 结束通话
    """
    from app.api.video_call.websocket import (
        manager,
        handle_offer,
        handle_answer,
        handle_ice_candidate,
        handle_join_call,
        handle_leave_call,
        handle_end_call
    )

    # 验证 token
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=1008, reason="Invalid token")
        return

    user_id = payload.get("sub")
    appointment_id = payload.get("appointment_id")
    user_type = payload.get("user_type")

    if not all([user_id, appointment_id, user_type]):
        await websocket.close(code=1008, reason="Invalid token data")
        return

    user_id = int(user_id)
    appointment_id = int(appointment_id)

    # 查找进行中的通话会话
    from app.models.video_call import VideoCallSession
    call_session = db.query(VideoCallSession).filter(
        VideoCallSession.appointment_id == appointment_id,
        VideoCallSession.call_status.in_(['pending', 'ringing', 'in_progress'])
    ).first()

    if not call_session:
        await websocket.close(code=1008, reason="No active call session")
        return

    room_id = call_session.room_id
    session_id = call_session.id

    # 连接到房间
    await manager.connect(websocket, room_id, session_id)

    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_json()
            message_type = data.get("type")

            # 根据消息类型分发处理
            if message_type == "offer":
                await handle_offer(websocket, data.get("data", {}), db)
            elif message_type == "answer":
                await handle_answer(websocket, data.get("data", {}), db)
            elif message_type == "ice_candidate":
                await handle_ice_candidate(websocket, data.get("data", {}), db)
            elif message_type == "join":
                await handle_join_call(websocket, data.get("data", {}), db)
            elif message_type == "leave":
                await handle_leave_call(websocket, data.get("data", {}), room_id, db)
            elif message_type == "end":
                await handle_end_call(websocket, data.get("data", {}), room_id, db)
            else:
                logger.warning(f"未知消息类型: {message_type}")

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id, session_id)
        logger.info(f"WebSocket 断开连接: user_id={user_id}, session_id={session_id}")
    except Exception as e:
        logger.error(f"WebSocket 错误: {str(e)}")
        manager.disconnect(websocket, room_id, session_id)
