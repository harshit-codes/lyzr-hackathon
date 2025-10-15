
"""
This module provides the `ContextManager` class, which is responsible for
managing the state of a conversation.
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict


@dataclass
class ConversationTurn:
    """
    A data class for representing a single turn in a conversation.
    """

    session_id: str
    turn_number: int
    user_query: str
    agent_response: str
    intent: str
    entities_mentioned: List[str]
    tools_used: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EntityReference:
    """
    A data class for tracking entity references and their context.
    """

    name: str
    entity_type: Optional[str] = None
    last_mentioned_turn: int = 0
    mention_count: int = 0
    aliases: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionContext:
    """
    A data class for representing the context of a conversation session.
    """

    session_id: str
    turns: List[ConversationTurn] = field(default_factory=list)
    entities: Dict[str, EntityReference] = field(default_factory=dict)
    current_turn: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextManager:
    """
    A class for managing the context of a conversation.

    The `ContextManager` is responsible for maintaining the state of a
    conversation, including the conversation history and a list of the
    entities that have been mentioned. It also provides a method for
    resolving pronouns and other references to previous turns in the
    conversation.
    """

    def __init__(self, max_turns_per_session: int = 50):
        """
        Initializes the `ContextManager`.

        Args:
            max_turns_per_session: The maximum number of conversation turns
                to keep in the history for each session.
        """
        self.sessions: Dict[str, SessionContext] = {}
        self.max_turns_per_session = max_turns_per_session

        # Anaphora resolution patterns
        self._initialize_anaphora_patterns()

    def _initialize_anaphora_patterns(self):
        """
        Initializes the patterns for anaphora resolution.
        """
        self.pronoun_patterns = {
            # Personal pronouns
            'he': 'male_person',
            'him': 'male_person',
            'his': 'male_person',
            'she': 'female_person',
            'her': 'female_person',
            'they': 'plural_entity',
            'them': 'plural_entity',
            'their': 'plural_entity',

            # Demonstrative pronouns
            'this': 'recent_entity',
            'that': 'previous_entity',
            'these': 'recent_entities',
            'those': 'previous_entities',

            # Relative pronouns
            'who': 'person',
            'which': 'entity',
            'that': 'entity',
        }

        # Contextual clues for resolution
        self.contextual_indicators = {
            'person': ['researcher', 'scientist', 'professor', 'doctor', 'author'],
            'organization': ['university', 'company', 'institute', 'lab', 'group'],
            'location': ['city', 'country', 'state', 'place', 'location'],
        }

    def add_turn(
        self,
        session_id: str,
        user_query: str,
        agent_response: str,
        intent: str,
        entities_mentioned: List[str],
        tools_used: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConversationTurn:
        """
        Adds a new conversation turn to a session.

        Args:
            session_id: The ID of the session.
            user_query: The user's query.
            agent_response: The agent's response.
            intent: The classified intent of the query.
            entities_mentioned: A list of the entities mentioned in the
                turn.
            tools_used: A list of the tools used to answer the query.
            metadata: Additional metadata for the turn.

        Returns:
            The created `ConversationTurn` object.
        """
        # Get or create session
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionContext(session_id=session_id)

        session = self.sessions[session_id]
        session.current_turn += 1

        # Create turn
        turn = ConversationTurn(
            session_id=session_id,
            turn_number=session.current_turn,
            user_query=user_query,
            agent_response=agent_response,
            intent=intent,
            entities_mentioned=entities_mentioned,
            tools_used=tools_used,
            metadata=metadata or {}
        )

        # Add to session
        session.turns.append(turn)

        # Update entity tracking
        self._update_entity_tracking(session, entities_mentioned, turn.turn_number)

        # Trim old turns if needed
        if len(session.turns) > self.max_turns_per_session:
            session.turns = session.turns[-self.max_turns_per_session:]

        return turn

    def _update_entity_tracking(
        self,
        session: SessionContext,
        entities: List[str],
        turn_number: int
    ):
        """
        Updates the entity references in a session.
        """
        for entity in entities:
            if entity not in session.entities:
                session.entities[entity] = EntityReference(
                    name=entity,
                    last_mentioned_turn=turn_number,
                    mention_count=1
                )
            else:
                ref = session.entities[entity]
                ref.last_mentioned_turn = turn_number
                ref.mention_count += 1

    def resolve_references(self, query: str, session_id: str) -> str:
        """
        Resolves pronouns and implicit references in a query.

        Args:
            query: The query with potential references.
            session_id: The ID of the session to resolve the references
                against.

        Returns:
            The query with the references resolved.
        """
        if session_id not in self.sessions:
            return query

        session = self.sessions[session_id]
        if not session.entities:
            return query

        resolved_query = query

        # Find pronouns and resolve them
        words = re.findall(r'\b\w+\b', query.lower())

        for i, word in enumerate(words):
            if word in self.pronoun_patterns:
                resolved_entity = self._resolve_pronoun(word, session)
                if resolved_entity:
                    # Replace in original query (case-insensitive)
                    pattern = re.compile(re.escape(word), re.IGNORECASE)
                    resolved_query = pattern.sub(resolved_entity, resolved_query, count=1)
                    break  # Resolve one pronoun at a time

        return resolved_query

    def _resolve_pronoun(self, pronoun: str, session: SessionContext) -> Optional[str]:
        """
        Resolves a specific pronoun to an entity.
        """
        pronoun_type = self.pronoun_patterns.get(pronoun.lower())
        if not pronoun_type:
            return None

        # Get candidate entities sorted by recency and frequency
        candidates = []
        for entity_name, entity_ref in session.entities.items():
            # Calculate relevance score based on recency and frequency
            recency_score = 1.0 / (session.current_turn - entity_ref.last_mentioned_turn + 1)
            frequency_score = entity_ref.mention_count / session.current_turn
            total_score = recency_score + frequency_score

            candidates.append((entity_name, total_score, entity_ref))

        if not candidates:
            return None

        # Sort by score (highest first)
        candidates.sort(key=lambda x: x[1], reverse=True)

        # Return the most likely candidate
        best_candidate = candidates[0][0]

        # Additional filtering based on pronoun type
        if pronoun_type == 'male_person':
            # Check if entity looks like a male name (heuristic)
            if self._is_likely_male_name(best_candidate):
                return best_candidate
        elif pronoun_type == 'female_person':
            if self._is_likely_female_name(best_candidate):
                return best_candidate
        elif pronoun_type in ['plural_entity', 'recent_entities']:
            # For plural pronouns, might need multiple entities
            # For now, return the most recent
            return best_candidate
        else:
            return best_candidate

        return None

    def _is_likely_male_name(self, name: str) -> bool:
        """
        A heuristic for checking if a name is likely male.
        """
        male_indicators = ['john', 'james', 'michael', 'david', 'robert', 'william']
        return any(indicator in name.lower() for indicator in male_indicators)

    def _is_likely_female_name(self, name: str) -> bool:
        """
        A heuristic for checking if a name is likely female.
        """
        female_indicators = ['mary', 'anna', 'emma', 'olivia', 'ava', 'isabella']
        return any(indicator in name.lower() for indicator in female_indicators)

    def get_entities(self, session_id: str) -> List[str]:
        """
        Gets all the entities mentioned in a session.

        Args:
            session_id: The ID of the session.

        Returns:
            A list of the entity names.
        """
        if session_id not in self.sessions:
            return []

        return list(self.sessions[session_id].entities.keys())

    def get_recent_entities(self, session_id: str, limit: int = 5) -> List[str]:
        """
        Gets the most recently mentioned entities in a session.

        Args:
            session_id: The ID of the session.
            limit: The maximum number of entities to return.

        Returns:
            A list of the most recently mentioned entity names.
        """
        if session_id not in self.sessions:
            return []

        session = self.sessions[session_id]
        entities_with_turns = [
            (name, ref.last_mentioned_turn)
            for name, ref in session.entities.items()
        ]

        # Sort by most recent turn
        entities_with_turns.sort(key=lambda x: x[1], reverse=True)

        return [name for name, _ in entities_with_turns[:limit]]

    def get_context(self, session_id: str, window: int = 5) -> Dict[str, Any]:
        """
        Gets the conversation context for a session.

        Args:
            session_id: The ID of the session.
            window: The number of recent turns to include in the context.

        Returns:
            A dictionary containing the conversation context.
        """
        if session_id not in self.sessions:
            return {}

        session = self.sessions[session_id]
        recent_turns = session.turns[-window:] if session.turns else []

        return {
            'session_id': session_id,
            'current_turn': session.current_turn,
            'recent_turns': [
                {
                    'turn_number': turn.turn_number,
                    'user_query': turn.user_query,
                    'intent': turn.intent,
                    'entities': turn.entities_mentioned,
                    'tools': turn.tools_used
                }
                for turn in recent_turns
            ],
            'entities': list(session.entities.keys()),
            'recent_entities': self.get_recent_entities(session_id, limit=3)
        }

    def clear_session(self, session_id: str):
        """
        Clears all the context for a session.

        Args:
            session_id: The ID of the session to clear.
        """
        if session_id in self.sessions:
            del self.sessions[session_id]

    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """
        Gets statistics for a session.

        Args:
            session_id: The ID of the session.

        Returns:
            A dictionary containing the session statistics.
        """
        if session_id not in self.sessions:
            return {}

        session = self.sessions[session_id]

        return {
            'session_id': session_id,
            'total_turns': len(session.turns),
            'current_turn': session.current_turn,
            'unique_entities': len(session.entities),
            'most_mentioned_entity': max(
                session.entities.items(),
                key=lambda x: x[1].mention_count,
                default=(None, None)
            )[0] if session.entities else None
        }
