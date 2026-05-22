"""创建 notifications 表"""
import sys
sys.path.insert(0, '.')

from app.core.database import engine, Base
from app.models.counselor import Notification

# 确保所有模型已加载
from app.models import *

# 创建表
Base.metadata.create_all(bind=engine, tables=[Notification.__table__])
print("notifications 表创建成功")
