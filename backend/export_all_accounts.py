"""
导出所有测试账号信息到文本文件
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine
from datetime import datetime

def export_accounts_to_file():
    """导出所有账号信息到文件"""
    with engine.connect() as conn:
        # 创建输出文件
        output_dir = "docs"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "所有账号详细信息.txt")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("SoulStation 心理咨询服务平台 - 完整账号信息导出\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"系统状态: 运行中\n")
            f.write("\n" + "=" * 80 + "\n\n")

            # 导出管理员账号
            f.write("[管理员] 管理员账号详细信息\n")
            f.write("-" * 80 + "\n")
            admins = conn.execute(text("""
                SELECT id, username, email, role, created_at
                FROM admins
            """)).fetchall()

            if admins:
                for admin in admins:
                    f.write(f"管理员ID: {admin[0]}\n")
                    f.write(f"用户名: {admin[1]}\n")
                    f.write(f"邮箱: {admin[2]}\n")
                    f.write(f"角色: {admin[3]}\n")
                    f.write(f"创建时间: {admin[4]}\n")
                    f.write(f"登录密码: admin123\n")
                    f.write("\n")
            else:
                f.write("暂无管理员账号\n\n")

            # 导出用户账号
            f.write("\n" + "=" * 80 + "\n")
            f.write("[用户] 用户账号详细信息\n")
            f.write("-" * 80 + "\n")
            users = conn.execute(text("""
                SELECT id, email, nickname, gender,
                       role, status, is_verified, created_at
                FROM users
                WHERE is_deleted = 0
                ORDER BY id
            """)).fetchall()

            f.write(f"用户总数: {len(users)}\n\n")

            for idx, user in enumerate(users, 1):
                f.write(f"【用户 {idx}】\n")
                f.write(f"ID: {user[0]}\n")
                f.write(f"邮箱: {user[1]}\n")
                f.write(f"昵称: {user[2]}\n")
                f.write(f"性别: {user[3]}\n")
                f.write(f"角色: {user[4]}\n")
                f.write(f"状态: {user[5]}\n")
                f.write(f"认证状态: {'已认证' if user[6] else '未认证'}\n")
                f.write(f"注册时间: {user[7]}\n")
                f.write(f"登录密码: 123456\n")
                f.write("\n")

            # 导出咨询师账号
            f.write("\n" + "=" * 80 + "\n")
            f.write("[咨询师] 咨询师账号详细信息\n")
            f.write("-" * 80 + "\n")

            counselors = conn.execute(text("""
                SELECT c.id, c.name, c.title,
                       c.is_verified, c.is_deleted,
                       u.email, c.created_at
                FROM counselors c
                LEFT JOIN users u ON c.user_id = u.id
                ORDER BY c.id
            """)).fetchall()

            active_counselors = [c for c in counselors if not c[4]]
            f.write(f"咨询师总数: {len(active_counselors)}\n\n")

            for idx, counselor in enumerate(active_counselors, 1):
                f.write(f"【咨询师 {idx}】\n")
                f.write(f"ID: {counselor[0]}\n")
                f.write(f"姓名: {counselor[1]}\n")
                f.write(f"职称: {counselor[2]}\n")
                f.write(f"认证状态: {'已认证' if counselor[3] else '待认证'}\n")
                f.write(f"关联邮箱: {counselor[5]}\n")
                f.write(f"注册时间: {counselor[6]}\n")
                f.write(f"登录密码: 123456\n")
                f.write("\n")

            # 添加使用说明
            f.write("\n" + "=" * 80 + "\n")
            f.write("[说明] 账号使用说明\n")
            f.write("-" * 80 + "\n")
            f.write("[登录] 登录地址\n")
            f.write("前端页面: http://localhost:5173\n")
            f.write("登录页面: http://localhost:5173/login\n")
            f.write("管理后台: http://localhost:5173/admin\n")
            f.write("API文档: http://localhost:8000/docs\n\n")

            f.write("[密码] 密码说明\n")
            f.write("所有用户和咨询师密码: 123456\n")
            f.write("管理员密码: admin123\n\n")

            f.write("[角色] 角色识别\n")
            f.write("- 管理员登录 → 跳转到管理后台\n")
            f.write("- 咨询师登录 → 跳转到咨询师工作台\n")
            f.write("- 普通用户登录 → 跳转到用户首页\n\n")

            f.write("[测试] 测试建议\n")
            f.write("1. 用户功能测试: 使用 user1@test.com\n")
            f.write("2. 咨询功能测试: 使用 test@example.com (同时具有用户和咨询师角色)\n")
            f.write("3. 管理功能测试: 使用 admin@soulstation.com\n")
            f.write("4. 视频通话测试: 需要一个用户账号和一个咨询师账号\n\n")

            f.write("=" * 80 + "\n")
            f.write("文档结束 - 祝您使用愉快！\n")
            f.write("=" * 80 + "\n")

        print(f"[SUCCESS] 账号信息已导出到: {output_file}")

        # 同时创建一个CSV格式文件，方便导入到Excel
        csv_file = "docs/账号清单.csv"
        with open(csv_file, 'w', encoding='utf-8-sig') as csv:
            csv.write("类型,邮箱,用户名/姓名,密码,角色,状态,创建时间\n")

            # 管理员
            for admin in admins:
                csv.write(f"管理员,{admin[2]},{admin[1]},admin123,{admin[3]},活跃,{admin[4]}\n")

            # 用户
            for user in users:
                csv.write(f"用户,{user[1]},{user[2]},123456,{user[4]},{user[5]},{user[7]}\n")

            # 咨询师
            for counselor in active_counselors:
                csv.write(f"咨询师,{counselor[5]},{counselor[1]},123456,咨询师,{'已认证' if counselor[3] else '待认证'},{counselor[6]}\n")

        print(f"[SUCCESS] 账号清单已导出到: {csv_file}")

if __name__ == "__main__":
    export_accounts_to_file()