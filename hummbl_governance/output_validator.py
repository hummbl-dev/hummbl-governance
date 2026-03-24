"""Output Validator -- Rule-based content validation for agent outputs (ASI-06).

Validates agent output content beyond structural schema checks.
Detects PII leakage, prompt injection attempts, length violations,
blocked terms, and missing provenance citations.

Usage:
    from hummbl_governance import OutputValidator

    validator = OutputValidator.default()
    result = validator.validate("some agent output text")
    # {"valid": True} or {"valid": False, "violations": [...]}

Stdlib-only. Zero third-party dependencies.
"""

from __future__ import annotations

import re
import threading
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Violation:
    """A single validation violation found in agent output."""

    rule: str
    detail: str
    severity: str  # "low", "medium", "high", "critical"


class PIIDetector:
    """Detects personally identifiable information patterns in text.

    Patterns detected:
    - SSN: XXX-XX-XXXX
    - Email addresses
    - Phone numbers (US formats)
    - Credit card numbers (4 groups of 4 digits)
    """

    def __init__(self) -> None:
        self._patterns: list[tuple[str, re.Pattern[str], str]] = [
            ("SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "high"),
            ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "high"),
            (
                "phone",
                re.compile(
                    r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
                ),
                "medium",
            ),
            (
                "credit_card",
                re.compile(r"\b\d{4}[\s-]\d{4}[\s-]\d{4}[\s-]\d{4}\b"),
                "high",
            ),
        ]

    def check(self, text: str) -> list[Violation]:
        """Check text for PII patterns."""
        violations: list[Violation] = []
        for label, pattern, severity in self._patterns:
            for match in pattern.finditer(text):
                violations.append(
                    Violation(
                        rule="PII",
                        detail=f"{label} pattern at position {match.start()}",
                        severity=severity,
                    )
                )
        return violations


class InjectionDetector:
    """Detects prompt injection attempts in agent output.

    Patterns detected:
    - "ignore previous" / "ignore all previous"
    - "system:" prefixed lines
    - "ADMIN:" prefixed lines
    - ```system code blocks
    - Role manipulation ("you are now", "act as", "pretend to be")
    """

    def __init__(self) -> None:
        self._patterns: list[tuple[str, re.Pattern[str], str]] = [
            (
                "ignore_previous",
                re.compile(r"ignore\s+(all\s+)?previous", re.IGNORECASE),
                "critical",
            ),
            (
                "system_prefix",
                re.compile(r"^\s*system\s*:", re.IGNORECASE | re.MULTILINE),
                "critical",
            ),
            (
                "admin_prefix",
                re.compile(r"^\s*ADMIN\s*:", re.MULTILINE),
                "critical",
            ),
            (
                "system_codeblock",
                re.compile(r"```system", re.IGNORECASE),
                "critical",
            ),
            (
                "role_manipulation",
                re.compile(
                    r"\b(?:you\s+are\s+now|act\s+as|pretend\s+to\s+be)\b",
                    re.IGNORECASE,
                ),
                "high",
            ),
        ]

    def check(self, text: str) -> list[Violation]:
        """Check text for injection patterns."""
        violations: list[Violation] = []
        for label, pattern, severity in self._patterns:
            for match in pattern.finditer(text):
                violations.append(
                    Violation(
                        rule="injection",
                        detail=f"{label} at position {match.start()}",
                        severity=severity,
                    )
                )
        return violations


class LengthBounds:
    """Enforces minimum and maximum character length on output.

    Args:
        min_chars: Minimum character count (default 0).
        max_chars: Maximum character count (default 10000).
    """

    def __init__(self, min_chars: int = 0, max_chars: int = 10000) -> None:
        if min_chars < 0:
            raise ValueError("min_chars must be >= 0")
        if max_chars < min_chars:
            raise ValueError("max_chars must be >= min_chars")
        self._min_chars = min_chars
        self._max_chars = max_chars

    @property
    def min_chars(self) -> int:
        return self._min_chars

    @property
    def max_chars(self) -> int:
        return self._max_chars

    def check(self, text: str) -> list[Violation]:
        """Check text length against bounds."""
        violations: list[Violation] = []
        length = len(text)
        if length < self._min_chars:
            violations.append(
                Violation(
                    rule="length",
                    detail=f"output length {length} below minimum {self._min_chars}",
                    severity="medium",
                )
            )
        if length > self._max_chars:
            violations.append(
                Violation(
                    rule="length",
                    detail=f"output length {length} exceeds maximum {self._max_chars}",
                    severity="medium",
                )
            )
        return violations


