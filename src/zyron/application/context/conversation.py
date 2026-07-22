from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Iterable


class MessageRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass(slots=True, frozen=True)
class ConversationMessage:

    role: MessageRole
    content: str
    created_at: datetime = field(default_factory=datetime.now)
    source: str = "unknown"


class ConversationContext:

    DEFAULT_MAX_MESSAGES = 30
    DEFAULT_MAX_CHARACTERS = 12_000

    def __init__(
        self,
        max_messages: int = DEFAULT_MAX_MESSAGES,
        max_characters: int = DEFAULT_MAX_CHARACTERS,
        system_prompt: str | None = None,
    ) -> None:
      
        if max_messages <= 0:
            raise ValueError(
                "max_messages deve ser maior que zero."
            )

        if max_characters <= 0:
            raise ValueError(
                "max_characters deve ser maior que zero."
            )

        self._max_messages = max_messages
        self._max_characters = max_characters
        self._messages: list[ConversationMessage] = []

        if system_prompt:
            self.add_system_message(system_prompt)

    @property
    def max_messages(self) -> int:
        return self._max_messages

    @property
    def max_characters(self) -> int:
        return self._max_characters

    @property
    def size(self) -> int:

        return len(self._messages)

    def add_system_message(
        self,
        content: str,
        source: str = "system",
    ) -> ConversationMessage:

        return self.add_message(
            role=MessageRole.SYSTEM,
            content=content,
            source=source,
        )

    def add_user_message(
        self,
        content: str,
        source: str = "user",
    ) -> ConversationMessage:

        return self.add_message(
            role=MessageRole.USER,
            content=content,
            source=source,
        )

    def add_assistant_message(
        self,
        content: str,
        source: str = "assistant",
    ) -> ConversationMessage:

        return self.add_message(
            role=MessageRole.ASSISTANT,
            content=content,
            source=source,
        )

    def add_message(
        self,
        role: MessageRole,
        content: str,
        source: str = "unknown",
    ) -> ConversationMessage:

        cleaned_content = self._clean_content(content)

        if not cleaned_content:
            raise ValueError(
                "O conteúdo da mensagem não pode estar vazio."
            )

        cleaned_source = self._clean_source(source)

        message = ConversationMessage(
            role=role,
            content=cleaned_content,
            source=cleaned_source,
        )

        self._messages.append(message)

        self._enforce_message_limit()

        return message

    def get_messages(
        self,
    ) -> list[ConversationMessage]:

        return list(self._messages)

    def get_recent_messages(
        self,
        limit: int = 10,
    ) -> list[ConversationMessage]:

        if limit <= 0:
            return []

        return list(self._messages[-limit:])

    def get_messages_by_role(
        self,
        role: MessageRole,
    ) -> list[ConversationMessage]:

        return [
            message
            for message in self._messages
            if message.role is role
        ]

    def get_last_message(
        self,
        role: MessageRole | None = None,
    ) -> ConversationMessage | None:

        if role is None:
            if not self._messages:
                return None

            return self._messages[-1]

        for message in reversed(self._messages):
            if message.role is role:
                return message

        return None

    def get_last_user_message(
        self,
    ) -> ConversationMessage | None:

        return self.get_last_message(
            role=MessageRole.USER,
        )

    def get_last_assistant_message(
        self,
    ) -> ConversationMessage | None:

        return self.get_last_message(
            role=MessageRole.ASSISTANT,
        )

    def build_prompt(
        self,
        new_user_message: str | None = None,
        include_system_messages: bool = True,
    ) -> str:

        messages = list(self._messages)

        if new_user_message:
            cleaned_message = self._clean_content(
                new_user_message
            )

            if cleaned_message:
                messages.append(
                    ConversationMessage(
                        role=MessageRole.USER,
                        content=cleaned_message,
                        source="temporary",
                    )
                )

        if not include_system_messages:
            messages = [
                message
                for message in messages
                if message.role is not MessageRole.SYSTEM
            ]

        selected_messages = self._select_messages_for_prompt(
            messages
        )

        lines: list[str] = []

        for message in selected_messages:
            role_name = self._format_role(message.role)

            lines.append(
                f"{role_name}: {message.content}"
            )

        return "\n".join(lines)

    def clear(
        self,
        preserve_system_messages: bool = True,
    ) -> None:

        if preserve_system_messages:
            self._messages = [
                message
                for message in self._messages
                if message.role is MessageRole.SYSTEM
            ]

            return

        self._messages.clear()

    def remove_last_message(
        self,
    ) -> ConversationMessage | None:

        if not self._messages:
            return None

        return self._messages.pop()

    def extend(
        self,
        messages: Iterable[ConversationMessage],
    ) -> None:

        for message in messages:
            self.add_message(
                role=message.role,
                content=message.content,
                source=message.source,
            )

    def to_dict_list(
        self,
    ) -> list[dict[str, str]]:

        return [
            {
                "role": message.role.value,
                "content": message.content,
                "source": message.source,
                "created_at": message.created_at.isoformat(),
            }
            for message in self._messages
        ]

    def _enforce_message_limit(
        self,
    ) -> None:

        while len(self._messages) > self._max_messages:
            removable_index = self._find_oldest_non_system_index()

            if removable_index is None:
                self._messages.pop(0)
            else:
                self._messages.pop(removable_index)

    def _find_oldest_non_system_index(
        self,
    ) -> int | None:

        for index, message in enumerate(self._messages):
            if message.role is not MessageRole.SYSTEM:
                return index

        return None

    def _select_messages_for_prompt(
        self,
        messages: list[ConversationMessage],
    ) -> list[ConversationMessage]:
      
        system_messages = [
            message
            for message in messages
            if message.role is MessageRole.SYSTEM
        ]

        conversation_messages = [
            message
            for message in messages
            if message.role is not MessageRole.SYSTEM
        ]

        selected_reversed: list[ConversationMessage] = []
        total_characters = sum(
            len(message.content)
            for message in system_messages
        )

        for message in reversed(conversation_messages):
            message_size = len(message.content)

            if (
                selected_reversed
                and total_characters + message_size
                > self._max_characters
            ):
                break

            if (
                not selected_reversed
                and message_size > self._max_characters
            ):
                truncated_content = message.content[
                    -self._max_characters:
                ]

                selected_reversed.append(
                    ConversationMessage(
                        role=message.role,
                        content=truncated_content,
                        created_at=message.created_at,
                        source=message.source,
                    )
                )

                break

            total_characters += message_size
            selected_reversed.append(message)

        selected_conversation = list(
            reversed(selected_reversed)
        )

        return system_messages + selected_conversation

    @staticmethod
    def _clean_content(
        content: str,
    ) -> str:

        if not isinstance(content, str):
            return ""

        lines = [
            line.rstrip()
            for line in content.strip().splitlines()
        ]

        return "\n".join(lines).strip()

    @staticmethod
    def _clean_source(
        source: str,
    ) -> str:

        if not isinstance(source, str):
            return "unknown"

        cleaned = source.strip().lower()

        return cleaned or "unknown"

    @staticmethod
    def _format_role(
        role: MessageRole,
    ) -> str:

        names = {
            MessageRole.SYSTEM: "Sistema",
            MessageRole.USER: "Usuário",
            MessageRole.ASSISTANT: "ZYRON",
        }

        return names[role]
