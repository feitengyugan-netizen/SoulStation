"""危机检测模块完整测试"""
from app.services.crisis_service import (
    detect_crisis,
    build_crisis_system_instruction,
    build_crisis_intervention_prompt,
    format_hotline_list,
    get_crisis_level_label,
    is_crisis_detected,
)

# ── 等级检测 ──

# 一级（极高风险）—— 割腕在 CRISIS_LEVEL_1
level, kws = detect_crisis('我想自杀')
assert level == 3, f'自杀level={level}'
assert '自杀' in kws

level, kws = detect_crisis('不想活了，真是活够了')
assert level == 3, f'不想活了level={level}'
assert '不想活了' in kws
assert '活够' in kws

level, kws = detect_crisis('我想割腕')
assert level == 3, f'割腕level={level}'
assert '割腕' in kws

# 二级（高风险）
level, kws = detect_crisis('我感到绝望崩溃')
assert level == 2, f'绝望level={level}'
assert '绝望' in kws or '崩溃' in kws

level, kws = detect_crisis('我快撑不下去了')
assert level == 2, f'撑不下去level={level}'
assert '撑不下去' in kws

# 三级（中风险）
level, kws = detect_crisis('生不如死')
assert level == 1, f'生不如死level={level}'
assert '生不如死' in kws

level, kws = detect_crisis('我想消失')
assert level == 1, f'消失level={level}'
assert '消失' in kws

# 无危机
assert detect_crisis('今天天气不错') == (0, []), '无危机误报'
assert detect_crisis('') == (0, []), '空字符串'
assert detect_crisis('   ') == (0, []), '空白字符串'

# ── 格式化热线 ──
hotlines = format_hotline_list()
assert '400-161-9995' in hotlines, '热线号缺失'
assert '全国心理援助热线' in hotlines, '热线名称缺失'
print(f'✓ format_hotline_list OK: 长度={len(hotlines)}')

# ── 系统指令构建 ──
instr = build_crisis_system_instruction(True)
assert '400-161-9995' in instr, '指令中缺失热线'
assert '危机干预' in instr, '指令标题缺失'
print(f'✓ build_crisis_system_instruction(True) OK: 长度={len(instr)}')

instr_false = build_crisis_system_instruction(False)
assert instr_false == '', '非危机应返回空'
print(f'✓ build_crisis_system_instruction(False) OK')

# ── 干预提示 ──
prompt = build_crisis_intervention_prompt(True)
assert '400-161-9995' in prompt, '干预提示中缺失热线'
print(f'✓ build_crisis_intervention_prompt(True) OK: 长度={len(prompt)}')

prompt_false = build_crisis_intervention_prompt(False)
assert prompt_false == '', '非危机应返回空'
print(f'✓ build_crisis_intervention_prompt(False) OK')

# ── 标签 ──
assert get_crisis_level_label(3) == '一级（极高风险）'
assert get_crisis_level_label(2) == '二级（高风险）'
assert get_crisis_level_label(1) == '三级（中风险）'
assert get_crisis_level_label(0) == '无'
assert get_crisis_level_label(99) == '未知'
print('✓ get_crisis_level_label OK')

# ── 快捷检测 ──
assert is_crisis_detected('我不想活了') == True
assert is_crisis_detected('绝望') == True
assert is_crisis_detected('想死') == True
assert is_crisis_detected('今晚吃什么') == False
assert is_crisis_detected('') == False
print('✓ is_crisis_detected OK')

print('\n✅ 危机检测模块所有测试通过！')
