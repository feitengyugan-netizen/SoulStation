"""
修复 GBK->UTF-8 mojibake 的 Vue 文件
用法：把 TARGET_FILES 列表中的文件逐一做 encode('gbk').decode('utf-8') 转换
"""
import os
import re

BASE = r'c:\Users\Jiang\Desktop\bs\SoulStation\frontend\src'

TARGET_FILES = [
    r'views\test\TestResult.vue',
]

def fix_mojibake(path):
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # 去掉替换字符
    clean = content.replace('\ufffd', '')

    # encode 为 GBK 恢复原始 UTF-8 字节，再 decode
    try:
        recovered = clean.encode('gbk', errors='ignore').decode('utf-8', errors='replace')
    except Exception as e:
        print(f'[FAIL] {path}: {e}')
        return

    # 修复已知的末尾截断（行尾 ? 替代了最后汉字+引号）
    # pattern: 属性值或字符串结尾 ? 代替了应有的字符
    # 先打印关键行预览
    lines = recovered.split('\n')
    print(f'\n=== {os.path.basename(path)} 前20行预览 ===')
    for i, line in enumerate(lines[:20], 1):
        print(f'{i:3}: {line.rstrip()}')

    # 检查是否还有残留 \ufffd 或行末 ?
    issues = []
    for i, line in enumerate(lines, 1):
        if '\ufffd' in line:
            issues.append(f'  Line {i}: {repr(line.rstrip()[:80])}')
        elif line.rstrip().endswith('?') and ('="' in line or "='" in line) and line.count('"') % 2 != 0:
            issues.append(f'  Line {i}: {repr(line.rstrip()[:80])}')

    if issues:
        print(f'\n残留问题 ({len(issues)} 处):')
        for iss in issues:
            print(iss)
    else:
        print('\n✓ 无残留问题')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(recovered)
    print(f'[OK] {os.path.basename(path)} 写入完成')

for rel in TARGET_FILES:
    full = os.path.join(BASE, rel)
    fix_mojibake(full)
