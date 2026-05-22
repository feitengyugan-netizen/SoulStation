import pymysql
import json
from datetime import datetime

# 连接数据库
connection = pymysql.connect(
    host='localhost',
    port=3307,
    user='root',
    password='123456',
    database='soulstation'
)

# 心理测试数据
psychological_tests = [
    {
        'test_code': 'SAS',
        'title': '焦虑自评量表(Self-Rating Anxiety Scale)',
        'description': '焦虑自评量表用于评定焦虑症状的严重程度，包含20个项目，适用于具有焦虑症状的成年人。',
        'category': 'anxiety',
        'intro_text': '本量表包含20个问题，请根据您最近一周的实际感觉，选择最符合的选项。测试时间约5-10分钟。',
        'total_questions': 20,
        'score_type': 'sum',
        'option_type': '4point',
        'scoring_rules': json.dumps({
            'scoring_method': 'sum',
            'reverse_questions': [5, 9, 13, 17, 19],
            'score_map': {'A': 1, 'B': 2, 'C': 3, 'D': 4},
            'total_max': 80
        }),
        'result_rules': json.dumps({
            'ranges': [
                {'min': 0, 'max': 49, 'level': 'normal', 'title': '正常', 'description': '焦虑水平在正常范围内，心理状态良好。'},
                {'min': 50, 'max': 59, 'level': 'mild', 'title': '轻度焦虑', 'description': '存在轻度焦虑症状，建议注意休息，适当放松。'},
                {'min': 60, 'max': 69, 'level': 'moderate', 'title': '中度焦虑', 'description': '存在中度焦虑症状，建议寻求专业心理咨询。'},
                {'min': 70, 'max': 80, 'level': 'severe', 'title': '重度焦虑', 'description': '存在严重焦虑症状，建议尽快寻求专业心理医疗帮助。'}
            ]
        }),
        'sort_order': 1,
        'is_active': 1,
        'hot_value': 1523,
        'questions': [
            {'number': 1, 'text': '我觉得比平常容易紧张和焦虑', 'dimension': 'anxiety', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 2, 'text': '我无缘无故地感到害怕', 'dimension': 'anxiety', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 3, 'text': '我容易心里烦乱或觉得惊慌', 'dimension': 'anxiety', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 4, 'text': '我觉得我可能将要发疯', 'dimension': 'anxiety', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 5, 'text': '我觉得一切都很好，不会发生什么不幸', 'dimension': 'anxiety', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 6, 'text': '我手脚阵痛和抽筋', 'dimension': 'somatic', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 7, 'text': '我因为头痛、颈痛和背痛而苦恼', 'dimension': 'somatic', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 8, 'text': '我感觉疲乏，容易疲倦', 'dimension': 'somatic', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 9, 'text': '我觉得心平气和，容易安静坐着', 'dimension': 'relaxation', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 10, 'text': '我觉得心跳得很快', 'dimension': 'somatic', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 11, 'text': '我因为一阵阵头晕而苦恼', 'dimension': 'somatic', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 12, 'text': '我有晕倒发作，或觉得要晕倒似的', 'dimension': 'somatic', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 13, 'text': '我吸气呼气都感到很容易', 'dimension': 'somatic', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 14, 'text': '我的手脚麻木和刺痛', 'dimension': 'somatic', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 15, 'text': '我因为胃痛和消化不良而苦恼', 'dimension': 'somatic', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 16, 'text': '我常常要小便', 'dimension': 'somatic', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 17, 'text': '我的手常常是干燥温暖的', 'dimension': 'somatic', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 18, 'text': '我脸红发热', 'dimension': 'somatic', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 19, 'text': '我容易入睡并且一夜睡得很好', 'dimension': 'sleep', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 20, 'text': '我做恶梦', 'dimension': 'sleep', 'is_reverse': 0, 'reverse_value': 0}
        ]
    },
    {
        'test_code': 'SDS',
        'title': '抑郁自评量表(Self-Rating Depression Scale)',
        'description': '抑郁自评量表用于衡量抑郁状态的严重程度，包含20个项目，适用于具有抑郁症状的成年人。',
        'category': 'depression',
        'intro_text': '本量表包含20个问题，请根据您最近一周的实际感觉，选择最符合的选项。每个题目按症状出现频度评分。',
        'total_questions': 20,
        'score_type': 'sum',
        'option_type': '4point',
        'scoring_rules': json.dumps({
            'scoring_method': 'sum',
            'reverse_questions': [2, 5, 6, 11, 12, 14, 16, 17, 18, 20],
            'score_map': {'A': 1, 'B': 2, 'C': 3, 'D': 4},
            'total_max': 80
        }),
        'result_rules': json.dumps({
            'ranges': [
                {'min': 0, 'max': 52, 'level': 'normal', 'title': '正常', 'description': '抑郁水平在正常范围内，心理状态良好。'},
                {'min': 53, 'max': 62, 'level': 'mild', 'title': '轻度抑郁', 'description': '存在轻度抑郁症状，建议多参与社交活动，保持积极心态。'},
                {'min': 63, 'max': 72, 'level': 'moderate', 'title': '中度抑郁', 'description': '存在中度抑郁症状，建议寻求专业心理咨询帮助。'},
                {'min': 73, 'max': 80, 'level': 'severe', 'title': '重度抑郁', 'description': '存在严重抑郁症状，建议尽快寻求专业心理医疗帮助。'}
            ]
        }),
        'sort_order': 2,
        'is_active': 1,
        'hot_value': 1834,
        'questions': [
            {'number': 1, 'text': '我感到情绪沮丧，郁闷', 'dimension': 'mood', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 2, 'text': '我感到早晨心情最好', 'dimension': 'mood', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 3, 'text': '我要哭或想哭', 'dimension': 'mood', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 4, 'text': '我夜间睡眠不好', 'dimension': 'sleep', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 5, 'text': '我吃饭像平时一样多', 'dimension': 'appetite', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 6, 'text': '我的性功能正常', 'dimension': 'physical', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 7, 'text': '我感到体重减轻', 'dimension': 'physical', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 8, 'text': '我为便秘烦恼', 'dimension': 'physical', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 9, 'text': '我的心跳比平时快', 'dimension': 'physical', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 10, 'text': '我感到无故疲劳', 'dimension': 'energy', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 11, 'text': '我的头脑像往常一样清楚', 'dimension': 'cognitive', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 12, 'text': '我做事情像平时一样不感到困难', 'dimension': 'cognitive', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 13, 'text': '我坐卧不安，难以保持平静', 'dimension': 'anxiety', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 14, 'text': '我对未来感到有希望', 'dimension': 'hopelessness', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 15, 'text': '我比平时更容易激怒', 'dimension': 'irritability', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 16, 'text': '我觉得决定什么事很容易', 'dimension': 'cognitive', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 17, 'text': '我感到自己是有用的和不可缺少的人', 'dimension': 'self_worth', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 18, 'text': '我的生活很有意义', 'dimension': 'life_meaning', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 19, 'text': '假若我死了别人会过得更好', 'dimension': 'hopelessness', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 20, 'text': '我仍旧喜爱那些我往常喜爱的东西', 'dimension': 'interest', 'is_reverse': 1, 'reverse_value': 0}
        ]
    },
    {
        'test_code': 'PSQI',
        'title': '匹兹堡睡眠质量指数(Pittsburgh Sleep Quality Index)',
        'description': '匹兹堡睡眠质量指数用于评定被试者最近一个月的睡眠质量，包含7个成分，每个成分按0-3分计分。',
        'category': 'sleep',
        'intro_text': '本量表用于评估您最近一个月的睡眠质量，请根据实际情况回答每个问题。',
        'total_questions': 19,
        'score_type': 'weighted',
        'option_type': 'varied',
        'scoring_rules': json.dumps({
            'scoring_method': 'component_based',
            'components': 7,
            'component_scoring': '0-3分制',
            'total_max': 21
        }),
        'result_rules': json.dumps({
            'ranges': [
                {'min': 0, 'max': 5, 'level': 'good', 'title': '睡眠质量很好', 'description': '您的睡眠质量很好，继续保持良好的睡眠习惯。'},
                {'min': 6, 'max': 10, 'level': 'fair', 'title': '睡眠质量较好', 'description': '您的睡眠质量尚可，但仍有改善空间。'},
                {'min': 11, 'max': 15, 'level': 'poor', 'title': '睡眠质量一般', 'description': '您存在睡眠问题，建议改善睡眠卫生习惯。'},
                {'min': 16, 'max': 21, 'level': 'bad', 'title': '睡眠质量很差', 'description': '您存在严重睡眠问题，建议寻求专业帮助。'}
            ]
        }),
        'sort_order': 3,
        'is_active': 1,
        'hot_value': 987,
        'questions': [
            {'number': 1, 'text': '近1个月，您晚上上床睡觉通常在几点钟？', 'dimension': 'sleep_schedule', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 2, 'text': '近1个月，您从上床到入睡通常需要多少分钟？', 'dimension': 'sleep_latency', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 3, 'text': '近1个月，您早上通常起床的时间是？', 'dimension': 'sleep_schedule', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 4, 'text': '近1个月，您每晚实际睡眠时间（不等于卧床时间）是多少小时？', 'dimension': 'sleep_duration', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 5, 'text': '近1个月，您是否因以下情况影响睡眠而烦恼：a. 入睡困难（30分钟内不能入睡）', 'dimension': 'sleep_disturbance', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 6, 'text': '近1个月，您是否因以下情况影响睡眠而烦恼：b. 夜间或凌晨易醒或早醒', 'dimension': 'sleep_disturbance', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 7, 'text': '近1个月，您是否因以下情况影响睡眠而烦恼：c. 夜间上厕所', 'dimension': 'sleep_disturbance', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 8, 'text': '近1个月，您是否因以下情况影响睡眠而烦恼：d. 呼吸不畅或咳嗽', 'dimension': 'sleep_disturbance', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 9, 'text': '近1个月，您是否因以下情况影响睡眠而烦恼：e. 感觉太冷或太热', 'dimension': 'sleep_disturbance', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 10, 'text': '近1个月，您是否因以下情况影响睡眠而烦恼：f. 做恶梦', 'dimension': 'sleep_disturbance', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 11, 'text': '近1个月，您是否因以下情况影响睡眠而烦恼：g. 身体疼痛不适', 'dimension': 'sleep_disturbance', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 12, 'text': '近1个月，您是否因其他问题影响睡眠而烦恼', 'dimension': 'sleep_disturbance', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 13, 'text': '近1个月，您如何评价自己的睡眠质量？', 'dimension': 'sleep_quality', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 14, 'text': '近1个月，您是否因以下情况而困扰：a. 即使没喝酒也感到头痛', 'dimension': 'daytime_dysfunction', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 15, 'text': '近1个月，您是否因以下情况而困扰：b. 感到困倦或精力不足', 'dimension': 'daytime_dysfunction', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 16, 'text': '近1个月，您在驾车、吃饭或参加社会活动时是否感到困倦？', 'dimension': 'daytime_dysfunction', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 17, 'text': '近1个月，您在在积极参与日常活动时是否感到精力不足？', 'dimension': 'daytime_dysfunction', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 18, 'text': '近1个月，您与室友、同事或家人的睡眠质量相比如何？', 'dimension': 'sleep_quality_comparison', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 19, 'text': '您对自己当前的睡眠质量是否满意？', 'dimension': 'sleep_satisfaction', 'is_reverse': 0, 'reverse_value': 0}
        ]
    },
    {
        'test_code': 'BIG_FIVE',
        'title': '大五人格测试(简版)',
        'description': '基于大五人格理论的心理测试，评估开放性、尽责性、外向性、宜人性、神经质五个维度。',
        'category': 'personality',
        'intro_text': '本测试包含25个问题，请根据您的真实情况，选择最符合的选项。测试时间约10分钟。',
        'total_questions': 25,
        'score_type': 'dimensional',
        'option_type': '5point',
        'scoring_rules': json.dumps({
            'scoring_method': 'dimensional',
            'dimensions': ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism'],
            'questions_per_dimension': 5,
            'score_map': {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5},
            'reverse_questions': {
                'openness': [],
                'conscientiousness': [8, 18, 23],
                'extraversion': [6, 11, 16],
                'agreeableness': [9, 14, 24],
                'neuroticism': [5, 10, 15, 20, 25]
            }
        }),
        'result_rules': json.dumps({
            'dimension_ranges': [
                {'min': 5, 'max': 15, 'level': 'low', 'title': '较低', 'description': '在该维度上表现较低'},
                {'min': 16, 'max': 20, 'level': 'medium', 'title': '中等', 'description': '在该维度上表现中等'},
                {'min': 21, 'max': 25, 'level': 'high', 'title': '较高', 'description': '在该维度上表现较高'}
            ],
            'dimension_descriptions': {
                'openness': '开放性：想象力、创造力、好奇心',
                'conscientiousness': '尽责性：自律性、组织性、可靠性',
                'extraversion': '外向性：社交性、活力、积极情绪',
                'agreeableness': '宜人性：友善性、合作性、信任度',
                'neuroticism': '神经质：情绪稳定性、焦虑倾向、敏感度'
            }
        }),
        'sort_order': 4,
        'is_active': 1,
        'hot_value': 2156,
        'questions': [
            {'number': 1, 'text': '我是一个富有想象力的人', 'dimension': 'openness', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 2, 'text': '我对艺术和美有很强的鉴赏力', 'dimension': 'openness', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 3, 'text': '我喜欢新奇的事物和体验', 'dimension': 'openness', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 4, 'text': '我经常思考抽象的概念', 'dimension': 'openness', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 5, 'text': '我很少担忧', 'dimension': 'neuroticism', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 6, 'text': '我更喜欢安静独处', 'dimension': 'extraversion', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 7, 'text': '我喜欢成为关注的焦点', 'dimension': 'extraversion', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 8, 'text': '我经常把事情留到最后一刻', 'dimension': 'conscientiousness', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 9, 'text': '我经常批评别人', 'dimension': 'agreeableness', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 10, 'text': '我容易感到紧张', 'dimension': 'neuroticism', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 11, 'text': '我不喜欢大型聚会', 'dimension': 'extraversion', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 12, 'text': '我对他人的感受很敏感', 'dimension': 'agreeableness', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 13, 'text': '我总是准备充分', 'dimension': 'conscientiousness', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 14, 'text': '我有时候利用别人', 'dimension': 'agreeableness', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 15, 'text': '我很少感到情绪低落', 'dimension': 'neuroticism', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 16, 'text': '我很少主动与人交谈', 'dimension': 'extraversion', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 17, 'text': '我喜欢尝试新的活动和爱好', 'dimension': 'openness', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 18, 'text': '我的物品经常凌乱不堪', 'dimension': 'conscientiousness', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 19, 'text': '我同情他人的感受', 'dimension': 'agreeableness', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 20, 'text': '我经常感到焦虑', 'dimension': 'neuroticism', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 21, 'text': '我喜欢哲学和理论讨论', 'dimension': 'openness', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 22, 'text': '我做事很有计划性', 'dimension': 'conscientiousness', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 23, 'text': '我经常忘记归还借来的东西', 'dimension': 'conscientiousness', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 24, 'text': '我有时显得冷漠无情', 'dimension': 'agreeableness', 'is_reverse': 1, 'reverse_value': 0},
            {'number': 25, 'text': '我容易情绪激动', 'dimension': 'neuroticism', 'is_reverse': 0, 'reverse_value': 0}
        ]
    },
    {
        'test_code': 'STRESS',
        'title': '压力水平测试',
        'description': '评估您当前的压力水平和压力应对能力，帮助了解自己的压力状况。',
        'category': 'stress',
        'intro_text': '本测试包含15个问题，请根据您最近一个月的实际情况，选择最符合的选项。',
        'total_questions': 15,
        'score_type': 'sum',
        'option_type': '5point',
        'scoring_rules': json.dumps({
            'scoring_method': 'sum',
            'reverse_questions': [],
            'score_map': {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5},
            'total_max': 75
        }),
        'result_rules': json.dumps({
            'ranges': [
                {'min': 0, 'max': 25, 'level': 'low', 'title': '压力水平较低', 'description': '您的压力水平在正常范围内，压力管理能力良好。'},
                {'min': 26, 'max': 40, 'level': 'moderate', 'title': '压力水平适中', 'description': '您有一定的压力，但在可控范围内。建议适当放松。'},
                {'min': 41, 'max': 55, 'level': 'high', 'title': '压力水平较高', 'description': '您的压力水平偏高，建议学习压力管理技巧。'},
                {'min': 56, 'max': 75, 'level': 'severe', 'title': '压力水平很高', 'description': '您的压力水平很高，建议寻求专业心理咨询帮助。'}
            ]
        }),
        'sort_order': 5,
        'is_active': 1,
        'hot_value': 1342,
        'questions': [
            {'number': 1, 'text': '我感到被工作或学习压得喘不过气', 'dimension': 'work_stress', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 2, 'text': '我经常感到时间不够用', 'dimension': 'time_pressure', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 3, 'text': '我难以集中注意力完成任务', 'dimension': 'concentration', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 4, 'text': '我经常感到疲劳或精力不足', 'dimension': 'physical', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 5, 'text': '我容易发脾气或情绪波动', 'dimension': 'emotional', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 6, 'text': '我的睡眠质量受到影响', 'dimension': 'sleep', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 7, 'text': '我对未来感到担忧', 'dimension': 'worry', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 8, 'text': '我经常感到紧张或不安', 'dimension': 'anxiety', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 9, 'text': '我难以享受日常生活', 'dimension': 'enjoyment', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 10, 'text': '我的人际关系受到影响', 'dimension': 'relationships', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 11, 'text': '我经常头痛或身体不适', 'dimension': 'physical_symptoms', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 12, 'text': '我感到孤独或缺乏支持', 'dimension': 'social_support', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 13, 'text': '我觉得事情总是出问题', 'dimension': 'pessimism', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 14, 'text': '我难以做出决定', 'dimension': 'decision_making', 'is_reverse': 0, 'reverse_value': 0},
            {'number': 15, 'text': '我觉得失去对生活的控制', 'dimension': 'control', 'is_reverse': 0, 'reverse_value': 0}
        ]
    }
]

