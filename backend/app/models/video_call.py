"""
视频通话相关数据库模型
"""
from sqlalchemy import Column, BigInteger, String, DateTime, Text, Integer, Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class VideoCallSession(Base):
    """视频通话会话表"""
    __tablename__ = "video_call_sessions"

    id = Column(BigInteger, primary_key=True, index=True, comment="通话会话ID")
    appointment_id = Column(BigInteger, ForeignKey("appointments.id"), nullable=False, comment="关联预约ID")
    caller_id = Column(BigInteger, nullable=False, comment="发起者ID")
    caller_type = Column(Enum('user', 'counselor'), nullable=False, comment="发起者类型")

    # 通话配置
    call_type = Column(Enum('video', 'voice'), nullable=False, default='video', comment="通话类型")
    call_status = Column(
        Enum('pending', 'ringing', 'in_progress', 'ended', 'rejected', 'failed'),
        default='pending',
        comment="通话状态"
    )

    # 连接信息
    room_id = Column(String(100), unique=True, nullable=False, index=True, comment="WebRTC房间ID")
    caller_sdp = Column(Text, comment="发起者SDP")
    callee_sdp = Column(Text, comment="接收者SDP")

    # 统计信息
    start_time = Column(DateTime, comment="实际开始时间")
    end_time = Column(DateTime, comment="结束时间")
    duration = Column(Integer, default=0, comment="通话时长（秒）")

    # 结束原因
    end_reason = Column(String(50), comment="结束原因：user_ended/caller_cancelled/timeout/network_error")

    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    appointment = relationship("Appointment", backref="video_calls")
    events = relationship("VideoCallEvent", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<VideoCallSession(id={self.id}, room_id={self.room_id}, status={self.call_status})>"


class VideoCallEvent(Base):
    """视频通话事件日志表"""
    __tablename__ = "video_call_events"

    id = Column(BigInteger, primary_key=True, index=True, comment="事件ID")
    call_session_id = Column(BigInteger, ForeignKey("video_call_sessions.id"), nullable=False, comment="通话会话ID")
    event_type = Column(String(50), nullable=False, comment="事件类型：offer/answer/ice_candidate/joined/left/ended")
    event_data = Column(Text, comment="事件数据（JSON）")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系
    session = relationship("VideoCallSession", back_populates="events")

    def __repr__(self):
        return f"<VideoCallEvent(id={self.id}, type={self.event_type}, session_id={self.call_session_id})>"
