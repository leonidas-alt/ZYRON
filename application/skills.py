from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher

from domain.models import CommandIntent, CommandType, Skill


@dataclass(frozen=True)
class SkillMatch:
    skill: Skill
    confidence: float
    target: str | None = None


class SkillRegistry:
    """Stores skills exposed by discovered plugins."""

    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        self._skills[skill.name] = skill

    def all(self) -> tuple[Skill, ...]:
        return tuple(self._skills.values())


class SkillMatcher:
    """Scores input text against registered skills without hard-coded branches."""

    def __init__(self, registry: SkillRegistry) -> None:
        self._registry = registry

    def match(self, text: str) -> SkillMatch | None:
        normalized = self._normalize(text)
        best: SkillMatch | None = None
        for skill in self._registry.all():
            terms = (*skill.keywords, *skill.synonyms, *skill.examples)
            score = max(
                (self._score(normalized, self._normalize(term)) for term in terms),
                default=0.0,
            )
            if best is None or score > best.confidence:
                best = SkillMatch(skill, score, self._extract_target(normalized, terms))
        return best

    def _score(self, text: str, term: str) -> float:
        if not term:
            return 0.0
        if term in text:
            coverage = len(term) / max(len(text), 1)
            return min(1.0, 0.72 + coverage * 0.28)
        return SequenceMatcher(None, text, term).ratio()

    def _extract_target(self, text: str, terms: tuple[str, ...]) -> str | None:
        target = text
        for term in sorted(terms, key=len, reverse=True):
            target = target.replace(self._normalize(term), " ")
        return re.sub(r"\s+", " ", target).strip() or None

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"[^\w\s-]", "", text.lower()).strip()


class IntentMatcher:
    """Converts a skill match into a command intent with confidence metadata."""

    def __init__(self, matcher: SkillMatcher, low_confidence_threshold: float = 0.5) -> None:
        self._matcher = matcher
        self._threshold = low_confidence_threshold

    def match(self, text: str) -> CommandIntent:
        match = self._matcher.match(text)
        if match and match.confidence >= self._threshold:
            return CommandIntent(
                CommandType.SYSTEM,
                text,
                match.target,
                match.confidence,
                match.skill.name,
            )
        return CommandIntent(
            CommandType.AI_CHAT,
            text,
            confidence=match.confidence if match else 0.0,
        )


class CapabilityEngine:
    """Policy helper for capability safety checks."""

    def requires_confirmation(self, skill: Skill | None) -> bool:
        return bool(skill and skill.capability and skill.capability.dangerous)
