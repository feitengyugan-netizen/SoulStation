"""
WebRTC 配置和工具函数
"""
import uuid
import secrets
from typing import List, Dict
from app.core.security import create_access_token


# ==================== ICE 服务器配置 ====================

# 使用 Google 的免费公共 STUN 服务器
ICE_SERVERS = [
    {
        "urls": "stun:stun.l.google.com:19302"
    },
    {
        "urls": "stun:stun1.l.google.com:19302"
    },
    {
        "urls": "stun:stun2.l.google.com:19302"
    },
    {
        "urls": "stun:stun3.l.google.com:19302"
    },
    {
        "urls": "stun:stun4.l.google.com:19302"
    }
]


# ==================== 房间 ID 生成 ====================

def generate_room_id() -> str:
    """
    生成唯一的 WebRTC 房间ID

    Returns:
        str: 格式为 "call-{uuid}" 的房间ID
    """
    return f"call-{uuid.uuid4()}"


def generate_short_room_id() -> str:
    """
    生成短房间ID（用于快速连接）

    Returns:
        str: 12字符的随机字符串
    """
    return secrets.token_urlsafe(9)[:12]


# ==================== Token 生成 ====================

def generate_call_token(appointment_id: int, user_id: int, user_type: str) -> str:
    """
    生成视频通话 WebSocket 连接 token

    Args:
        appointment_id: 预约ID
        user_id: 用户ID
        user_type: 用户类型（user/counselor）

    Returns:
        str: JWT token
    """
    # Token 中包含预约信息，用于 WebSocket 验证
    data = {
        "sub": str(user_id),
        "appointment_id": str(appointment_id),
        "user_type": user_type,
        "type": "video_call"
    }
    return create_access_token(data)


def verify_call_token(token: str) -> Dict:
    """
    验证通话 token 并返回信息

    Args:
        token: JWT token

    Returns:
        Dict: 包含用户信息的字典
    """
    from app.core.security import decode_access_token
    return decode_access_token(token)


# ==================== WebRTC 配置 ====================

def get_webrtc_configuration() -> Dict:
    """
    获取 WebRTC 配置

    Returns:
        Dict: 包含 ICE 服务器的配置
    """
    return {
        "iceServers": ICE_SERVERS
    }


def get_media_constraints(call_type: str) -> Dict:
    """
    获取媒体约束

    Args:
        call_type: 通话类型（video/voice）

    Returns:
        Dict: 媒体约束配置
    """
    if call_type == "video":
        return {
            "audio": True,
            "video": {
                "width": {"ideal": 1280},
                "height": {"ideal": 720},
                "frameRate": {"ideal": 30}
            }
        }
    else:  # voice
        return {
            "audio": True,
            "video": False
        }


# ==================== 常量定义 ====================

# 通话状态
CALL_STATUS_PENDING = "pending"
CALL_STATUS_RINGING = "ringing"
CALL_STATUS_IN_PROGRESS = "in_progress"
CALL_STATUS_ENDED = "ended"
CALL_STATUS_REJECTED = "rejected"
CALL_STATUS_FAILED = "failed"

# 通话类型
CALL_TYPE_VIDEO = "video"
CALL_TYPE_VOICE = "voice"

# 结束原因
END_REASON_USER_ENDED = "user_ended"
END_REASON_CALLER_CANCELLED = "caller_cancelled"
END_REASON_TIMEOUT = "timeout"
END_REASON_NETWORK_ERROR = "network_error"
END_REASON_PERMISSION_DENIED = "permission_denied"

# WebSocket 消息类型
MSG_TYPE_OFFER = "offer"
MSG_TYPE_ANSWER = "answer"
MSG_TYPE_ICE_CANDIDATE = "ice_candidate"
MSG_TYPE_JOIN = "join"
MSG_TYPE_LEAVE = "leave"
MSG_TYPE_END = "end"
MSG_TYPE_ERROR = "error"
MSG_TYPE_RINGING = "ringing"
