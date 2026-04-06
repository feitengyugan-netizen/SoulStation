"""
扫描所有 Vue 文件，找出被损坏的 UTF-8 中文字符（通常表现为 \ufffd? 或 行末尾的 ?）
"""
import os
import glob

base = r'c:\Users\Jiang\Desktop\bs\SoulStation\frontend\src'
vue_files = glob.glob(os.path.join(base, '**', '*.vue'), recursive=True)

issues = {}

for fpath in sorted(vue_files):
    try:
        with open(fpath, encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"ERROR reading {fpath}: {e}")
        continue

    file_issues = []
    for i, line in enumerate(lines, 1):
        stripped = line.rstrip('\n\r')
        # 检测含有替换字符 \ufffd（乱码标志）
        if '\ufffd' in stripped:
            file_issues.append((i, repr(stripped[:120])))
        # 检测属性值引号未闭合：以 ? 结尾且含有 ="（常见损坏模式）
        elif stripped.endswith('?') and '="' in stripped and stripped.count('"') % 2 != 0:
            file_issues.append((i, repr(stripped[:120])))

    if file_issues:
        rel = os.path.relpath(fpath, base)
        issues[rel] = file_issues

if not issues:
    print("✓ 所有 Vue 文件未发现乱码问题")
else:
    print(f"发现 {len(issues)} 个文件存在问题：\n")
    for fname, lns in issues.items():
        print(f"  {fname}:")
        for lineno, content in lns:
            print(f"    Line {lineno}: {content}")
        print()