class BlocklistFilter:
    """Filters output against a configurable list of blocked terms.

    Args:
        terms: List of blocked terms or phrases.
        case_sensitive: Whether matching is case-sensitive (default False).
    """

    def __init__(self, terms: list[str], case_sensitive: bool = False) -> None:
        self._case_sensitive = case_sensitive
        self._patterns: list[tuple[str, re.Pattern[str]]] = []
        for term in terms:
            flags = 0 if case_sensitive else re.IGNORECASE
            self._patterns.append(
                (term, re.compile(re.escape(term), flags))
            )

    def check(self, text: str) -> list[Violation]:
        """Check text for blocked terms."""
        violations: list[Violation] = []
        for term, pattern in self._patterns:
            for match in pattern.finditer(text):
                violations.append(
                    Violation(
                        rule="blocklist",
                        detail=f"blocked term {term!r} at position {match.start()}",
                        severity="high",
                    )
                )
        return violations


class ProvenanceCheck:
    """Flags output that makes claims without citation markers.

    Detects assertion patterns (e.g., "studies show", "according to",
    "research indicates") without nearby citation markers like [1], (Author, 2024),
    or URL references.

    Disabled by default -- enable by passing ``enabled=True``.

    Args:
        enabled: Whether this check is active (default False).
    """

    def __init__(self, enabled: bool = False) -> None:
        self._enabled = enabled
        self._claim_patterns = re.compile(
            r"\b(?:studies\s+show|according\s+to|research\s+(?:indicates|shows|suggests)"
            r"|it\s+is\s+(?:well\s+)?known\s+that|evidence\s+suggests)\b",
            re.IGNORECASE,
        )
        self._citation_pattern = re.compile(
            r"(?:\[\d+\]|\([A-Z][a-z]+(?:\s+et\s+al\.?)?,?\s*\d{4}\)|https?://)"
        )

    @property
    def enabled(self) -> bool:
        return self._enabled

    def check(self, text: str) -> list[Violation]:
        """Check text for unsupported claims."""
        if not self._enabled:
            return []
        violations: list[Violation] = []
        for match in self._claim_patterns.finditer(text):
            # Check for citation within 200 chars after the claim
            start = match.start()
            end = min(match.end() + 200, len(text))
            window = text[match.end() : end]
            if not self._citation_pattern.search(window):
                violations.append(
                    Violation(
                        rule="provenance",
                        detail=f"unsupported claim at position {start}: {match.group()!r}",
                        severity="low",
                    )
                )
        return violations


# Type alias for any rule object with a check(text) -> list[Violation] method
Rule = PIIDetector | InjectionDetector | LengthBounds | BlocklistFilter | ProvenanceCheck


class OutputValidator:
    """Validates agent output content using composable rules.

    Thread-safe. Each call to validate() is independent.

    Usage:
        validator = OutputValidator(rules=[PIIDetector(), InjectionDetector()])
        result = validator.validate("some text")
        # {"valid": True} or {"valid": False, "violations": [...]}
    """

    def __init__(self, rules: list[Any] | None = None) -> None:
        self._rules: list[Any] = list(rules) if rules else []
        self._lock = threading.Lock()

    @classmethod
    def default(cls) -> OutputValidator:
        """Create a validator with default rules: PII + Injection + LengthBounds(10000)."""
        return cls(rules=[PIIDetector(), InjectionDetector(), LengthBounds(max_chars=10000)])

    def validate(self, text: str) -> dict[str, Any]:
        """Validate text against all configured rules.

        Args:
            text: Agent output text to validate.

        Returns:
            Dict with "valid" (bool) and optionally "violations" (list of dicts).
        """
        all_violations: list[Violation] = []
        with self._lock:
            rules = list(self._rules)
        for rule in rules:
            all_violations.extend(rule.check(text))
        if not all_violations:
            return {"valid": True}
        return {
            "valid": False,
            "violations": [
                {"rule": v.rule, "detail": v.detail, "severity": v.severity}
                for v in all_violations
            ],
        }
