---
inclusion: always
---

# PDF-Grepper Requirements Conformance

This steering file ensures all code changes conform to the requirements and design specifications defined in `.kiro/specs/pdf-intelligence-system/`.

## Traceability Requirements

When implementing features or fixing bugs:

1. **Reference Requirements**: Always reference the specific requirement ID (e.g., FR-1, NFR-2) from `docs/requirements.md` or the spec requirements
2. **Update Traceability Matrix**: Update the traceability matrix in `docs/requirements.md` when adding tests or validation artifacts
3. **Link Tests to Properties**: All property-based tests must include a comment with the format:
   ```python
   # Feature: pdf-intelligence-system, Property N: <property description>
   ```

## EARS Compliance

All requirements must follow EARS (Easy Approach to Requirements Syntax) patterns:

- **Ubiquitous**: THE <system> SHALL <response>
- **Event-driven**: WHEN <trigger>, THEN THE <system> SHALL <response>
- **State-driven**: WHILE <condition>, THE <system> SHALL <response>
- **Unwanted event**: IF <condition>, THEN THE <system> SHALL <response>
- **Optional feature**: WHERE <option>, THE <system> SHALL <response>

## Correctness Properties

The system has 43 defined correctness properties in `.kiro/specs/pdf-intelligence-system/design.md`. When implementing features:

1. **Verify Property Coverage**: Ensure the implementation satisfies the relevant correctness properties
2. **Property-Based Testing**: Use Hypothesis with minimum 100 iterations per property test
3. **Round-Trip Testing**: For serialization/parsing (Turtle, JSON), always implement round-trip properties
4. **Provenance Tracking**: All extracted elements must include SourceSpan with source_path, page_index, and bbox

## Architecture Principles

### Local-First Design
- All core functionality must work offline without network access
- Cloud adapters are optional enhancements, not requirements
- Graceful degradation when cloud services are unavailable

### Modular Extensibility
- New cloud adapters should follow the existing interface pattern
- New enrichment sources should be added to `pdf_grepper.enrich`
- New export formats should be added to `pdf_grepper.ontology`

### Error Handling
- **Fail Fast**: Invalid inputs or missing required dependencies should error immediately
- **Graceful Degradation**: Optional components (cloud, enrichment) should fail gracefully
- **Clear Messages**: All errors must include context (file paths, step names, reasons)
- **Logging**: All errors must be logged with appropriate severity

### Provenance and Reproducibility
- Every extracted element must track its source (file path, page, coordinates)
- Offline mode must produce deterministic results
- Cache operations must preserve provenance metadata

## Testing Requirements

### Property-Based Testing
- Use Hypothesis for Python property-based tests
- Configure with `@settings(max_examples=100)`
- Tag each test with the property number and description
- Test universal properties that hold across all valid inputs

### Unit Testing
- Test specific examples and edge cases
- Test error conditions and boundary values
- Mock external dependencies (cloud APIs, file system)
- Use pytest fixtures for test data

### Integration Testing
- Test full pipeline with sample PDFs
- Test multi-file processing with provenance verification
- Test offline mode end-to-end
- Test cache behavior across multiple runs

## Code Quality Standards

### Type Annotations
- All functions must have type annotations for parameters and return values
- Use dataclasses for structured data (already defined in `types.py`)
- Use Optional[] for nullable values

### Documentation
- All modules must have docstrings explaining purpose
- All public functions must have docstrings with parameter descriptions
- Complex algorithms must include inline comments

### Logging
- Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)
- Log all pipeline steps with step names
- Log all cloud adapter invocations
- Log all errors with context

## Implementation Checklist

Before marking a task as complete:

- [ ] Implementation satisfies all acceptance criteria for referenced requirements
- [ ] Relevant correctness properties are validated by tests
- [ ] Error handling follows graceful degradation principles
- [ ] Provenance metadata is correctly populated
- [ ] Type annotations are complete
- [ ] Docstrings are present and accurate
- [ ] Logging is appropriate for the component
- [ ] Tests pass (unit, property-based, and integration as applicable)
- [ ] Traceability matrix is updated if new tests were added

## Specific Implementation Guidance

### OCR Mode Selection
- `auto`: Check text density, trigger OCR if sparse
- `local`: Always use Tesseract
- `none`: Skip OCR entirely
- Always include confidence scores with OCR results

### Entity Extraction
- Primary: Use spaCy NER for standard entity types
- Fallback: Use regex for capitalized noun phrases
- Deduplicate by normalized text (lowercase)
- Assign UUIDs to all entities

### Relation Extraction
- Pattern-based: "uses", "depends on", "integrates with", "is part of"
- Validate entity references exist
- Assign confidence scores (0.5 for pattern-based)

### Diagram Processing
- Extract rectangles as nodes, lines as edges
- Best-effort interpretation (failures should not stop pipeline)
- Record bounding boxes for all primitives

### Ontology Export
- Use rdflib for RDF graph construction
- Include standard vocabularies: RDF, RDFS, DCTERMS, XSD
- Generate URIs for all model elements
- Include provenance triples for all elements with SourceSpan

### Caching
- Cache key: hash of input files + configuration
- Store intermediate results (OCR, entities, relations)
- Include provenance metadata indicating cache source
- Verify cache consistency on read

## Anti-Patterns to Avoid

❌ **Silent Failures**: Never catch exceptions without logging or reporting
❌ **Hardcoded Credentials**: Always use environment variables
❌ **Blocking on Optional Features**: Cloud/enrichment failures should not stop pipeline
❌ **Missing Provenance**: All extracted elements must have source tracking
❌ **Non-Deterministic Offline Mode**: Offline processing must be reproducible
❌ **Skipping Tests**: All properties must have corresponding property-based tests
❌ **Incomplete Error Messages**: Always include context (paths, reasons)

## References

- Requirements: `.kiro/specs/pdf-intelligence-system/requirements.md`
- Design: `.kiro/specs/pdf-intelligence-system/design.md`
- Tasks: `.kiro/specs/pdf-intelligence-system/tasks.md`
- Traceability Matrix: `docs/requirements.md`
