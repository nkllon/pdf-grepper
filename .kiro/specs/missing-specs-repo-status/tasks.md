# Implementation Plan

- [ ] 1. Establish the audit domain model and deterministic ordering
- [ ] 1.1 Define the finding, report, severity, and options data model
  - Define stable finding identifiers, severity levels, and recommended-action fields.
  - Define a deterministic sorting rule for findings and summaries.
  - Ensure all public data structures are type-annotated and immutable where appropriate.
  - _Requirements: 6.2, 5.2_

- [ ] 1.2 Add a minimal “audit runner” interface that returns a report without side effects
  - Ensure the default behavior performs read-only scanning.
  - Ensure runtime errors are represented as findings rather than terminating the scan.
  - _Requirements: 1.5, 6.3, 6.4_

- [ ] 2. Implement spec discovery and spec.json normalization (P)
- [ ] 2.1 (P) Discover spec directories and artifacts under the Kiro specs root
  - Enumerate specification directories deterministically.
  - For each specification, record presence/absence of required artifact files.
  - Report invalid specs when required files are missing.
  - _Requirements: 1.1, 1.3, 1.4_

- [ ] 2.2 (P) Parse and normalize supported spec.json schema variants
  - Support the repository’s existing legacy schema and current template schema.
  - Produce a normalized internal view used by validation logic.
  - Convert JSON parse failures into error findings containing path and reason.
  - _Requirements: 1.2, 2.5, 6.3_

- [ ] 3. Implement structural validators for spec completeness (P)
- [ ] 3.1 (P) Validate phase-to-artifact expectations for requirements/design/tasks
  - Validate required artifacts are present based on declared phase.
  - Emit clear findings per spec with actionable remediation hints.
  - _Requirements: 2.1, 2.3, 2.4_

- [ ] 3.2 (P) Validate requirements files contain at least one numeric requirement heading
  - Detect absence of requirement headings using a robust, deterministic heuristic.
  - Emit a finding that includes the file path and recommended next step.
  - _Requirements: 2.2, 6.2_

- [ ] 4. Implement steering and traceability validations (P)
- [ ] 4.1 (P) Validate required steering file presence and report missing files
  - Verify required steering files are present.
  - Emit findings per missing file.
  - _Requirements: 3.1, 3.2_

- [ ] 4.2 (P) Validate repository path references within steering files
  - Extract referenced repository paths deterministically.
  - Verify referenced paths exist and emit findings for missing targets.
  - _Requirements: 3.3, 6.2_

- [ ] 4.3 (P) Validate traceability matrix presence in the requirements document
  - Confirm a traceability matrix table exists and includes at least one validation artifact mapping.
  - Emit findings that are suitable for CI enforcement.
  - _Requirements: 3.4, 5.3_

- [ ] 5. Implement optional remediation scaffolding
- [ ] 5.1 Plan and apply safe scaffolding actions without overwriting
  - Create missing artifacts only when remediation mode is explicitly enabled.
  - Refuse to overwrite existing files and report conflicts as findings.
  - _Requirements: 4.1, 4.2, 1.5_

- [ ] 5.2 Render templates with feature name and timestamp placeholders
  - Populate placeholders deterministically.
  - Ensure scaffolding uses repository templates and produces consistent output.
  - _Requirements: 4.3, 6.2_

- [ ] 5.3 Produce non-destructive migration guidance for spec.json schema mismatches
  - Produce a machine-readable and human-readable “migration advice” section in reports.
  - Ensure the guidance does not modify existing specs.
  - _Requirements: 4.4, 2.5_

- [ ] 6. Implement reporting, CLI wiring, and exit behavior
- [ ] 6.1 Add a new CLI command to run audits and set an exit code
  - Accept options for output format, output file path, remediation mode, and severity threshold.
  - Exit non-zero when findings meet or exceed the configured threshold.
  - _Requirements: 5.3, 5.4_

- [ ] 6.2 Implement human-readable report output grouped by spec and severity
  - Group and order findings deterministically.
  - Include per-finding recommended action when available.
  - _Requirements: 5.1, 6.2_

- [ ] 6.3 Implement machine-readable JSON output with stable schema
  - Include finding ids, severity, message, spec, path, and recommended action.
  - Include summary counts and generation timestamp.
  - _Requirements: 5.2, 6.2_

- [ ] 7. Tests-first implementation and Docker-based verification
- [ ] 7.1 Add unit tests for schema parsing, ordering, and error-to-finding conversion
  - Cover normalization for legacy and current spec.json shapes.
  - Cover deterministic ordering guarantees.
  - Cover unreadable/invalid JSON behavior including path and reason.
  - _Requirements: 2.5, 6.2, 6.3_

- [ ] 7.2 Add integration tests for end-to-end audits and remediation safety
  - Validate a minimal repo fixture produces expected findings.
  - Validate remediation creates missing files and refuses overwrites.
  - Validate exit codes match severity threshold behavior.
  - _Requirements: 1.1, 4.1, 4.2, 5.3, 5.4_

- [ ] 7.3 Run the test suite in the project’s Docker environment
  - Run unit and integration tests in Docker to ensure CI parity.
  - Confirm results are deterministic across repeated runs.
  - _Requirements: 6.1, 6.2_
