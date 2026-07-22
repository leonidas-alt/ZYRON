from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from uuid import UUID, uuid4


class ConfirmationDecision(str, Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"
    EXPIRED = "expired"


@dataclass(frozen=True, slots=True)
class PendingConfirmation:
    id: UUID
    action: str
    description: str
    created_at: datetime
    expires_at: datetime

    @property
    def expired(self) -> bool:
        return datetime.now(UTC) >= self.expires_at


@dataclass(frozen=True, slots=True)
class ConfirmationResult:
    decision: ConfirmationDecision
    confirmation: PendingConfirmation | None = None

    @property
    def confirmed(self) -> bool:
        return self.decision is ConfirmationDecision.CONFIRMED

    @property
    def cancelled(self) -> bool:
        return self.decision is ConfirmationDecision.CANCELLED

    @property
    def expired(self) -> bool:
        return self.decision is ConfirmationDecision.EXPIRED


class ConfirmationService:
    def __init__(
        self,
        timeout_seconds: int = 30,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError(
                "O tempo de confirmação deve ser maior que zero."
            )

        self._timeout_seconds = timeout_seconds
        self._pending: PendingConfirmation | None = None

    @property
    def pending(self) -> PendingConfirmation | None:
        self._clear_if_expired()

        return self._pending

    @property
    def has_pending(self) -> bool:
        return self.pending is not None

    def request(
        self,
        action: str,
        description: str,
    ) -> PendingConfirmation:
        cleaned_action = action.strip()
        cleaned_description = description.strip()

        if not cleaned_action:
            raise ValueError(
                "O nome da ação não pode estar vazio."
            )

        if not cleaned_description:
            raise ValueError(
                "A descrição da confirmação não pode estar vazia."
            )

        now = datetime.now(UTC)

        confirmation = PendingConfirmation(
            id=uuid4(),
            action=cleaned_action,
            description=cleaned_description,
            created_at=now,
            expires_at=now
            + timedelta(
                seconds=self._timeout_seconds
            ),
        )

        self._pending = confirmation

        return confirmation

    def resolve(
        self,
        user_text: str,
    ) -> ConfirmationResult:
        pending = self._pending

        if pending is None:
            return ConfirmationResult(
                decision=ConfirmationDecision.UNKNOWN,
            )

        if pending.expired:
            self._pending = None

            return ConfirmationResult(
                decision=ConfirmationDecision.EXPIRED,
                confirmation=pending,
            )

        normalized_text = self._normalize(user_text)

        if normalized_text in self._confirmation_words():
            self._pending = None

            return ConfirmationResult(
                decision=ConfirmationDecision.CONFIRMED,
                confirmation=pending,
            )

        if normalized_text in self._cancellation_words():
            self._pending = None

            return ConfirmationResult(
                decision=ConfirmationDecision.CANCELLED,
                confirmation=pending,
            )

        return ConfirmationResult(
            decision=ConfirmationDecision.UNKNOWN,
            confirmation=pending,
        )

    def cancel(self) -> PendingConfirmation | None:
        pending = self._pending
        self._pending = None

        return pending

    def build_prompt(
        self,
        confirmation: PendingConfirmation,
    ) -> str:
        return (
            f"{confirmation.description} "
            "Deseja confirmar? Responda sim ou não."
        )

    def _clear_if_expired(self) -> None:
        if self._pending is None:
            return

        if self._pending.expired:
            self._pending = None

    def _normalize(
        self,
        text: str,
    ) -> str:
        return " ".join(
            text.casefold().strip().split()
        )

    def _confirmation_words(self) -> set[str]:
        return {
            "sim",
            "confirmar",
            "confirmo",
            "confirmado",
            "pode confirmar",
            "pode fazer",
            "pode executar",
            "pode continuar",
            "faça",
            "execute",
            "ok",
            "certo",
        }

    def _cancellation_words(self) -> set[str]:
        return {
            "não",
            "nao",
            "cancelar",
            "cancela",
            "cancele",
            "não faça",
            "nao faça",
            "não execute",
            "nao execute",
            "deixa",
            "deixe",
            "voltar",
        }
