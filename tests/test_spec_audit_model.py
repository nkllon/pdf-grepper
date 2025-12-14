from __future__ import annotations

import pytest

from pdf_grepper.maintenance.spec_audit_model import (
	AuditReport,
	Finding,
	Severity,
	make_finding_id,
	sort_findings,
)


def test_make_finding_id_normalizes_and_prefixes() -> None:
	fid = make_finding_id("missing spec.json")
	assert str(fid) == "SPEC_AUDIT_MISSING_SPEC_JSON"


def test_make_finding_id_rejects_empty() -> None:
	with pytest.raises(ValueError):
		make_finding_id("   ")


def test_finding_is_immutable() -> None:
	f = Finding(
		id=make_finding_id("x"),
		severity=Severity.warn,
		message="m",
		path="a",
		spec="s",
		recommended_action="do",
	)
	with pytest.raises(Exception):
		# dataclasses.FrozenInstanceError, but avoid importing the type.
		f.message = "new"  # type: ignore[misc]


def test_sort_findings_orders_by_spec_then_severity_then_id_then_path() -> None:
	# spec: None sorts before 'alpha'
	f1 = Finding(id=make_finding_id("b"), severity=Severity.info, message="", spec=None, path="b")
	f2 = Finding(id=make_finding_id("a"), severity=Severity.error, message="", spec=None, path="a")
	f3 = Finding(id=make_finding_id("a"), severity=Severity.warn, message="", spec="alpha", path="a")
	f4 = Finding(id=make_finding_id("a"), severity=Severity.error, message="", spec="alpha", path="b")
	f5 = Finding(id=make_finding_id("a"), severity=Severity.error, message="", spec="alpha", path="a")

	sorted_fs = sort_findings([f1, f2, f3, f4, f5])
	assert sorted_fs == (f2, f1, f5, f4, f3)


def test_report_can_hold_sorted_findings() -> None:
	f = Finding(id=make_finding_id("x"), severity=Severity.error, message="m")
	report = AuditReport(findings=sort_findings([f]), summary={"errors": 1})
	assert len(report.findings) == 1
	assert report.summary["errors"] == 1
