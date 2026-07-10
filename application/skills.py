from __future__ import annotations
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from domain.models import CommandIntent, CommandType, Skill

@dataclass(frozen=True)
class SkillMatch:
    skill: Skill; confidence: float; target: str | None = None

class SkillRegistry:
    def __init__(self) -> None: self._skills: dict[str, Skill] = {}
    def register(self, skill: Skill) -> None: self._skills[skill.name] = skill
    def all(self) -> tuple[Skill, ...]: return tuple(self._skills.values())

class SkillMatcher:
    PRIORITY = {"memory": 100, "browser": 90, "application": 80, "system": 70, "ai_chat": 0}
    def __init__(self, registry: SkillRegistry, ambiguity_margin: float = 0.04) -> None: self._registry = registry; self._margin=ambiguity_margin
    def match(self, text: str) -> SkillMatch | None:
        normalized = self._normalize(text); candidates: list[SkillMatch] = []
        for skill in self._registry.all():
            terms = (*skill.keywords, *skill.synonyms, *skill.examples)
            base = max((self._score(normalized, self._normalize(term)) for term in terms), default=0.0)
            priority_boost = self.PRIORITY.get(skill.name, 0) / 1000
            candidates.append(SkillMatch(skill, min(1.0, base + priority_boost), self._extract_target(normalized, terms)))
        if not candidates: return None
        candidates.sort(key=lambda m: (m.confidence, self.PRIORITY.get(m.skill.name, 0), len(m.skill.keywords)), reverse=True)
        best = candidates[0]
        if len(candidates)>1 and abs(best.confidence-candidates[1].confidence) < self._margin and self.PRIORITY.get(best.skill.name,0)==self.PRIORITY.get(candidates[1].skill.name,0):
            return SkillMatch(best.skill, best.confidence - self._margin, best.target)
        return best
    def _score(self, text: str, term: str) -> float:
        if not term: return 0.0
        if term in text: return min(0.95, 0.70 + len(term)/max(len(text),1)*0.25)
        words=set(text.split()); term_words=set(term.split())
        overlap=len(words & term_words)/max(len(term_words),1)
        return max(overlap*0.82, SequenceMatcher(None, text, term).ratio()*0.65)
    def _extract_target(self, text: str, terms: tuple[str, ...]) -> str | None:
        target = text
        for term in sorted(terms, key=len, reverse=True): target = target.replace(self._normalize(term), " ")
        return re.sub(r"\s+", " ", target).strip() or None
    @staticmethod
    def _normalize(text: str) -> str: return re.sub(r"[^\w\s-]", "", text.lower()).strip()

class IntentMatcher:
    def __init__(self, matcher: SkillMatcher, low_confidence_threshold: float = 0.5) -> None: self._matcher = matcher; self._threshold = low_confidence_threshold
    def match(self, text: str) -> CommandIntent:
        match = self._matcher.match(text)
        if match and match.confidence >= self._threshold:
            return CommandIntent(CommandType.SYSTEM, text, match.target, match.confidence, match.skill.name)
        return CommandIntent(CommandType.AI_CHAT, text, confidence=match.confidence if match else 0.0)
class CapabilityEngine:
    def requires_confirmation(self, skill: Skill | None) -> bool: return bool(skill and skill.capability and skill.capability.dangerous)
