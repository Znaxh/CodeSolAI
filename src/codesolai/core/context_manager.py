"""
Context Manager for handling agent context and memory
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional, List

from .logger import Logger


class ContextManager:
    """Manager for agent context and memory"""

    def __init__(self, logger: Logger, max_size: int = 100000, 
                 compression_threshold: float = 0.8, retention_strategy: str = "importance"):
        self.logger = logger
        self.max_size = max_size
        self.compression_threshold = compression_threshold
        self.retention_strategy = retention_strategy
        
        # Context storage
        self.context_data = {
            'current_session': {},
            'conversation_history': [],
            'user_preferences': {},
            'system_state': {},
            'knowledge_base': {},
            'metadata': {
                'created': datetime.now(),
                'last_updated': datetime.now(),
                'size_bytes': 0
            }
        }
        
        self.logger.info('Context manager initialized', {
            'max_size': max_size,
            'compression_threshold': compression_threshold,
            'retention_strategy': retention_strategy
        })

    async def build_context(self, context_request: Dict[str, Any]) -> Dict[str, Any]:
        """Build context for reasoning based on current input and history"""
        input_text = context_request.get('input', '')
        conversation = context_request.get('conversation', {})
        options = context_request.get('options', {})
        
        # Update current session context
        await self._update_current_session(input_text, conversation, options)
        
        # Build comprehensive context
        context = {
            'current_input': input_text,
            'conversation_id': conversation.get('id'),
            'session_context': self.context_data['current_session'],
            'relevant_history': await self._get_relevant_history(input_text),
            'user_preferences': self.context_data['user_preferences'],
            'system_state': self.context_data['system_state'],
            'knowledge_snippets': await self._get_relevant_knowledge(input_text),
            'metadata': {
                'context_size': self._calculate_context_size(),
                'timestamp': datetime.now()
            }
        }
        
        # Compress if needed
        if self._should_compress():
            context = await self._compress_context(context)
        
        self.logger.debug('Context built', {
            'input_length': len(input_text),
            'context_size': len(json.dumps(context, default=str)),
            'conversation_id': conversation.get('id')
        })
        
        return context

    async def _update_current_session(self, input_text: str, conversation: Dict[str, Any], options: Dict[str, Any]):
        """Update current session context"""
        session_update = {
            'last_input': input_text,
            'last_input_time': datetime.now(),
            'conversation_id': conversation.get('id'),
            'options': options,
            'input_count': self.context_data['current_session'].get('input_count', 0) + 1
        }
        
        self.context_data['current_session'].update(session_update)
        self.context_data['metadata']['last_updated'] = datetime.now()

    async def _get_relevant_history(self, input_text: str, max_items: int = 5) -> List[Dict[str, Any]]:
        """Get relevant conversation history based on input"""
        # Simple relevance scoring based on keyword matching
        # In a real implementation, this could use embeddings or other NLP techniques
        
        relevant_items = []
        input_words = set(input_text.lower().split())
        
        for item in self.context_data['conversation_history']:
            if 'input' in item:
                item_words = set(item['input'].lower().split())
                relevance_score = len(input_words.intersection(item_words)) / len(input_words.union(item_words))
                
                if relevance_score > 0.1:  # Minimum relevance threshold
                    relevant_items.append({
                        'item': item,
                        'relevance_score': relevance_score
                    })
        
        # Sort by relevance and return top items
        relevant_items.sort(key=lambda x: x['relevance_score'], reverse=True)
        return [item['item'] for item in relevant_items[:max_items]]

    async def _get_relevant_knowledge(self, input_text: str, max_items: int = 3) -> List[Dict[str, Any]]:
        """Get relevant knowledge base snippets"""
        # Placeholder for knowledge base retrieval
        # In a real implementation, this would search through stored knowledge
        return []

    def _calculate_context_size(self) -> int:
        """Calculate current context size in bytes"""
        try:
            context_json = json.dumps(self.context_data, default=str)
            size = len(context_json.encode('utf-8'))
            self.context_data['metadata']['size_bytes'] = size
            return size
        except Exception as error:
            self.logger.error('Error calculating context size', {'error': str(error)})
            return 0

    def _should_compress(self) -> bool:
        """Determine if context should be compressed"""
        current_size = self._calculate_context_size()
        threshold_size = self.max_size * self.compression_threshold
        return current_size > threshold_size

    async def _compress_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Compress context to reduce size"""
        compressed_context = context.copy()
        
        # Reduce history items
        if 'relevant_history' in compressed_context:
            compressed_context['relevant_history'] = compressed_context['relevant_history'][:3]
        
        # Summarize session context
        if 'session_context' in compressed_context:
            session = compressed_context['session_context']
            compressed_context['session_context'] = {
                'input_count': session.get('input_count', 0),
                'last_input_time': session.get('last_input_time'),
                'conversation_id': session.get('conversation_id')
            }
        
        self.logger.debug('Context compressed', {
            'original_size': len(json.dumps(context, default=str)),
            'compressed_size': len(json.dumps(compressed_context, default=str))
        })
        
        return compressed_context

    async def add_to_history(self, conversation_data: Dict[str, Any]):
        """Add conversation data to history"""
        history_item = {
            'conversation_id': conversation_data.get('id'),
            'input': conversation_data.get('input', ''),
            'timestamp': datetime.now(),
            'metadata': conversation_data.get('metadata', {})
        }
        
        self.context_data['conversation_history'].append(history_item)
        
        # Apply retention strategy
        await self._apply_retention_strategy()
        
        self.logger.debug('Added to conversation history', {
            'conversation_id': conversation_data.get('id'),
            'history_size': len(self.context_data['conversation_history'])
        })

    async def _apply_retention_strategy(self):
        """Apply retention strategy to manage history size"""
        max_history_items = 100  # Configurable limit
        
        if len(self.context_data['conversation_history']) <= max_history_items:
            return
        
        if self.retention_strategy == 'fifo':
            # Keep most recent items
            self.context_data['conversation_history'] = self.context_data['conversation_history'][-max_history_items:]
        
        elif self.retention_strategy == 'importance':
            # Keep items with higher importance (placeholder logic)
            # In a real implementation, this would use more sophisticated scoring
            self.context_data['conversation_history'] = self.context_data['conversation_history'][-max_history_items:]
        
        elif self.retention_strategy == 'recency':
            # Keep most recent items (same as FIFO for now)
            self.context_data['conversation_history'] = self.context_data['conversation_history'][-max_history_items:]

    async def update_user_preferences(self, preferences: Dict[str, Any]):
        """Update user preferences"""
        self.context_data['user_preferences'].update(preferences)
        self.context_data['metadata']['last_updated'] = datetime.now()
        
        self.logger.debug('User preferences updated', {
            'preferences': list(preferences.keys())
        })

    async def update_system_state(self, state_updates: Dict[str, Any]):
        """Update system state"""
        self.context_data['system_state'].update(state_updates)
        self.context_data['metadata']['last_updated'] = datetime.now()
        
        self.logger.debug('System state updated', {
            'updates': list(state_updates.keys())
        })

    async def add_knowledge(self, knowledge_item: Dict[str, Any]):
        """Add item to knowledge base"""
        item_id = knowledge_item.get('id', str(datetime.now().timestamp()))
        self.context_data['knowledge_base'][item_id] = {
            'content': knowledge_item.get('content', ''),
            'metadata': knowledge_item.get('metadata', {}),
            'timestamp': datetime.now()
        }
        
        self.logger.debug('Knowledge added', {'item_id': item_id})

    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of current context"""
        return {
            'session_inputs': self.context_data['current_session'].get('input_count', 0),
            'history_items': len(self.context_data['conversation_history']),
            'knowledge_items': len(self.context_data['knowledge_base']),
            'context_size_bytes': self.context_data['metadata']['size_bytes'],
            'last_updated': self.context_data['metadata']['last_updated'],
            'retention_strategy': self.retention_strategy
        }

    async def clear_session(self):
        """Clear current session context"""
        self.context_data['current_session'] = {}
        self.context_data['metadata']['last_updated'] = datetime.now()
        
        self.logger.info('Session context cleared')

    async def clear_history(self):
        """Clear conversation history"""
        self.context_data['conversation_history'] = []
        self.context_data['metadata']['last_updated'] = datetime.now()
        
        self.logger.info('Conversation history cleared')

    async def shutdown(self):
        """Shutdown the context manager"""
        self.logger.info('Shutting down context manager', {
            'final_context_size': self._calculate_context_size(),
            'history_items': len(self.context_data['conversation_history'])
        })
