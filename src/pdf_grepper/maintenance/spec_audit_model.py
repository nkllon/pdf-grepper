from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Literal, Mapping, NewType, Optional


FindingId = NewType("FindingId", str)


def make_finding_id(code: str) -> FindingId:
	"""Create a stable finding identifier.

	The intent is that callers pass a stable, code-defined identifier (not derived
	from runtime paths). This helper enforces a consistent format.
	"""
	norm = re.sub(r"[^A-Za-z0-9]+", "_", code.strip()).strip("_").upper()
	if not norm:
		raise ValueError("finding id code must be non-empty")
	return FindingId(f"SPEC_AUDIT_{norm}")


class Severity(str, Enum):
	"""Finding severity for audit results."""

	info = "info"
	warn = "warn"
	error = "error"

	def rank(self) -> int:
		"""Higher severity sorts earlier."""
		return {Severity.error: 0, Severity.warn: 1, Severity.info: 2}[self]


OutputFormat = Literal["human", "json"]


@dataclass(frozen=True, slots=True)
class AuditOptions:
	"""Options that affect auditing and output behavior."""

	repo_root: str
	remediation: bool = False
	output_format: OutputFormat = "human"
	output_path: Optional[str] = None
	severity_threshold: Severity = Severity.error


@dataclass(frozen=True, slots=True)
class Finding:
	"""An atomic audit observation."""

	id: FindingId
	severity: Severity
	message: str
	path: Optional[str] = None
	spec: Optional[str] = None
	recommended_action: Optional[str] = None


@dataclass(frozen=True, slots=True)
class AuditReport:
	"""Audit output: deterministic findings plus summary metadata."""

	findings: tuple[Finding, ...]
	summary: Mapping[str, Any]


def sort_findings(findings: Iterable[Finding]) -> tuple[Finding, ...]:
	"""Return findings sorted deterministically for stable output.

	Sort order:
	- spec (missing spec sorts first)
	- severity (error > warn > info)
	- finding id
	- path
	"""

	def _key(f: Finding) -> tuple[str, int, str, str]:
		spec = f.spec or ""
		path = f.path or ""
		return (spec, f.severity.rank(), str(f.id), path)

	return tuple(sorted(findings, key=_key))

