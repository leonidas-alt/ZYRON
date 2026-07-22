from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping


class PluginStatus(StrEnum):
    CREATED = "created"
    INITIALIZED = "initialized"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class PluginMetadata:
    name: str
    version: str
    description: str
    author: str | None = None
    capabilities: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class PluginExecutionResult:
    success: bool
    message: str
    data: Mapping[str, Any] = field(default_factory=dict)


class Plugin(ABC):
    def __init__(
        self,
        metadata: PluginMetadata,
    ) -> None:
        self._metadata = metadata
        self._status = PluginStatus.CREATED

    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata

    @property
    def name(self) -> str:
        return self._metadata.name

    @property
    def version(self) -> str:
        return self._metadata.version

    @property
    def status(self) -> PluginStatus:
        return self._status

    @property
    def is_enabled(self) -> bool:
        return self._status is PluginStatus.ENABLED

    def initialize(self) -> None:
        if self._status is PluginStatus.INITIALIZED:
            return

        if self._status is PluginStatus.ENABLED:
            return

        try:
            self.on_initialize()
            self._status = PluginStatus.INITIALIZED
        except Exception:
            self._status = PluginStatus.ERROR
            raise

    def enable(self) -> None:
        if self._status is PluginStatus.ENABLED:
            return

        if self._status is PluginStatus.CREATED:
            self.initialize()

        if self._status is PluginStatus.ERROR:
            raise RuntimeError(
                f"O plugin '{self.name}' está em estado de erro."
            )

        try:
            self.on_enable()
            self._status = PluginStatus.ENABLED
        except Exception:
            self._status = PluginStatus.ERROR
            raise

    def disable(self) -> None:
        if self._status is PluginStatus.DISABLED:
            return

        if self._status is PluginStatus.CREATED:
            self._status = PluginStatus.DISABLED
            return

        try:
            self.on_disable()
            self._status = PluginStatus.DISABLED
        except Exception:
            self._status = PluginStatus.ERROR
            raise

    def supports(
        self,
        capability: str,
    ) -> bool:
        normalized_capability = capability.strip().lower()

        return any(
            item.strip().lower() == normalized_capability
            for item in self._metadata.capabilities
        )

    def execute(
        self,
        action: str,
        parameters: Mapping[str, Any] | None = None,
    ) -> PluginExecutionResult:
        if not self.is_enabled:
            return PluginExecutionResult(
                success=False,
                message=f"O plugin '{self.name}' não está habilitado.",
            )

        normalized_action = action.strip()

        if not normalized_action:
            return PluginExecutionResult(
                success=False,
                message="A ação do plugin não pode estar vazia.",
            )

        try:
            return self.handle(
                normalized_action,
                parameters or {},
            )
        except Exception as error:
            self._status = PluginStatus.ERROR

            return PluginExecutionResult(
                success=False,
                message=(
                    f"Falha ao executar a ação '{normalized_action}' "
                    f"no plugin '{self.name}': {error}"
                ),
            )

    def health_check(self) -> bool:
        if self._status is PluginStatus.ERROR:
            return False

        try:
            return self.on_health_check()
        except Exception:
            self._status = PluginStatus.ERROR
            return False

    def on_initialize(self) -> None:
        pass

    def on_enable(self) -> None:
        pass

    def on_disable(self) -> None:
        pass

    def on_health_check(self) -> bool:
        return True

    @abstractmethod
    def handle(
        self,
        action: str,
        parameters: Mapping[str, Any],
    ) -> PluginExecutionResult:
        raise NotImplementedError
