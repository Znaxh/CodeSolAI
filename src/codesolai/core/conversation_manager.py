"""
Conversation Manager for handling agent conversations and context
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable

from .logger import Logger


class ConversationManager:
    """Manager for agent conversations and context"""

    def __init__(self, logger: Logger, agent_id: str):
        self.logger = logger
        self.agent_id = agent_id
        self.conversations: Dict[str, Dict[str, Any]] = {}
        
        # Event handlers
        self.on_conversation_start: Optional[Callable] = None
        self.on_conversation_end: Optional[Callable] = None
        
        self.logger.info('Conversation manager initialized', {'agent_id': agent_id})

    async def start_conversation(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new conversation"""
        conversation_id = conversation_data.get('id', str(uuid.uuid4()))
        
        conversation = {
            'id': conversation_id,
            'agent_id': self.agent_id,
            'start_time': datetime.now(),
            'input': conversation_data.get('input', ''),
            'options': conversation_data.get('options', {}),
            'messages': [],
            'context': {},
            'metadata': {},
            'status': 'active'
        }
        
        # Add initial user message
        conversation['messages'].append({
            'role': 'user',
            'content': conversation['input'],
            'timestamp': conversation['start_time']
        })
        
        # Store conversation
        self.conversations[conversation_id] = conversation
        
        # Notify start
        if self.on_conversation_start:
            self.on_conversation_start({
                'conversation_id': conversation_id,
                'agent_id': self.agent_id,
                'input_length': len(conversation['input'])
            })
        
        self.logger.info('Conversation started', {
            'conversation_id': conversation_id,
            'input_length': len(conversation['input'])
        })
        
        return conversation

    async def add_message(self, conversation_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add a message to the conversation"""
        if conversation_id not in self.conversations:
            self.logger.error('Conversation not found', {'conversation_id': conversation_id})
            return False
        
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now(),
            'metadata': metadata or {}
        }
        
        self.conversations[conversation_id]['messages'].append(message)
        
        self.logger.debug('Message added to conversation', {
            'conversation_id': conversation_id,
            'role': role,
            'content_length': len(content)
        })
        
        return True

    async def update_context(self, conversation_id: str, context_updates: Dict[str, Any]) -> bool:
        """Update conversation context"""
        if conversation_id not in self.conversations:
            self.logger.error('Conversation not found', {'conversation_id': conversation_id})
            return False
        
        self.conversations[conversation_id]['context'].update(context_updates)
        
        self.logger.debug('Conversation context updated', {
            'conversation_id': conversation_id,
            'updates': list(context_updates.keys())
        })
        
        return True

    async def update_metadata(self, conversation_id: str, metadata_updates: Dict[str, Any]) -> bool:
        """Update conversation metadata"""
        if conversation_id not in self.conversations:
            self.logger.error('Conversation not found', {'conversation_id': conversation_id})
            return False
        
        self.conversations[conversation_id]['metadata'].update(metadata_updates)
        
        self.logger.debug('Conversation metadata updated', {
            'conversation_id': conversation_id,
            'updates': list(metadata_updates.keys())
        })
        
        return True

    async def end_conversation(self, conversation_id: str, final_data: Optional[Dict[str, Any]] = None) -> bool:
        """End a conversation"""
        if conversation_id not in self.conversations:
            self.logger.error('Conversation not found', {'conversation_id': conversation_id})
            return False
        
        conversation = self.conversations[conversation_id]
        conversation['end_time'] = datetime.now()
        conversation['duration'] = (conversation['end_time'] - conversation['start_time']).total_seconds()
        conversation['status'] = 'completed'
        
        if final_data:
            conversation['final_data'] = final_data
        
        # Notify end
        if self.on_conversation_end:
            self.on_conversation_end({
                'conversation_id': conversation_id,
                'agent_id': self.agent_id,
                'duration': conversation['duration'],
                'message_count': len(conversation['messages'])
            })
        
        self.logger.info('Conversation ended', {
            'conversation_id': conversation_id,
            'duration': conversation['duration'],
            'message_count': len(conversation['messages'])
        })
        
        return True

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation by ID"""
        return self.conversations.get(conversation_id)

    def get_conversation_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get messages from a conversation"""
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            return []
        return conversation.get('messages', [])

    def get_conversation_context(self, conversation_id: str) -> Dict[str, Any]:
        """Get context from a conversation"""
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            return {}
        return conversation.get('context', {})

    def get_active_conversations(self) -> List[str]:
        """Get list of active conversation IDs"""
        return [
            conv_id for conv_id, conv in self.conversations.items()
            if conv.get('status') == 'active'
        ]

    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        total_conversations = len(self.conversations)
        active_conversations = len(self.get_active_conversations())
        completed_conversations = sum(
            1 for conv in self.conversations.values()
            if conv.get('status') == 'completed'
        )
        
        total_messages = sum(
            len(conv.get('messages', []))
            for conv in self.conversations.values()
        )
        
        return {
            'total_conversations': total_conversations,
            'active_conversations': active_conversations,
            'completed_conversations': completed_conversations,
            'total_messages': total_messages,
            'agent_id': self.agent_id
        }

    async def cleanup_old_conversations(self, max_age_hours: int = 24):
        """Cleanup old conversations"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        conversations_to_remove = []
        for conv_id, conv in self.conversations.items():
            if conv.get('status') == 'completed':
                end_time = conv.get('end_time')
                if end_time and end_time.timestamp() < cutoff_time:
                    conversations_to_remove.append(conv_id)
        
        for conv_id in conversations_to_remove:
            del self.conversations[conv_id]
        
        if conversations_to_remove:
            self.logger.info('Cleaned up old conversations', {
                'removed_count': len(conversations_to_remove),
                'max_age_hours': max_age_hours
            })

    async def shutdown(self):
        """Shutdown the conversation manager"""
        self.logger.info('Shutting down conversation manager', {
            'total_conversations': len(self.conversations)
        })
        
        # End any active conversations
        active_conversations = self.get_active_conversations()
        for conv_id in active_conversations:
            await self.end_conversation(conv_id, {'reason': 'shutdown'})
