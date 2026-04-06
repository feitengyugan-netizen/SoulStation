"""
修复 ForgotPassword.vue 的 mojibake 问题：
原始 UTF-8 字节 → 被当作 GBK 读取 → 乱码 Unicode 字符 → 再存为 UTF-8
修复方向：乱码字符 encode('gbk') → 原始字节 decode('utf-8') → 正确中文
"""
import re
import os

BASE = r'c:\Users\Jiang\Desktop\bs\SoulStation\frontend\src'
forgot_path = os.path.join(BASE, r'views\auth\ForgotPassword.vue')

# 读取当前（乱码）UTF-8 内容
with open(forgot_path, 'r', encoding='utf-8', errors='replace') as f:
    garbled = f.read()

# 去掉替换字符 \ufffd（代表损坏字节）
garbled_clean = garbled.replace('\ufffd', '')

# encode 为 GBK 恢复原始 UTF-8 字节，再 decode 为 UTF-8
recovered_bytes = garbled_clean.encode('gbk', errors='ignore')
correct = recovered_bytes.decode('utf-8', errors='replace')

# 打印修复后关键行，供核查
lines = correct.split('\n')
print("=== 修复后关键行预览 ===")
for i, line in enumerate(lines[38:48], start=39):
    print(f"Line {i+1}: {line.rstrip()}")
print()
for i, line in enumerate(lines[138:147], start=139):
    print(f"Line {i+1}: {line.rstrip()}")
print()

# 修复 data-loss 行：行末 ? 替换为正确末尾字符 + 闭合引号
# 这 3 行在 mojibake 过程中最后一个字节丢失，变成 ?
targeted = [
    # 匹配模式（转换后可能出现的残缺内容）                           正确替换
    (r'(placeholder=")([^"]*?)[\?\ufffd]+"?(\s*$)', r'\1\2箱"\3'),         # 请输入注册邮箱
    (r'(title=")([^"]*?)[\?\ufffd]+"?(\s*$)',        r'\1\2功！"\3'),       # 密码重置成功！
    (r'(sub-title=")([^"]*?)[\?\ufffd]+"?(\s*$)',    r'\1\2了"\3'),         # 使用新密码登录了
]

fixed_count = 0
for pattern, repl in targeted:
    new_correct, n = re.subn(pattern, repl, correct, flags=re.MULTILINE)
    if n:
        correct = new_correct
        fixed_count += n
        print(f"  额外修复 {n} 处: {pattern[:40]}")

# 写回文件
with open(forgot_path, 'w', encoding='utf-8') as f:
    f.write(correct)

print(f"\n[OK] ForgotPassword.vue 修复完成（含 {fixed_count} 处末尾字符修复）")
print("\n=== 修复后文件前 30 行 ===")
for i, line in enumerate(lines[:30], start=1):
    print(f"{i:3}: {line.rstrip()}")
