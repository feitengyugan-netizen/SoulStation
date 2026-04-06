"""
修复两个 Vue 文件的编码问题：
1. ForgotPassword.vue: 整个文件由 GBK 转换为 UTF-8
2. ChatIndex.vue: 修复行末尾损坏的中文字符
"""
import os
import re

BASE = r'c:\Users\Jiang\Desktop\bs\SoulStation\frontend\src'

# ============================================================
# 1. ForgotPassword.vue: GBK → UTF-8
# ============================================================
forgot_path = os.path.join(BASE, r'views\auth\ForgotPassword.vue')

with open(forgot_path, 'rb') as f:
    raw = f.read()

# 尝试以 GBK 解码（windows-1252/gbk）
try:
    content = raw.decode('gbk')
    with open(forgot_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[OK] ForgotPassword.vue: GBK → UTF-8 转换成功")
except Exception as e:
    print(f"[FAIL] ForgotPassword.vue: {e}")

# ============================================================
# 2. ChatIndex.vue: 修复行末尾 ? 代替了最后一个汉字字节
# ============================================================
chat_path = os.path.join(BASE, r'views\chat\ChatIndex.vue')

# 每行的正确修复映射：(损坏的字符串片段, 正确替换)
# 通过上下文推断正确内容
FIXES = [
    # template 注释
    ('<!-- 顶部导航\ufffd', '<!-- 顶部导航栏'),
    ('<!-- 功能按钮\ufffd', '<!-- 功能按钮区'),
    ('<!-- 搜索\ufffd', '<!-- 搜索框'),
    ('<!-- 标签筛\ufffd', '<!-- 标签筛选'),
    ('<!-- 加载\ufffd', '<!-- 加载中'),
    ('<!-- 工具\ufffd', '<!-- 工具栏'),
    ('<!-- 输入\ufffd', '<!-- 输入框'),
    ('<!-- 标签管理对话\ufffd', '<!-- 标签管理对话框'),
    ('<!-- 创建新标\ufffd', '<!-- 创建新标签'),
    # template 内容/属性
    ('换行\ufffd"', '换行）"'),
    ('<h4>创建新标\ufffd/h4>', '<h4>创建新标签</h4>'),
    # script 注释
    ('// 加载状\ufffd', '// 加载状态'),
    ('// 搜索和筛\ufffd', '// 搜索和筛选'),
    ('// 按更新时间排\ufffd', '// 按更新时间排序'),
    ('// 只返回有对话的分\ufffd', '// 只返回有对话的分组'),
    ('// 格式化时\ufffd', '// 格式化时间'),
    ('// 渲染Markdown（简化版\ufffd', '// 渲染Markdown（简化版）'),
    ('// 这里简化处理，实际项目应该使用marked或markdown-it\ufffd', '// 这里简化处理，实际项目应该使用marked或markdown-it库'),
    ('// 如果有对话，默认选择第一\ufffd', '// 如果有对话，默认选择第一个'),
    ('// 创建新对\ufffd', '// 创建新对话'),
    ('// 发送消\ufffd', '// 发送消息'),
    ('// 添加用户消息到列\ufffd', '// 添加用户消息到列表'),
    ('// 创建AI消息占位符（空消息，准备接收流式内容\ufffd', '// 创建AI消息占位符（空消息，准备接收流式内容）'),
    ('// 重要：确保流式传输不被缓\ufffd', '// 重要：确保流式传输不被缓存'),
    ('// 某些浏览器可能需要这\ufffd', '// 某些浏览器可能需要这个'),
    ('// 处理SSE格式的数\ufffd', '// 处理SSE格式的数据'),
    ('// 如果有错\ufffd', '// 如果有错误'),
    ('// 更新消息状\ufffd', '// 更新消息状态'),
    ('// 接收内容并更新UI（打字机效果\ufffd', '// 接收内容并更新UI（打字机效果）'),
    ('// 更新内容（创建新对象以触发Vue更新\ufffd', '// 更新内容（创建新对象以触发Vue更新）'),
    ('// 立即滚动到底\ufffd', '// 立即滚动到底部'),
    ('// 更新对话列表的最后消\ufffd', '// 更新对话列表的最后消息'),
    ('// 滚动到底\ufffd', '// 滚动到底部'),
    ('// 将识别结果填充到输入\ufffd', '// 将识别结果填充到输入框'),
    ('// 返回上一\ufffd', '// 返回上一页'),
    ('// 如果没有历史记录，返回首\ufffd', '// 如果没有历史记录，返回首页'),
    ('// 导出为文\ufffd', '// 导出为文本'),
    ('// ---- 右侧主区\ufffd', '// ---- 右侧主区域 ----'),
    ('// ---- 响应\ufffd', '// ---- 响应式 ----'),
    ('<!-- 标签管理对话框样\ufffd', '<!-- 标签管理对话框样式'),
    # script 字符串/模板
    ("|| '未命名对\ufffd'", "|| '未命名对话'"),
    ("{ label: '今天\ufffd", "{ label: '今天',"),
    ("title: '新对\ufffd'", "title: '新对话'"),
    ("'请输入新的对话标\ufffd", "'请输入新的对话标题'"),
    ("'确定要删除这个对话吗\ufffd'", "'确定要删除这个对话吗？'"),
    ("'流式接收完成，总chunk\ufffd'", "'流式接收完成，总chunk数: '"),
    ("'发送消息失\ufffd'", "'发送消息失败'"),
    ("'发送失败，请重\ufffd'", "'发送失败，请重试'"),
    ("'请输入标签名\ufffd'", "'请输入标签名称'"),
    ("'确定要删除这个标签吗\ufffd'", "'确定要删除这个标签吗？'"),
    ("'对话已导\ufffd'", "'对话已导出'"),
    ("'确定要清空当前对话的所有消息吗？此操作不可恢复\ufffd'", "'确定要清空当前对话的所有消息吗？此操作不可恢复！'"),
    ("'对话已清\ufffd'", "'对话已清空'"),
    # 模板字符串
    ("对话（\ufffd", "对话："),
    ("`对话\ufffd", "`对话标题："),
    ("导出时间\ufffd", "导出时间："),
    # 组件卸载
    ('// 组件卸载\ufffd', '// 组件卸载时'),
]

with open(chat_path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

count = 0
for broken, fixed in FIXES:
    if broken in content:
        content = content.replace(broken, fixed)
        count += 1
        print(f"  修复: {repr(broken[:40])} → {repr(fixed[:40])}")

# 额外修复：行末 \ufffd? 模式（损坏字符 + 字面问号）
# 这种情况下是 \ufffd 后紧跟 ? 的
content = re.sub(r'\ufffd\?', '', content)

with open(chat_path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"\n[OK] ChatIndex.vue: 共修复 {count} 处")

print("\n全部修复完成！")
