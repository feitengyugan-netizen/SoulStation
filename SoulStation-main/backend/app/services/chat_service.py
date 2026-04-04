"""
聊天服务 - 业务逻辑层
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from typing import List, Optional
from datetime import datetime

from app.models.chat import ChatDialogue, ChatMessage, ChatTag, ChatDialogueTag
from app.models.user import User
from app.schemas.chat import (
    DialogueCreate, DialogueUpdate, TagCreate, MessageCreate
)
from app.services.ai_service import ai_service


class ChatService:
    """聊天服务类"""

    # ========== 对话管理 ==========
    @staticmethod
    def get_dialogue_list(db: Session, user_id: int) -> List[dict]:
        """
        获取用户的对话列表

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            List[dict]: 对话列表
        """
        dialogues = db.query(ChatDialogue).filter(
            and_(
                ChatDialogue.user_id == user_id,
                ChatDialogue.is_deleted == False
            )
        ).order_by(desc(ChatDialogue.updated_at)).all()

        result = []
        for dialogue in dialogues:
            # 获取消息数量
            message_count = db.query(func.count(ChatMessage.id)).filter(
                and_(
                    ChatMessage.dialogue_id == dialogue.id,
                    ChatMessage.is_deleted == False
                )
            ).scalar() or 0

            # 获取最后一条消息
            last_message = db.query(ChatMessage).filter(
                and_(
                    ChatMessage.dialogue_id == dialogue.id,
                    ChatMessage.is_deleted == False
                )
            ).order_by(desc(ChatMessage.created_at)).first()

            # 获取标签
            tags = db.query(ChatTag).join(
                ChatDialogueTag,
                ChatDialogueTag.tag_id == ChatTag.id
            ).filter(
                ChatDialogueTag.dialogue_id == dialogue.id
            ).all()

            result.append({
                "id": dialogue.id,
                "title": dialogue.title,
                "created_at": dialogue.created_at,
                "updated_at": dialogue.updated_at,
                "message_count": message_count,
                "tags": [{"id": tag.id, "name": tag.name, "color": tag.color} for tag in tags],
                "last_message": last_message.content[:50] + "..." if last_message and len(last_message.content) > 50 else (last_message.content if last_message else None)
            })

        return result

    @staticmethod
    def get_dialogue_detail(db: Session, dialogue_id: int, user_id: int) -> Optional[dict]:
        """
        获取对话详情

        Args:
            db: 数据库会话
            dialogue_id: 对话ID
            user_id: 用户ID

        Returns:
            Optional[dict]: 对话详情
        """
        dialogue = db.query(ChatDialogue).filter(
            and_(
                ChatDialogue.id == dialogue_id,
                ChatDialogue.user_id == user_id,
                ChatDialogue.is_deleted == False
            )
        ).first()

        if not dialogue:
            return None

        # 获取消息列表
        messages = db.query(ChatMessage).filter(
            and_(
                ChatMessage.dialogue_id == dialogue_id,
                ChatMessage.is_deleted == False
            )
        ).order_by(ChatMessage.created_at).all()

        # 获取标签
        tags = db.query(ChatTag).join(
            ChatDialogueTag,
            ChatDialogueTag.tag_id == ChatTag.id
        ).filter(
            ChatDialogueTag.dialogue_id == dialogue_id
        ).all()

        return {
            "id": dialogue.id,
            "user_id": dialogue.user_id,
            "title": dialogue.title,
            "created_at": dialogue.created_at,
            "updated_at": dialogue.updated_at,
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at
                }
                for msg in messages
            ],
            "tags": [{"id": tag.id, "name": tag.name, "color": tag.color} for tag in tags]
        }

    @staticmethod
    def create_dialogue(db: Session, user_id: int, dialogue_data: DialogueCreate) -> ChatDialogue:
        """
        创建新对话

        Args:
            db: 数据库会话
            user_id: 用户ID
            dialogue_data: 对话数据

        Returns:
            ChatDialogue: 创建的对话对象
        """
        # 创建对话
        dialogue = ChatDialogue(
            user_id=user_id,
            title=dialogue_data.title
        )
        db.add(dialogue)
        db.flush()  # 获取 dialogue.id

        # 关联标签
        if dialogue_data.tag_ids:
            for tag_id in dialogue_data.tag_ids:
                # 检查标签是否存在且属于该用户
                tag = db.query(ChatTag).filter(
                    and_(
                        ChatTag.id == tag_id,
                        ChatTag.user_id == user_id,
                        ChatTag.is_deleted == False
                    )
                ).first()
                if tag:
                    dialogue_tag = ChatDialogueTag(
                        dialogue_id=dialogue.id,
                        tag_id=tag_id
                    )
                    db.add(dialogue_tag)

        db.commit()
        db.refresh(dialogue)
        return dialogue

    @staticmethod
    def update_dialogue_title(db: Session, dialogue_id: int, user_id: int, title: str) -> Optional[ChatDialogue]:
        """
        更新对话标题

        Args:
            db: 数据库会话
            dialogue_id: 对话ID
            user_id: 用户ID
            title: 新标题

        Returns:
            Optional[ChatDialogue]: 更新后的对话对象
        """
        dialogue = db.query(ChatDialogue).filter(
            and_(
                ChatDialogue.id == dialogue_id,
                ChatDialogue.user_id == user_id,
                ChatDialogue.is_deleted == False
            )
        ).first()

        if not dialogue:
            return None

        dialogue.title = title
        db.commit()
        db.refresh(dialogue)
        return dialogue

    @staticmethod
    def delete_dialogue(db: Session, dialogue_id: int, user_id: int) -> bool:
        """
        删除对话（软删除）

        Args:
            db: 数据库会话
            dialogue_id: 对话ID
            user_id: 用户ID

        Returns:
            bool: 是否删除成功
        """
        dialogue = db.query(ChatDialogue).filter(
            and_(
                ChatDialogue.id == dialogue_id,
                ChatDialogue.user_id == user_id,
                ChatDialogue.is_deleted == False
            )
        ).first()

        if not dialogue:
            return False

        dialogue.is_deleted = True
        db.commit()
        return True

    # ========== 消息管理 ==========
    @staticmethod
    def send_message(db: Session, dialogue_id: int, user_id: int, message_data: MessageCreate) -> dict:
        """
        发送消息并获取 AI 回复

        Args:
            db: 数据库会话
            dialogue_id: 对话ID
            user_id: 用户ID
            message_data: 消息数据

        Returns:
            dict: 包含用户消息和 AI 回复的字典
        """
        # 验证对话是否属于该用户
        dialogue = db.query(ChatDialogue).filter(
            and_(
                ChatDialogue.id == dialogue_id,
                ChatDialogue.user_id == user_id,
                ChatDialogue.is_deleted == False
            )
        ).first()

        if not dialogue:
            raise ValueError("对话不存在或无权访问")

        # 保存用户消息
        user_message = ChatMessage(
            dialogue_id=dialogue_id,
            role="user",
            content=message_data.content
        )
        db.add(user_message)
        db.flush()

        # 获取历史消息（最近10条）
        history_messages = db.query(ChatMessage).filter(
            and_(
                ChatMessage.dialogue_id == dialogue_id,
                ChatMessage.is_deleted == False
            )
        ).order_by(desc(ChatMessage.created_at)).limit(10).all()

        # 构建消息列表（按时间正序）
        messages_list = [
            {"role": "system", "content": ai_service.generate_system_prompt()}
        ]
        for msg in reversed(history_messages):
            messages_list.append({
                "role": msg.role,
                "content": msg.content
            })

        # 调用 AI 服务获取回复
        try:
            ai_reply = ai_service.chat(messages=messages_list, stream=False)
        except Exception as e:
            ai_reply = f"抱歉，我遇到了一些问题：{str(e)}。请稍后再试。"

        # 保存 AI 回复
        ai_message = ChatMessage(
            dialogue_id=dialogue_id,
            role="assistant",
            content=ai_reply
        )
        db.add(ai_message)
        db.commit()

        return {
            "user_message": {
                "id": user_message.id,
                "role": "user",
                "content": user_message.content,
                "created_at": user_message.created_at
            },
            "ai_message": {
                "id": ai_message.id,
                "role": "assistant",
                "content": ai_message.content,
                "created_at": ai_message.created_at
            }
        }

    # ========== 标签管理 ==========
    @staticmethod
    def get_all_tags(db: Session, user_id: int) -> List[ChatTag]:
        """
        获取用户的所有标签

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            List[ChatTag]: 标签列表
        """
        return db.query(ChatTag).filter(
            and_(
                ChatTag.user_id == user_id,
                ChatTag.is_deleted == False
            )
        ).order_by(ChatTag.created_at).all()

    @staticmethod
    def create_tag(db: Session, user_id: int, tag_data: TagCreate) -> ChatTag:
        """
        创建标签

        Args:
            db: 数据库会话
            user_id: 用户ID
            tag_data: 标签数据

        Returns:
            ChatTag: 创建的标签对象
        """
        # 检查标签名是否已存在
        existing_tag = db.query(ChatTag).filter(
            and_(
                ChatTag.user_id == user_id,
                ChatTag.name == tag_data.name,
                ChatTag.is_deleted == False
            )
        ).first()

        if existing_tag:
            raise ValueError("标签名已存在")

        tag = ChatTag(
            user_id=user_id,
            name=tag_data.name,
            color=tag_data.color
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        return tag

    @staticmethod
    def delete_tag(db: Session, tag_id: int, user_id: int) -> bool:
        """
        删除标签

        Args:
            db: 数据库会话
            tag_id: 标签ID
            user_id: 用户ID

        Returns:
            bool: 是否删除成功
        """
        tag = db.query(ChatTag).filter(
            and_(
                ChatTag.id == tag_id,
                ChatTag.user_id == user_id,
                ChatTag.is_deleted == False
            )
        ).first()

        if not tag:
            return False

        tag.is_deleted = True
        db.commit()
        return True

    @staticmethod
    def add_tag_to_dialogue(db: Session, dialogue_id: int, tag_id: int, user_id: int) -> bool:
        """
        为对话添加标签

        Args:
            db: 数据库会话
            dialogue_id: 对话ID
            tag_id: 标签ID
            user_id: 用户ID

        Returns:
            bool: 是否添加成功
        """
        # 验证对话和标签是否都属于该用户
        dialogue = db.query(ChatDialogue).filter(
            and_(
                ChatDialogue.id == dialogue_id,
                ChatDialogue.user_id == user_id,
                ChatDialogue.is_deleted == False
            )
        ).first()

        tag = db.query(ChatTag).filter(
            and_(
                ChatTag.id == tag_id,
                ChatTag.user_id == user_id,
                ChatTag.is_deleted == False
            )
        ).first()

        if not dialogue or not tag:
            return False

        # 检查是否已经关联
        existing = db.query(ChatDialogueTag).filter(
            and_(
                ChatDialogueTag.dialogue_id == dialogue_id,
                ChatDialogueTag.tag_id == tag_id
            )
        ).first()

        if existing:
            return True  # 已关联，直接返回成功

        # 创建关联
        dialogue_tag = ChatDialogueTag(
            dialogue_id=dialogue_id,
            tag_id=tag_id
        )
        db.add(dialogue_tag)
        db.commit()
        return True


# 创建全局聊天服务实例
chat_service = ChatService()
