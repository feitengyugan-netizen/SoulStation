"""
测试语音通话功能
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine
from app.models.user import User
from app.models.counselor import Counselor, Appointment
from app.models.video_call import VideoCallSession
from app.services.video_call_service import VideoCallService


def test_voice_call():
    """测试语音通话功能"""

    # 创建数据库会话
    with Session(engine) as db:
        print("=== 测试语音通话功能 ===\n")

        # 1. 检查用户数据
        print("1. 检查用户数据...")
        users = db.query(User).limit(5).all()
        print(f"   找到 {len(users)} 个用户:")
        for user in users:
            print(f"   - ID: {user.id}, Username: {user.username}, Email: {user.email}")

        if not users:
            print("   ❌ 没有找到用户，请先创建测试用户")
            return

        # 2. 检查咨询师数据
        print("\n2. 检查咨询师数据...")
        counselors = db.query(Counselor).limit(5).all()
        print(f"   找到 {len(counselors)} 个咨询师:")
        for counselor in counselors:
            print(f"   - ID: {counselor.id}, Name: {counselor.name}, User ID: {counselor.user_id}")

        if not counselors:
            print("   ❌ 没有找到咨询师，请先创建测试咨询师")
            return

        # 3. 检查预约数据
        print("\n3. 检查预约数据...")
        appointments = db.query(Appointment).limit(5).all()
        print(f"   找到 {len(appointments)} 个预约:")
        for appointment in appointments:
            print(f"   - ID: {appointment.id}, Status: {appointment.status}, Date: {appointment.appointment_date}")

        if not appointments:
            print("   ❌ 没有找到预约，请先创建测试预约")
            return

        # 4. 测试发起语音通话
        print("\n4. 测试发起语音通话...")
        test_appointment = appointments[0]
        test_user = users[0]

        try:
            result = VideoCallService.initiate_call(
                db,
                test_appointment.id,
                test_user.id,
                'user',
                'voice'  # 语音通话
            )
            print(f"   ✅ 语音通话发起成功!")
            print(f"   - Session ID: {result['session_id']}")
            print(f"   - Room ID: {result['room_id']}")
            print(f"   - Call Status: {result['call_status']}")

            # 5. 检查通话会话是否创建成功
            print("\n5. 检查通话会话...")
            session = db.query(VideoCallSession).filter(
                VideoCallSession.id == result['session_id']
            ).first()

            if session:
                print(f"   ✅ 通话会话创建成功!")
                print(f"   - ID: {session.id}")
                print(f"   - Call Type: {session.call_type}")
                print(f"   - Status: {session.call_status}")
                print(f"   - Room ID: {session.room_id}")
            else:
                print(f"   ❌ 未找到通话会话")

            # 6. 测试结束通话
            print("\n6. 测试结束通话...")
            end_result = VideoCallService.end_call(
                db,
                result['session_id'],
                test_user.id,
                'test_end'
            )

            if end_result:
                print(f"   ✅ 通话结束成功!")

                # 检查通话状态
                db.refresh(session)
                print(f"   - Final Status: {session.call_status}")
                print(f"   - Duration: {session.duration} seconds")
            else:
                print(f"   ❌ 通话结束失败")

            print("\n=== 语音通话功能测试完成 ===")

        except Exception as e:
            print(f"   ❌ 语音通话测试失败: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_voice_call()