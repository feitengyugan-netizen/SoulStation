"""检查咨询师和用户账号关联"""
from app.core.database import SessionLocal
from app.models.counselor import Counselor
from app.models.user import User

db = SessionLocal()

print("=" * 60)
print("咨询师列表")
print("=" * 60)

counselors = db.query(Counselor).all()
print(f"\n总共: {len(counselors)} 个咨询师\n")

for c in counselors:
    print(f"ID: {c.id}")
    print(f"  姓名: {c.name}")
    print(f"  User_ID: {c.user_id}")
    print(f"  状态: {c.status}")

    # 检查是否有对应的User账号
    if c.user_id:
        user = db.query(User).filter(User.id == c.user_id).first()
        if user:
            print(f"  ✅ 账号存在: {user.email}, 角色: {user.role}")
        else:
            print(f"  ❌ 账号不存在! user_id={c.user_id} 找不到对应的User记录")
    else:
        print(f"  ❌ 没有关联User账号!")
    print()

print("=" * 60)
print("检查结果汇总")
print("=" * 60)

no_account = [c for c in counselors if not c.user_id]
invalid_ref = [c for c in counselors if c.user_id and not db.query(User).filter(User.id == c.user_id).first()]

print(f"\n没有user_id的咨询师: {len(no_account)} 个")
print(f"user_id无效的咨询师: {len(invalid_ref)} 个")
print(f"需要创建账号的咨询师: {len(no_account) + len(invalid_ref)} 个")

db.close()
