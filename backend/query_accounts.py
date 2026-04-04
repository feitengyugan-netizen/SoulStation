"""
查询数据库中的账号信息
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app.core.database import SessionLocal
    from app.models.user import User
    from app.models.admin import Admin
    from app.models.counselor import Counselor

    db = SessionLocal()

    print('\n' + '='*70)
    print('                    SoulStation 账号信息查询')
    print('='*70)

    # 管理员账号
    print('\n【管理员账号】')
    print('-'*70)
    admins = db.query(Admin).all()
    if admins:
        for admin in admins:
            print(f'用户名: {admin.username}')
            print(f'密码: admin123 (默认密码)')
            print(f'邮箱: {admin.email}')
            print(f'真实姓名: {admin.real_name}')
            print(f'角色: {admin.role}')
            print(f'状态: {"✓ 激活" if admin.is_active else "✗ 未激活"}')
            print('-'*70)
    else:
        print('未找到管理员账号')

    # 普通用户账号
    print('\n【普通用户账号】')
    print('-'*70)
    users = db.query(User).filter(User.role == 'user').all()
    if users:
        for i, user in enumerate(users[:10], 1):
            print(f'{i}. 邮箱: {user.email}')
            print(f'   昵称: {user.nickname}')
            print(f'   密码: 123456 (默认密码)')
            print(f'   状态: {"✓ 激活" if user.is_active else "✗ 未激活"}')
            print('-'*70)
    else:
        print('未找到普通用户账号')

    # 咨询师账号
    print('\n【咨询师账号】')
    print('-'*70)
    counselors = db.query(Counselor).all()
    if counselors:
        for i, counselor in enumerate(counselors[:10], 1):
            user = db.query(User).filter(User.id == counselor.user_id).first()
            print(f'{i}. 姓名: {counselor.name}')
            if user:
                print(f'   关联邮箱: {user.email}')
                print(f'   密码: 123456 (默认密码)')
            print(f'   职称: {counselor.title}')
            print(f'   专长: {counselor.specialties}')
            print(f'   状态: {"✓ 激活" if counselor.status == "active" else "✗ 未激活"}')
            print('-'*70)
    else:
        print('未找到咨询师账号')

    db.close()

except Exception as e:
    print(f'\n错误: {e}')
    print('\n请确保：')
    print('1. 数据库已启动')
    print('2. 后端依赖已安装 (pip install -r requirements.txt)')
    print('3. .env 文件已配置')
