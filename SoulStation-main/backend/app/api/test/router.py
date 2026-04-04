"""
心理测试 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user, get_current_user_optional
from app.models.user import User
from app.models.test import TestResult, PsychologicalTest
from app.schemas.test import (
    TestListQuery, StartTestRequest, SaveProgressRequest, SubmitTestRequest,
    FavoriteResultRequest, GetTrendRequest,
    TestListItemSchema, TestDetailSchema, StartTestResponseSchema,
    TestResultSchema, TestHistoryItemSchema, TestHistoryResponseSchema,
    TestTrendResponseSchema, ApiResponse
)
from app.services.test_service import TestService
from app.services.ai_service import AIService
from app.services.chat_service import chat_service

router = APIRouter(prefix="/test", tags=["心理测试"])


@router.get("/list", response_model=ApiResponse)
async def get_test_list(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    category: Optional[str] = Query(None, description="分类筛选"),
    sort: Optional[str] = Query("latest", description="排序方式"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    获取测试列表

    支持按关键词搜索、分类筛选、排序（热度/最新/评分）
    """
    query = TestListQuery(
        keyword=keyword,
        category=category,
        sort=sort,
        page=page,
        page_size=page_size
    )

    result = TestService.get_test_list(db, query)

    # Service 层已经返回了包含统计数据的数据，直接使用
    items_data = result["items"]

    return ApiResponse(
        code=200,
        message="成功",
        data={
            "total": result["total"],
            "items": items_data,
            "page": page,
            "page_size": page_size
        }
    )


