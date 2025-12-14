# Implementation Plan

- [ ] 1. Validate and enhance core document loading infrastructure
  - Review and test PDF loading with PyMuPDF for multi-page documents
  - Review and test DOCX loading for OCR variants
  - Ensure multi-file provenance tracking is correctly implemented
  - Verify error handling for invalid/corrupted files
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 1.1 Write property test for PDF loading
  - **Property 1: PDF loading preserves page structure**
  - **Validates: Requirements 1.1**

- [x] 1.2 Write property test for multi-file provenance
  - **Property 2: Multi-file provenance tracking**
  - **Validates: Requirements 1.3**

- [x] 1.3 Write property test for invalid file handling
  - **Property 3: Invalid file error reporting**
  - **Validates: Requirements 1.4**

- [ ] 2. Implement and validate OCR mode selection logic
  - Review OCR mode handling (auto, local, none) in loader
  - Implement sparse text detection for auto mode
  - Ensure Tesseract availability checking
  - Verify confidence score inclusion in OCR results
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 2.1 Write property test for auto OCR triggering
  - **Property 4: Auto OCR triggers on sparse text**
  - **Validates: Requirements 2.1**

- [x] 2.2 Write property test for local OCR mode
  - **Property 5: Local OCR mode universality**
  - **Validates: Requirements 2.2**

- [x] 2.3 Write property test for none OCR mode
  - **Property 6: None OCR mode skips processing**
  - **Validates: Requirements 2.3**

- [x] 2.4 Write property test for OCR confidence scores
  - **Property 7: OCR confidence inclusion**
  - **Validates: Requirements 2.5**

- [ ] 3. Implement cloud adapter integration framework
  - Review existing cloud adapter stubs (OpenAI, Google, AWS, Azure)
  - Implement environment variable credential checking
  - Ensure graceful fallback when adapters fail
  - Verify offline mode prevents cloud invocations
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 3.1 Write property test for offline mode cloud prevention
  - **Property 8: Offline mode prevents cloud calls**
  - **Validates: Requirements 3.4, 17.1**

- [x] 3.2 Write property test for cloud adapter graceful degradation
  - **Property 9: Cloud adapter graceful degradation**
  - **Validates: Requirements 3.5**

- [ ] 4. Enhance layout parsing and spatial analysis
  - Review layout parsing implementation for bounding box extraction
  - Implement reading order preservation (top-to-bottom, left-to-right)
  - Ensure error resilience for layout parsing failures
  - Verify SourceSpan provenance is correctly populated
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 4.1 Write property test for bounding box inclusion
  - **Property 10: Layout parsing includes bounding boxes**
  - **Validates: Requirements 4.1, 4.2**

- [x] 4.2 Write property test for reading order
  - **Property 11: Reading order preservation**
  - **Validates: Requirements 4.3**

- [x] 4.3 Write property test for layout parsing resilience
  - **Property 12: Layout parsing resilience**
  - **Validates: Requirements 4.4**

- [ ] 5. Implement and validate entity extraction
  - Review spaCy NER integration for standard entity types
  - Review regex fallback for CONCEPT entities
  - Implement entity deduplication by normalized text
  - Ensure unique ID assignment for all entities
  - Verify source span provenance tracking
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 5.1 Write property test for entity extraction invocation
  - **Property 13: Entity extraction invocation**
  - **Validates: Requirements 5.1**

- [x] 5.2 Write property test for entity unique IDs
  - **Property 14: Entity unique identifiers**
  - **Validates: Requirements 5.4**

- [x] 5.3 Write property test for entity deduplication
  - **Property 15: Entity deduplication**
  - **Validates: Requirements 5.5**

- [ ] 6. Implement and validate relation extraction
  - Review pattern-based relation extraction (uses, depends on, integrates with, is part of)
  - Ensure relation structure includes subject, predicate, object, and span
  - Implement unique ID assignment and confidence scoring
  - Verify cloud adapter refinement integration
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 6.1 Write property test for relation structure
  - **Property 16: Relation structure completeness**
  - **Validates: Requirements 6.2**

- [x] 6.2 Write property test for relation unique IDs
  - **Property 17: Relation unique identifiers**
  - **Validates: Requirements 6.3**

