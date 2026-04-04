"""
预约提醒定时任务
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.counselor import Appointment
from app.models.user import User
from app.services.email_service import EmailService
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def check_and_send_reminders():
    """检查并发送预约提醒"""
    db: Session = next(get_db())

    try:
        # 查找1小时后开始且未发送提醒的预约
        one_hour_later = datetime.now() + timedelta(hours=1)
        appointments = db.query(Appointment).filter(
            Appointment.appointment_date.between(
                one_hour_later - timedelta(minutes=5),
                one_hour_later + timedelta(minutes=5)
            ),
            Appointment.status.in_(['confirmed', 'in_progress']),
            Appointment.reminder_sent == False
        ).all()

        for appt in appointments:
            try:
                # 获取用户邮箱
                user = db.query(User).filter(User.id == appt.user_id).first()

                if user and user.email:
                    EmailService.send_appointment_reminder(
                        email=user.email,
                        nickname=user.nickname or "用户",
                        counselor_name=appt.counselor.name,
                        appointment_date=appt.appointment_date.strftime("%Y-%m-%d"),
                        appointment_time=appt.appointment_date.strftime("%H:%M"),
                        consultation_type=appt.consultation_type
                    )

                    # 标记已发送
                    appt.reminder_sent = True
                    appt.reminder_sent_at = datetime.now()
                    db.commit()

                    logger.info(f"预约提醒已发送: {appt.appointment_no}")
            except Exception as e:
                logger.error(f"发送预约提醒失败: {e}")
    finally:
        db.close()

def start_scheduler():
    """启动定时任务"""
    scheduler.add_job(
        check_and_send_reminders,
        'interval',
        minutes=10,  # 每10分钟检查一次
        id='appointment_reminder'
    )
    scheduler.start()
    logger.info("预约提醒定时任务已启动")