@router.get("/history", response_model=ApiResponse)
async def get_test_history(
    test_id: Optional[int] = Query(None, description="筛选特定测试"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户测试历史

    支持按测试ID筛选、分页查询
    """
    result = TestService.get_test_history(db, current_user.id, test_id, page, page_size)

    items_data = [
        {
            "id": item.id,
            "test_id": item.test_id,
            "test_code": item.test_code,
            "test_title": item.test_title,
            "total_score": item.total_score,
            "result_level": item.result_level,
            "result_title": item.result_title,
            "is_favorite": item.is_favorite,
            "created_at": item.created_at.isoformat()
        }
        for item in result["items"]
    ]

    return ApiResponse(
        code=200,
        message="成功",
        data={
            "total": result["total"],
            "items": items_data
        }
    )


@router.get("/{test_id}", response_model=ApiResponse)
async def get_test_detail(
    test_id: int,
    db: Session = Depends(get_db)
):
    """
    获取测试详情

    返回测试的基本信息、计分规则、结果解读规则等
    """
    test = TestService.get_test_detail(db, test_id)

    if not test:
        raise HTTPException(status_code=404, detail="测试不存在")

    return ApiResponse(
        code=200,
        message="成功",
        data={
            "id": test.id,
            "test_code": test.test_code,
            "title": test.title,
            "description": test.description,
            "category": test.category,
            "intro_text": test.intro_text,
            "total_questions": test.total_questions,
            "score_type": test.score_type,
            "option_type": test.option_type,
            "scoring_rules": test.scoring_rules,
            "result_rules": test.result_rules
        }
    )


@router.post("/{test_id}/start", response_model=ApiResponse)
async def start_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    开始测试

    返回测试题目列表
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="请先登录")

    result = TestService.start_test(db, test_id, current_user.id)

    if not result:
        raise HTTPException(status_code=404, detail="测试不存在")

    return ApiResponse(
        code=200,
        message="成功",
        data=result
    )


@router.post("/{test_id}/progress", response_model=ApiResponse)
async def save_progress(
    test_id: int,
    request: SaveProgressRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    保存答题进度

    支持断点续答功能
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="请先登录")

    success = TestService.save_progress(db, current_user.id, test_id, request)

    if success:
        return ApiResponse(code=200, message="进度保存成功")
    else:
        raise HTTPException(status_code=500, detail="保存失败")


@router.post("/{test_id}/submit", response_model=ApiResponse)
async def submit_test(
    test_id: int,
    request: SubmitTestRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    提交测试答案

    自动计算分数并生成结果解读
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="请先登录")

    result = TestService.submit_test(db, current_user.id, test_id, request)

    if not result:
        raise HTTPException(status_code=404, detail="测试不存在")

    return ApiResponse(
        code=200,
        message="测试完成",
        data={
            "id": result.id,
            "test_id": result.test_id,
            "test_code": result.test_code,
            "test_title": result.test_title,
            "total_score": result.total_score,
            "dimension_scores": result.dimension_scores,
            "result_level": result.result_level,
            "result_title": result.result_title,
            "result_description": result.result_description,
            "suggestions": result.suggestions,
            "ai_suggestion": result.ai_suggestion,
            "is_favorite": result.is_favorite,
            "created_at": result.created_at.isoformat()
        }
    )


@router.get("/result/{result_id}", response_model=ApiResponse)
async def get_test_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    获取测试结果详情
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="请先登录")

    result = TestService.get_test_result(db, result_id, current_user.id)

    if not result:
        raise HTTPException(status_code=404, detail="结果不存在")

    return ApiResponse(
        code=200,
        message="成功",
        data={
            "id": result.id,
            "test_id": result.test_id,
            "test_code": result.test_code,
            "test_title": result.test_title,
            "total_score": result.total_score,
            "dimension_scores": result.dimension_scores,
            "result_level": result.result_level,
            "result_title": result.result_title,
            "result_description": result.result_description,
            "suggestions": result.suggestions,
            "ai_suggestion": result.ai_suggestion,
            "is_favorite": result.is_favorite,
            "created_at": result.created_at.isoformat()
        }
    )


@router.get("/{test_id}/trend", response_model=ApiResponse)
async def get_test_trend(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    获取测试趋势数据

    返回用户在该测试下的历史分数变化，用于图表展示
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="请先登录")

    result = TestService.get_test_trend(db, current_user.id, test_id)

    if not result:
        raise HTTPException(status_code=404, detail="测试不存在")

    return ApiResponse(
        code=200,
        message="成功",
        data=result
    )


@router.post("/result/{result_id}/favorite", response_model=ApiResponse)
async def favorite_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    收藏/取消收藏测试结果
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="请先登录")

    result = TestService.toggle_favorite(db, result_id, current_user.id)

    if not result:
        raise HTTPException(status_code=404, detail="结果不存在")

    return ApiResponse(
        code=200,
        message="收藏状态已更新",
        data={
            "is_favorite": result.is_favorite
        }
    )


@router.delete("/result/{result_id}/favorite", response_model=ApiResponse)
async def unfavorite_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    取消收藏测试结果
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="请先登录")

    result = TestService.toggle_favorite(db, result_id, current_user.id)

    if not result:
        raise HTTPException(status_code=404, detail="结果不存在")

    return ApiResponse(
        code=200,
        message="已取消收藏",
        data={
            "is_favorite": result.is_favorite
        }
    )


@router.get("/{test_id}/progress", response_model=ApiResponse)
async def get_progress(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    获取答题进度

    用于断点续答功能
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="请先登录")

    progress = TestService.get_progress(db, current_user.id, test_id)

    if not progress:
        return ApiResponse(
            code=200,
            message="暂无进度记录",
            data=None
        )

    return ApiResponse(
        code=200,
        message="成功",
        data={
            "answers": progress.answers,
            "current_question": progress.current_question,
            "updated_at": progress.updated_at.isoformat()
        }
    )


@router.post("/{result_id}/ai-chat", response_model=ApiResponse)
async def create_ai_chat_from_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    从测试结果创建AI深度咨询对话

    基于用户的测试结果创建一个新的AI对话，并自动带入测试上下文信息
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="请先登录")

    # 获取测试结果
    result = db.query(TestResult).filter(
        and_(
            TestResult.id == result_id,
            TestResult.user_id == current_user.id
        )
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="测试结果不存在")

    # 获取测试信息
    test = db.query(PsychologicalTest).filter(
        PsychologicalTest.id == result.test_id
    ).first()

    if not test:
        raise HTTPException(status_code=404, detail="测试不存在")

    # 构建测试上下文信息
    context_info = f"""用户测试结果上下文：

【测试名称】{test.title}
【测试得分】{result.total_score}分
【测试等级】{result.result_level}
【测试描述】{result.result_description or '无'}
"""

    # 添加维度信息
    if result.dimension_scores:
        context_info += "\n【各维度得分】\n"
        for dim in result.dimension_scores:
            context_info += f"- {dim.get('dimension', '未知')}: {dim.get('score', 0)}分\n"

    # 构建对话标题
    dialogue_title = f"{test.title} - AI深度咨询"

    try:
        # 创建新对话
        from app.schemas.chat import DialogueCreate

        dialogue_data = DialogueCreate(
            title=dialogue_title,
            tag_ids=[]
        )

        dialogue = chat_service.create_dialogue(db, current_user.id, dialogue_data)

        # 发送第一条消息
        from app.schemas.chat import MessageCreate

        system_message = f"""您好！我是您的心理咨询师小宁。

我注意到您刚刚完成了《{test.title}》测试，以下是您的测试结果：

{context_info}

我们可以一起探讨这个结果，我会尽力为您提供专业的心理支持和建议。请告诉我您现在最想了解什么？"""

        message_data = MessageCreate(
            message=system_message,
            is_ai=True
        )

        chat_service.send_message(db, dialogue.id, current_user.id, message_data)

        return ApiResponse(
            code=200,
            message="创建成功",
            data={
                "dialogue_id": dialogue.id,
                "dialogue_title": dialogue.title,
                "test_id": result.test_id,
                "result_id": result_id,
                "redirect_url": f"/chat/{dialogue.id}"
            }
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"创建AI对话失败: {str(e)}"
        )