- [ ] 7. Implement and validate stakeholder extraction
  - Review stakeholder identification logic
  - Ensure stakeholder structure includes actor, claim, and span
  - Implement unique ID assignment
  - Verify confidence scoring
  - _Requirements: 7.1, 7.2, 7.3_

- [x] 7.1 Write property test for stakeholder structure
  - **Property 18: Stakeholder structure completeness**
  - **Validates: Requirements 7.2**

- [x] 7.2 Write property test for stakeholder unique IDs
  - **Property 19: Stakeholder unique identifiers**
  - **Validates: Requirements 7.3**

- [ ] 8. Implement and validate diagram processing
  - Review diagram primitive extraction from vector graphics
  - Review diagram interpretation (nodes and edges)
  - Ensure node structure includes label, type, and span
  - Ensure edge structure includes source, target, directionality, and label
  - Verify error resilience for diagram failures
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 8.1 Write property test for diagram node structure
  - **Property 20: Diagram node structure completeness**
  - **Validates: Requirements 8.3**

- [x] 8.2 Write property test for diagram edge structure
  - **Property 21: Diagram edge structure completeness**
  - **Validates: Requirements 8.4**

- [x] 8.3 Write property test for diagram processing resilience
  - **Property 22: Diagram processing resilience**
  - **Validates: Requirements 8.5**

- [ ] 9. Implement and validate dimension discovery
  - Review dimension discovery patterns (latency, throughput, cost, performance)
  - Ensure dimension structure includes name, value, unit, and span
  - Implement unique ID assignment and confidence scoring
  - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [x] 9.1 Write property test for dimension structure
  - **Property 23: Dimension structure completeness**
  - **Validates: Requirements 9.3, 9.4**

- [ ] 10. Implement and validate domain inference
  - Review TF-IDF computation for domain label extraction
  - Ensure stop word filtering is applied
  - Verify top-8 term limit is enforced
  - Test with various document types
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [x] 10.1 Write property test for stop word filtering
  - **Property 24: Domain label stop word filtering**
  - **Validates: Requirements 10.3**

- [x] 10.2 Write property test for domain label count limit
  - **Property 25: Domain label count limit**
  - **Validates: Requirements 10.4**

- [ ] 11. Implement and validate web enrichment
  - Review web search integration (DuckDuckGo, Wikipedia)
  - Ensure offline mode skips web enrichment
  - Verify enrichment metadata recording
  - Ensure error resilience for enrichment failures
  - _Requirements: 11.1, 11.2, 11.3, 11.4_

- [x] 11.1 Write property test for offline web enrichment skip
  - **Property 26: Offline mode skips web enrichment**
  - **Validates: Requirements 11.2, 17.2**

- [x] 11.2 Write property test for enrichment metadata
  - **Property 27: Web enrichment metadata recording**
  - **Validates: Requirements 11.3**

- [x] 11.3 Write property test for enrichment resilience
  - **Property 28: Web enrichment resilience**
  - **Validates: Requirements 11.4**

- [ ] 12. Implement and validate Turtle ontology export
  - Review RDF graph construction and namespace management
  - Ensure URI generation for all model elements
  - Verify provenance metadata inclusion (source paths, page indices, bboxes)
  - Ensure standard vocabulary usage (RDF, RDFS, DCTERMS, XSD)
  - Verify file writing and Turtle syntax validity
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 12.1 Write property test for Turtle round-trip consistency
  - **Property 29: Turtle export round-trip consistency**
  - **Validates: Requirements 12.1**

- [x] 12.2 Write property test for URI generation
  - **Property 30: Turtle URI generation completeness**
  - **Validates: Requirements 12.2**

- [x] 12.3 Write property test for provenance inclusion
  - **Property 31: Turtle provenance inclusion**
  - **Validates: Requirements 12.3**

- [x] 12.4 Write property test for vocabulary compliance
  - **Property 32: Turtle vocabulary compliance**
  - **Validates: Requirements 12.4**

- [x] 12.5 Write property test for Turtle file creation
  - **Property 33: Turtle file creation**
  - **Validates: Requirements 12.5**

- [ ] 13. Implement and validate JSON export
  - Review JSON serialization using dataclasses.asdict
  - Ensure completeness of exported data
  - Verify file writing and JSON syntax validity
  - _Requirements: 13.1, 13.2, 13.3_

- [x] 13.1 Write property test for JSON round-trip consistency
  - **Property 34: JSON export round-trip consistency**
  - **Validates: Requirements 13.1**

