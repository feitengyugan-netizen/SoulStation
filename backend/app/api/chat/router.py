"""
聊天路由 - 智能心理问答
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List
import json
from app.core.database import get_db
from app.models.chat import ChatDialogue, ChatMessage
from app.schemas.chat import (
    DialogueCreate, DialogueUpdate, DialogueListResponse,
    DialogueDetailResponse, TagCreate, TagResponse,
    MessageCreate, ChatResponse
)
from app.services.chat_service import chat_service
from app.services.ai_service import ai_service
from app.services.auth_service import AuthService

router = APIRouter(prefix="/chat", tags=["智能问答"])
security = HTTPBearer()


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """从 token 中获取当前用户 ID"""
    from app.core.security import decode_access_token
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )
    return int(user_id)


# ========== 对话管理 ==========

@router.get("/list", summary="获取对话列表")
async def get_dialogue_list(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    获取当前用户的所有对话

    返回对话列表，包含：
    - 对话基本信息
    - 消息数量
    - 最后一条消息预览
    - 关联的标签
    """
    dialogues = chat_service.get_dialogue_list(db, user_id)
    return {
        "code": 200,
        "message": "获取成功",
        "data": dialogues
    }


@router.post("/create", summary="创建新对话")
async def create_dialogue(
    dialogue_data: DialogueCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    创建新的对话

    - **title**: 对话标题（默认"新对话"）
    - **tag_ids**: 关联的标签ID列表（可选）
    """
    dialogue = chat_service.create_dialogue(db, user_id, dialogue_data)
    return {
        "code": 200,
        "message": "创建成功",
        "data": {
            "id": dialogue.id,
            "title": dialogue.title,
            "created_at": dialogue.created_at
        }
    }


# ========== 标签管理（必须在动态路由之前）==========

@router.get("/tags", summary="获取所有标签")
async def get_all_tags(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    获取当前用户创建的所有标签
    """
    tags = chat_service.get_all_tags(db, user_id)
    return {
        "code": 200,
        "message": "获取成功",
        "data": tags
    }


@router.post("/tag", summary="创建标签")
async def create_tag(
    tag_data: TagCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    创建新的标签

    - **name**: 标签名称（1-50字符）
    - **color**: 标签颜色（默认 #1890ff）
    """
    try:
        tag = chat_service.create_tag(db, user_id, tag_data)
        return {
            "code": 200,
            "message": "创建成功",
            "data": {
                "id": tag.id,
                "name": tag.name,
                "color": tag.color
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/tag/{tag_id}", summary="删除标签")
async def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    删除指定标签

    删除标签不会删除对话，只是移除关联关系
    """
    success = chat_service.delete_tag(db, tag_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在或无权访问"
        )
    return {
        "code": 200,
        "message": "删除成功"
    }


# ========== 语音转文字（必须在动态路由之前）==========

@router.post("/voice-to-text", summary="语音转文字")
async def voice_to_text(
    audio_url: str,
    user_id: int = Depends(get_current_user_id)
):
    """
    将语音转换为文字（需要集成第三方语音识别服务）

    - **audio_url**: 音频文件URL

    注意：此功能需要集成语音识别API，如阿里云、腾讯云等
    目前返回默认提示信息
    """
    # TODO: 集成语音识别服务
    return {
        "code": 200,
        "message": "功能待实现",
        "data": {
            "text": "语音转文字功能待实现"
        }
    }


# ========== 动态路由（必须放在最后）==========

@router.get("/{dialogue_id}", summary="获取对话详情")
async def get_dialogue_detail(
    dialogue_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    获取指定对话的详细信息

    包含完整的消息历史和关联的标签
    """
    detail = chat_service.get_dialogue_detail(db, dialogue_id, user_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在或无权访问"
        )
    return {
        "code": 200,
        "message": "获取成功",
        "data": detail
    }


@router.put("/{dialogue_id}/title", summary="更新对话标题")
async def update_dialogue_title(
    dialogue_id: int,
    title: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    更新对话标题

    - **dialogue_id**: 对话ID
    - **title**: 新标题
    """
    dialogue = chat_service.update_dialogue_title(db, dialogue_id, user_id, title)
    if not dialogue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在或无权访问"
        )
    return {
        "code": 200,
        "message": "更新成功",
        "data": {
            "id": dialogue.id,
            "title": dialogue.title
        }
    }


@router.delete("/{dialogue_id}", summary="删除对话")
async def delete_dialogue(
    dialogue_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    删除指定对话（软删除）

    实际上不会真正删除数据，只是标记为已删除
    """
    success = chat_service.delete_dialogue(db, dialogue_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在或无权访问"
        )
    return {
        "code": 200,
        "message": "删除成功"
    }


@router.post("/{dialogue_id}/message", summary="发送消息")
async def send_message(
    dialogue_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    发送消息并获取 AI 回复

    - **dialogue_id**: 对话ID
    - **message**: 用户消息内容

    返回 AI 的回复和消息ID
    """
    try:
        result = chat_service.send_message(db, dialogue_id, user_id, message_data)
        return {
            "code": 200,
            "message": "发送成功",
            "data": {
                "id": result["ai_message"]["id"],
                "content": result["ai_message"]["content"],
                "created_at": result["ai_message"]["created_at"]
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"消息发送失败: {str(e)}"
        )


@router.post("/{dialogue_id}/message/stream", summary="发送消息（流式输出）")
async def send_message_stream(
    dialogue_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    发送消息并获取 AI 回复（流式输出）
    """

    # 验证对话是否存在
    dialogue = db.query(ChatDialogue).filter(
        and_(
            ChatDialogue.id == dialogue_id,
            ChatDialogue.user_id == user_id,
            ChatDialogue.is_deleted == False
        )
    ).first()

    if not dialogue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在或无权访问"
        )

    async def generate():
        try:
            import asyncio

            # 保存用户消息
            user_message = ChatMessage(
                dialogue_id=dialogue_id,
                role="user",
                content=message_data.content
            )
            db.add(user_message)
            db.flush()

            # 获取历史消息
            history_messages = db.query(ChatMessage).filter(
                and_(
                    ChatMessage.dialogue_id == dialogue_id,
                    ChatMessage.is_deleted == False
                )
            ).order_by(desc(ChatMessage.created_at)).limit(10).all()

            # 构建消息列表
            messages_list = [
                {"role": "system", "content": ai_service.generate_system_prompt()}
            ]
            for msg in reversed(history_messages):
                messages_list.append({
                    "role": msg.role,
                    "content": msg.content
                })

            # 添加当前用户消息
            messages_list.append({
                "role": "user",
                "content": message_data.content
            })

            # 调用AI服务获取流式回复
            full_response = ""

            # 使用同步方式调用，然后转换为流式
            try:
                # 调用AI服务（非流式）
                ai_reply = ai_service.chat(messages=messages_list, stream=False)
                full_response = ai_reply

                # 逐字发送，模拟流式效果
                for char in full_response:
                    chunk = f"data: {json.dumps({'content': char, 'done': False}, ensure_ascii=False)}\n\n"
                    yield chunk
                    # 增加延迟，确保前端有时间渲染
                    await asyncio.sleep(0.05)  # 50ms延迟，让流式效果更明显

            except Exception as ai_error:
                print(f"AI调用失败: {ai_error}")
                full_response = f"抱歉，我遇到了一些问题：{str(ai_error)}。请稍后再试。"
                for char in full_response:
                    chunk = f"data: {json.dumps({'content': char, 'done': False}, ensure_ascii=False)}\n\n"
                    yield chunk
                    await asyncio.sleep(0.01)

            # 保存AI回复
            ai_message = ChatMessage(
                dialogue_id=dialogue_id,
                role="assistant",
                content=full_response
            )
            db.add(ai_message)
            db.commit()

            # 发送完成信号
            yield f"data: {json.dumps({'content': '', 'done': True, 'message_id': ai_message.id}, ensure_ascii=False)}\n\n"

        except Exception as e:
            db.rollback()
            print(f"流式生成失败: {e}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'error': str(e), 'done': True}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/{dialogue_id}/tag", summary="为对话添加标签")
async def add_tag_to_dialogue(
    dialogue_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    为指定对话添加标签

    - **dialogue_id**: 对话ID
    - **tag_id**: 标签ID
    """
    success = chat_service.add_tag_to_dialogue(db, dialogue_id, tag_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="对话或标签不存在，或无权访问"
        )
    return {
        "code": 200,
        "message": "添加成功"
    }
