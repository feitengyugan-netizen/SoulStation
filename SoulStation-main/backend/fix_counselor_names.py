#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修正咨询师姓名
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.counselor import Counselor

def fix_counselor_names():
    """修正咨询师姓名"""
    db = SessionLocal()

    try:
        print("=" * 70)
        print("修正咨询师姓名")
        print("=" * 70)

        # 正确的咨询师姓名映射
        correct_names = {
            1: "胡医生",
            2: "王芳",
            3: "李明",
            4: "张静",
            5: "陈刚",
            6: "刘雪"
        }

        print("\n[修正前的姓名]")
        for counselor_id in correct_names.keys():
            counselor = db.query(Counselor).filter(Counselor.id == counselor_id).first()
            if counselor:
                print(f"ID={counselor.id}: {counselor.name}")

        # 修正姓名
        print("\n[开始修正...]")
        for counselor_id, correct_name in correct_names.items():
            counselor = db.query(Counselor).filter(Counselor.id == counselor_id).first()
            if counselor:
                old_name = counselor.name
                if old_name != correct_name:
                    counselor.name = correct_name
                    print(f"ID={counselor.id}: '{old_name}' -> '{correct_name}'")
                else:
                    print(f"ID={counselor.id}: 已正确 ('{correct_name}')")

        db.commit()

        print("\n[修正后的姓名]")
        counselors = db.query(Counselor).filter(
            Counselor.is_deleted == False,
            Counselor.status == 'active'
        ).order_by(Counselor.id).all()

        for c in counselors:
            print(f"ID={c.id}: {c.name} - {c.title}")

        print("\n" + "=" * 70)
        print("[完成] 咨询师姓名修正成功！")
        print("=" * 70)

    except Exception as e:
        print(f"\n[错误] 修正失败: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    fix_counselor_names()
