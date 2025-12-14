# Requirements Document

## Introduction

The Missing Specs Repo Status feature provides a repository audit capability that detects missing or inconsistent spec-driven development artifacts (Kiro specs, steering files, and traceability references) and produces actionable findings so the `pdf-grepper` project can keep its specifications complete and current.

## Requirements

### Requirement 1: Specification discovery and inventory
**Objective:** As a maintainer, I want to inventory all Kiro specifications in the repository, so that I can understand what specs exist and their current lifecycle phase.

#### Acceptance Criteria
1. When an audit is executed, the Spec Auditor shall discover all specification directories under `.kiro/specs/`.
2. When a specification directory is discovered, the Spec Auditor shall read its `spec.json` and include the spec identifier and declared phase in the audit output.
3. If a specification directory does not contain `spec.json`, then the Spec Auditor shall report the directory as an invalid or incomplete specification.
4. The Spec Auditor shall report the presence or absence of `requirements.md`, `design.md`, and `tasks.md` for each discovered specification.
5. While running in read-only mode, the Spec Auditor shall not modify any repository files.

### Requirement 2: Specification completeness and metadata validation
**Objective:** As a maintainer, I want missing or inconsistent spec artifacts to be detected deterministically, so that I can remediate gaps without manual hunting.

#### Acceptance Criteria
1. When a specification is in phase `initialized`, the Spec Auditor shall verify that `requirements.md` exists.
2. When a specification is in phase `requirements-generated` (or later), the Spec Auditor shall verify that `requirements.md` contains at least one requirement heading in the form `Requirement <number>:`.
3. When a specification is in phase `design-generated` (or later), the Spec Auditor shall verify that `design.md` exists.
4. When a specification is in phase `tasks-generated` (or later), the Spec Auditor shall verify that `tasks.md` exists.
5. If a specification’s `spec.json` does not match the repository’s current spec metadata shape, then the Spec Auditor shall report a schema mismatch and list the expected keys.

### Requirement 3: Steering and traceability reference validation
**Objective:** As a maintainer, I want project steering and traceability references to be verifiable, so that spec-driven development context stays consistent and actionable.

#### Acceptance Criteria
1. When an audit is executed, the Spec Auditor shall verify that `.kiro/steering/` contains `product.md`, `tech.md`, and `structure.md`.
2. If any required steering file is missing, then the Spec Auditor shall report the missing file path(s) as findings.
3. When a steering file references a path in the repository, the Spec Auditor shall verify that the referenced path exists.
4. Where `docs/requirements.md` exists, the Spec Auditor shall verify that it contains a traceability matrix table that maps requirement IDs to at least one validation artifact.

### Requirement 4: Safe remediation and scaffolding (optional)
**Objective:** As a maintainer, I want an optional remediation mode that can scaffold missing artifacts safely, so that I can repair gaps quickly without accidental data loss.

#### Acceptance Criteria
1. Where remediation mode is enabled, the Spec Auditor shall create missing spec files using the repository’s templates without overwriting existing files.
2. If a remediation action would overwrite an existing file, then the Spec Auditor shall refuse the change and report the conflict.
3. When remediation creates a spec file from a template, the Spec Auditor shall populate feature name and timestamp placeholders.
4. Where a `spec.json` schema mismatch is detected, the Spec Auditor shall provide a non-destructive migration output rather than modifying the existing `spec.json` in place.

### Requirement 5: Audit outputs and exit behavior
**Objective:** As a maintainer, I want the audit to produce outputs suitable for both humans and automation, so that missing specs can be detected locally and in CI.

#### Acceptance Criteria
1. When an audit completes, the Spec Auditor shall produce a human-readable summary that lists findings grouped by specification and severity.
2. Where machine-readable output is enabled, the Spec Auditor shall produce a structured report that includes finding IDs, file paths, and recommended actions.
3. If the audit detects missing required artifacts, then the Spec Auditor shall exit with a non-zero status.
4. If the audit detects no findings above the configured severity threshold, then the Spec Auditor shall exit with a zero status.

### Requirement 6: Safety, determinism, and offline operation
**Objective:** As a maintainer, I want the audit to be safe and repeatable, so that it can run frequently without side effects.

#### Acceptance Criteria
1. The Spec Auditor shall run without requiring network access.
2. The Spec Auditor shall produce consistent findings given the same repository state.
3. If the Spec Auditor cannot read a required file, then the Spec Auditor shall report an error that includes the file path and the reason.
4. While scanning, the Spec Auditor shall not execute repository code.