- [x] 13.2 Write property test for JSON completeness
  - **Property 35: JSON completeness**
  - **Validates: Requirements 13.2**

- [x] 13.3 Write property test for JSON file creation
  - **Property 36: JSON file creation**
  - **Validates: Requirements 13.3**

- [ ] 14. Checkpoint - Ensure all core functionality tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 15. Implement and validate caching mechanism
  - Design cache key generation based on input files and configuration
  - Implement cache write operations with provenance metadata
  - Implement cache read operations with consistency checks
  - Verify cache directory creation and management
  - _Requirements: 16.1, 16.2, 16.3_

- [x] 15.1 Write property test for cache consistency
  - **Property 37: Cache write and read consistency**
  - **Validates: Requirements 16.1, 16.2**

- [x] 15.2 Write property test for cache provenance
  - **Property 38: Cache provenance metadata**
  - **Validates: Requirements 16.3**

- [ ] 16. Implement and validate offline mode
  - Review offline flag propagation through pipeline
  - Ensure all network-dependent operations check offline flag
  - Verify completeness of offline processing
  - Test error handling for missing local dependencies
  - _Requirements: 17.1, 17.2, 17.3, 17.4_

- [x] 16.1 Write property test for offline mode completeness
  - **Property 39: Offline mode completeness**
  - **Validates: Requirements 17.3**

- [ ] 17. Implement and validate logging infrastructure
  - Review logging configuration and levels
  - Ensure pipeline step logging
  - Ensure cloud adapter invocation logging
  - Ensure error logging with context
  - Ensure output path logging
  - _Requirements: 19.1, 19.2, 19.3, 19.4_

- [x] 17.1 Write property test for pipeline logging
  - **Property 40: Pipeline logging invocation**
  - **Validates: Requirements 19.1**

- [ ] 17.2 Write property test for error logging
  - **Property 41: Error logging with context**
  - **Validates: Requirements 19.3**

- [x] 17.3 Write property test for output path logging
  - **Property 42: Output path logging**
  - **Validates: Requirements 19.4**

- [ ] 18. Implement and validate deterministic processing
  - Review random seed usage in TF-IDF and other algorithms
  - Implement fixed seeding for deterministic mode
  - Verify offline mode produces identical outputs
  - _Requirements: 20.1, 20.2, 20.3_

- [x] 18.1 Write property test for deterministic offline processing
  - **Property 43: Deterministic offline processing**
  - **Validates: Requirements 20.1, 20.2**

- [ ] 19. Validate CLI interface and configuration
  - Review CLI argument parsing for all flags
  - Test positional arguments for input files
  - Test all optional flags (--out, --json, --ocr, --cloud, --enrich-web, --offline, --base-uri)
  - Verify comma-separated cloud adapter parsing
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 14.8_

- [x] 19.1 Write unit tests for CLI flag parsing
  - Test all CLI flags and argument combinations
  - Verify error handling for invalid arguments
  - _Requirements: 14.1-14.8_

- [ ] 20. Validate environment variable configuration
  - Review environment variable reading for all cloud adapters
  - Test OpenAI API key checking
  - Test Google credentials checking
  - Test AWS credentials checking
  - Test Azure credentials checking
  - _Requirements: 15.1, 15.2, 15.3, 15.4_

- [x] 20.1 Write unit tests for environment variable handling
  - Test credential checking for all cloud adapters
  - Verify error messages for missing credentials
  - _Requirements: 15.1-15.4_

- [ ] 21. Final checkpoint - Comprehensive integration testing
  - Ensure all tests pass, ask the user if questions arise.

- [x] 21.1 Write integration tests for end-to-end pipeline
  - Test full pipeline with sample PDFs
  - Test multi-file processing
  - Test offline mode end-to-end
  - Test cloud adapter integration with mocks
  - Test cache behavior across runs

- [ ] 22. Create test corpus and fixtures
  - Assemble sample PDFs (native and scanned)
  - Create sample DOCX files
  - Generate expected output files (Turtle and JSON)
  - Create corrupted/invalid files for error testing
  - Document test data provenance

- [ ] 23. Update documentation for traceability
  - Update docs/requirements.md traceability matrix with test references
  - Document all implemented properties and their test locations
  - Create validation artifact references for each requirement
  - Ensure consistency between spec and implementation
