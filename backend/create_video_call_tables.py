"""
创建视频通话相关表
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def create_video_call_tables():
    """创建视频通话表"""
    with engine.connect() as conn:
        print("=== 创建视频通话表 ===\n")

        # 创建 video_call_sessions 表
        create_sessions_table = """
        CREATE TABLE IF NOT EXISTS video_call_sessions (
            id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '通话会话ID',
            appointment_id BIGINT NOT NULL COMMENT '关联预约ID',
            caller_id BIGINT NOT NULL COMMENT '发起者ID',
            caller_type ENUM('user', 'counselor') NOT NULL COMMENT '发起者类型',
            call_type ENUM('video', 'voice') NOT NULL DEFAULT 'video' COMMENT '通话类型',
            call_status ENUM('pending', 'ringing', 'in_progress', 'ended', 'rejected', 'failed') DEFAULT 'pending' COMMENT '通话状态',
            room_id VARCHAR(100) UNIQUE NOT NULL COMMENT 'WebRTC房间ID',
            caller_sdp TEXT COMMENT '发起者SDP',
            callee_sdp TEXT COMMENT '接收者SDP',
            start_time DATETIME COMMENT '实际开始时间',
            end_time DATETIME COMMENT '结束时间',
            duration INT DEFAULT 0 COMMENT '通话时长（秒）',
            end_reason VARCHAR(50) COMMENT '结束原因',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            FOREIGN KEY (appointment_id) REFERENCES appointments(id),
            INDEX idx_appointment (appointment_id),
            INDEX idx_room (room_id),
            INDEX idx_status (call_status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='视频通话会话表'
        """

        try:
            conn.execute(text(create_sessions_table))
            print("video_call_sessions 表创建成功")
        except Exception as e:
            print(f"video_call_sessions 表创建失败: {e}")

        # 创建 video_call_events 表
        create_events_table = """
        CREATE TABLE IF NOT EXISTS video_call_events (
            id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '事件ID',
            call_session_id BIGINT NOT NULL COMMENT '通话会话ID',
            event_type VARCHAR(50) NOT NULL COMMENT '事件类型',
            event_data TEXT COMMENT '事件数据（JSON）',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            FOREIGN KEY (call_session_id) REFERENCES video_call_sessions(id) ON DELETE CASCADE,
            INDEX idx_session (call_session_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='视频通话事件日志表'
        """

        try:
            conn.execute(text(create_events_table))
            print("video_call_events 表创建成功")
        except Exception as e:
            print(f"video_call_events 表创建失败: {e}")

        # 检查appointments表是否有必要的字段
        print("\n=== 检查appointments表字段 ===")

        try:
            # 检查并添加 call_enabled 字段
            try:
                conn.execute(text("ALTER TABLE appointments ADD COLUMN call_enabled BOOLEAN DEFAULT FALSE COMMENT '是否启用通话'"))
                print("appointments.call_enabled 字段添加成功")
            except:
                print("appointments.call_enabled 字段已存在")

            # 检查并添加 last_call_id 字段
            try:
                conn.execute(text("ALTER TABLE appointments ADD COLUMN last_call_id BIGINT COMMENT '最后一个通话会话ID'"))
                print("appointments.last_call_id 字段添加成功")
            except:
                print("appointments.last_call_id 字段已存在")

            # 检查并添加 call_count 字段
            try:
                conn.execute(text("ALTER TABLE appointments ADD COLUMN call_count INT DEFAULT 0 COMMENT '通话次数'"))
                print("appointments.call_count 字段添加成功")
            except:
                print("appointments.call_count 字段已存在")

        except Exception as e:
            print(f"字段检查/添加失败: {e}")

        print("\n=== 完成 ===")
        print("视频通话表创建完成！")

if __name__ == "__main__":
    create_video_call_tables()