try:
    with connection.cursor() as cursor:
        print("开始插入心理测试数据...\n")

        for test in psychological_tests:
            # 插入测试基本信息
            test_sql = """
                INSERT INTO psychological_tests (
                    test_code, title, description, category, intro_text,
                    total_questions, score_type, option_type, scoring_rules,
                    result_rules, sort_order, is_active, hot_value,
                    created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                )
            """

            cursor.execute(test_sql, (
                test['test_code'],
                test['title'],
                test['description'],
                test['category'],
                test['intro_text'],
                test['total_questions'],
                test['score_type'],
                test['option_type'],
                test['scoring_rules'],
                test['result_rules'],
                test['sort_order'],
                test['is_active'],
                test['hot_value']
            ))

            test_id = cursor.lastrowid
            print(f"已插入测试: {test['title']} (ID: {test_id}, 代码: {test['test_code']})")

            # 插入测试问题
            for question in test['questions']:
                # 根据选项类型生成选项
                if test['option_type'] == '4point':
                    options = {
                        'A': '没有或很少时间',
                        'B': '小部分时间',
                        'C': '相当多时间',
                        'D': '绝大部分或全部时间'
                    }
                elif test['option_type'] == '5point':
                    options = {
                        'A': '非常不同意',
                        'B': '不同意',
                        'C': '中立',
                        'D': '同意',
                        'E': '非常同意'
                    }
                else:
                    options = {
                        'A': '选项A',
                        'B': '选项B',
                        'C': '选项C',
                        'D': '选项D'
                    }

                question_sql = """
                    INSERT INTO test_questions (
                        test_id, question_number, question_text, options,
                        dimension, is_reverse, reverse_value, sort_order, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """

                cursor.execute(question_sql, (
                    test_id,
                    question['number'],
                    question['text'],
                    json.dumps(options),
                    question['dimension'],
                    question['is_reverse'],
                    question['reverse_value'],
                    question['number']
                ))

            print(f"  - 已插入 {len(test['questions'])} 个问题")

        connection.commit()
        print(f"\n成功插入 {len(psychological_tests)} 个心理测试!")

        # 验证插入结果
        cursor.execute('SELECT COUNT(*) FROM psychological_tests')
        total_tests = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM test_questions')
        total_questions = cursor.fetchone()[0]

        print(f"数据库中测试总数: {total_tests}")
        print(f"数据库中问题总数: {total_questions}")

        # 显示测试列表
        print("\n=== 心理测试列表 ===")
        cursor.execute('''
            SELECT id, test_code, title, category, total_questions, hot_value
            FROM psychological_tests
            ORDER BY sort_order
        ''')
        tests = cursor.fetchall()

        for test in tests:
            print(f"ID: {test[0]} | 代码: {test[1]:10s} | {test[2][:30]:30s} | 分类: {test[3]:15s} | 问题数: {test[4]:2d} | 热度: {test[5]}")

        # 分类统计
        print("\n=== 分类统计 ===")
        cursor.execute('SELECT category, COUNT(*) FROM psychological_tests GROUP BY category')
        categories = cursor.fetchall()
        for cat, count in categories:
            print(f"  {cat}: {count} 个测试")

finally:
    connection.close()
