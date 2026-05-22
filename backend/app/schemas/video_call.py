"""
视频通话相关的 Pydantic Schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


# ==================== 视频通话相关 ====================

class VideoCallCreateRequest(BaseModel):
    """发起通话请求"""
    appointment_id: int = Field(..., description="预约ID")
    call_type: str = Field(..., pattern=r'^(video|voice)$', description="通话类型：video/voice")


class VideoCallResponse(BaseModel):
    """通话信息响应"""
    id: int
    appointment_id: int
    caller_id: int
    caller_type: str
    call_type: str
    call_status: str
    room_id: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VideoCallStatusResponse(BaseModel):
    """通话状态响应"""
    session_id: int
    call_status: str
    call_type: str
    room_id: str
    duration: int
    is_participant: bool


class VideoCallEndRequest(BaseModel):
    """结束通话请求"""
    end_reason: Optional[str] = Field("user_ended", description="结束原因")


class CallStatsResponse(BaseModel):
    """通话统计响应"""
    total_calls: int
    total_duration: int
    average_duration: int
    last_call_at: Optional[datetime] = None


class CallHistoryResponse(BaseModel):
    """通话历史响应"""
    session_id: int
    call_type: str
    call_status: str
    duration: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    end_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== WebSocket 消息 ====================

class WebRTCMessageSchema(BaseModel):
    """WebSocket 消息格式"""
    type: str = Field(..., description="消息类型：offer/answer/ice_candidate/join/leave/end")
    data: Dict[str, Any] = Field(default_factory=dict, description="消息数据")


class OfferMessage(BaseModel):
    """SDP Offer 消息"""
    type: str = "offer"
    data: Dict[str, Any] = Field(..., description="包含 sdp 和 session_id")


class AnswerMessage(BaseModel):
    """SDP Answer 消息"""
    type: str = "answer"
    data: Dict[str, Any] = Field(..., description="包含 sdp 和 session_id")


class IceCandidateMessage(BaseModel):
    """ICE 候选消息"""
    type: str = "ice_candidate"
    data: Dict[str, Any] = Field(..., description="包含 candidate 和 session_id")


class JoinCallMessage(BaseModel):
    """加入通话消息"""
    type: str = "join"
    data: Dict[str, Any] = Field(..., description="包含 session_id 和 user_info")


class LeaveCallMessage(BaseModel):
    """离开通话消息"""
    type: str = "leave"
    data: Dict[str, Any] = Field(..., description="包含 session_id")


class EndCallMessage(BaseModel):
    """结束通话消息"""
    type: str = "end"
    data: Dict[str, Any] = Field(..., description="包含 session_id 和 reason")


class ErrorMessage(BaseModel):
    """错误消息"""
    type: str = "error"
    data: Dict[str, Any] = Field(..., description="包含错误信息")
