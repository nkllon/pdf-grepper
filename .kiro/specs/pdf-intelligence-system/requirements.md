# Requirements Document

## Introduction

The PDF Intelligence System (pdf-grepper) is a hybrid document processing system that ingests PDF documents (including scanned PDFs), performs optical character recognition (OCR), extracts structured information including entities, relations, diagrams, stakeholders, and business dimensions, and exports the results as a formal RDF ontology in Turtle format. The system supports both local-first processing using open-source tools and optional cloud-based enhancement services. It is designed to transform unstructured PDF documents into machine-readable knowledge graphs with full provenance tracking.

## Glossary

- **System**: The PDF Intelligence System (pdf-grepper)
- **User**: A person or automated process invoking the system via CLI
- **PDF Document**: A Portable Document Format file, either native (text-based) or scanned (image-based)
- **OCR**: Optical Character Recognition - the process of converting images of text into machine-readable text
- **Entity**: A named concept extracted from text (person, organization, product, location, etc.)
- **Relation**: A semantic connection between two entities (e.g., "uses", "depends on")
- **Stakeholder**: An actor or perspective identified in the document with associated claims
- **Dimension**: A measurable business or technical attribute (e.g., latency, throughput, cost)
- **Diagram**: A visual representation containing nodes and edges (flowcharts, architecture diagrams, etc.)
- **Turtle**: A textual syntax for RDF (Resource Description Framework) ontologies
- **Ontology**: A formal representation of knowledge as a set of concepts and relationships
- **Provenance**: Metadata tracking the source and location of extracted information
- **Cloud Adapter**: An optional integration with external services (OpenAI, Google Vision, AWS Textract, Azure Read)
- **Offline Mode**: Operation mode that prevents all network calls
- **Cache**: Local storage of intermediate processing results
- **Layout Parsing**: Analysis of document structure including text blocks and spatial coordinates
- **Domain Labels**: Key terms representing the subject matter of the document

## Requirements

### Requirement 1

**User Story:** As a user, I want to load PDF documents into the system, so that I can extract structured information from them.

#### Acceptance Criteria

1. WHEN a user provides one or more PDF file paths THEN the System SHALL load each PDF and extract page content
2. WHEN a user provides a scanned PDF THEN the System SHALL load the PDF and preserve image data for OCR processing
3. WHEN a user provides multiple input files THEN the System SHALL process all files and merge results with source provenance
4. WHEN a PDF file cannot be opened THEN the System SHALL report an error with the file path and reason
5. WHEN a user provides a DOCX file as an OCR variant THEN the System SHALL load the DOCX content and associate it with corresponding PDF pages

### Requirement 2

**User Story:** As a user, I want the system to automatically detect when OCR is needed, so that I can process both native and scanned PDFs without manual configuration.

#### Acceptance Criteria

1. WHEN the OCR mode is set to "auto" and a page contains sparse text THEN the System SHALL perform OCR on that page
2. WHEN the OCR mode is set to "local" THEN the System SHALL perform OCR on all pages using Tesseract
3. WHEN the OCR mode is set to "none" THEN the System SHALL extract only native text without performing OCR
4. WHEN Tesseract is not available in PATH and local OCR is required THEN the System SHALL report an error indicating Tesseract is missing
5. WHEN OCR is performed THEN the System SHALL include confidence scores with extracted text

### Requirement 3

**User Story:** As a user, I want to use cloud OCR services for higher accuracy, so that I can improve extraction quality for complex documents.

#### Acceptance Criteria

1. WHEN a user enables Google Vision cloud adapter THEN the System SHALL send page images to Google Vision API for OCR
2. WHEN a user enables AWS Textract cloud adapter THEN the System SHALL send page images to AWS Textract for OCR
3. WHEN a user enables Azure Read cloud adapter THEN the System SHALL send page images to Azure Read API for OCR
4. WHEN offline mode is enabled THEN the System SHALL skip all cloud adapter invocations
5. WHEN a cloud adapter fails THEN the System SHALL fall back to local results without terminating processing

### Requirement 4

**User Story:** As a user, I want the system to parse document layout, so that spatial information is preserved for downstream analysis.

#### Acceptance Criteria

1. WHEN a PDF page is loaded THEN the System SHALL extract text blocks with bounding box coordinates
2. WHEN text blocks are extracted THEN the System SHALL record page index and spatial coordinates for each block
3. WHEN multiple text blocks exist on a page THEN the System SHALL preserve reading order based on spatial layout
4. WHEN layout parsing fails for a page THEN the System SHALL continue processing remaining pages

### Requirement 5

**User Story:** As a user, I want the system to extract entities from document text, so that I can identify key concepts, people, and organizations.

#### Acceptance Criteria

1. WHEN text is available from pages THEN the System SHALL extract entities using NLP processing
2. WHEN spaCy is available with trained models THEN the System SHALL use spaCy NER to extract PERSON, ORG, GPE, PRODUCT, FAC, LOC, and EVENT entities
3. WHEN spaCy is not available THEN the System SHALL use regex heuristics to extract capitalized noun phrases as CONCEPT entities
4. WHEN an entity is extracted THEN the System SHALL assign a unique identifier and record source span provenance
5. WHEN duplicate entities are detected THEN the System SHALL deduplicate based on normalized text

### Requirement 6

**User Story:** As a user, I want the system to extract relations between entities, so that I can understand how concepts are connected.

#### Acceptance Criteria

1. WHEN entities are extracted THEN the System SHALL analyze text to identify relations between entity pairs
2. WHEN a relation is identified THEN the System SHALL record subject entity, predicate, object entity, and source span
3. WHEN a relation is extracted THEN the System SHALL assign a unique identifier and confidence score
4. WHEN cloud adapters are enabled THEN the System SHALL refine relations using cloud-based information extraction

### Requirement 7

**User Story:** As a user, I want the system to identify stakeholders and their perspectives, so that I can understand different viewpoints in the document.

#### Acceptance Criteria

1. WHEN text contains stakeholder references THEN the System SHALL extract actor names and associated claims
2. WHEN a stakeholder is identified THEN the System SHALL record actor, claim text, source span, and confidence score
3. WHEN a stakeholder is extracted THEN the System SHALL assign a unique identifier

### Requirement 8

**User Story:** As a user, I want the system to detect and interpret diagrams, so that I can extract structured information from visual representations.

#### Acceptance Criteria

1. WHEN a PDF page contains vector graphics THEN the System SHALL extract diagram primitives including shapes and lines
2. WHEN diagram primitives are extracted THEN the System SHALL interpret them as nodes and edges
3. WHEN a diagram node is identified THEN the System SHALL extract label text and assign a node type (process, entity, decision)
4. WHEN diagram edges are identified THEN the System SHALL record source node, target node, directionality, and optional labels
5. WHEN diagram interpretation fails THEN the System SHALL continue processing without terminating

### Requirement 9

**User Story:** As a user, I want the system to discover business dimensions, so that I can identify measurable attributes discussed in the document.

#### Acceptance Criteria

1. WHEN text is analyzed THEN the System SHALL identify dimension names such as latency, throughput, cost, and performance
2. WHEN a dimension is identified THEN the System SHALL extract associated values and units
3. WHEN a dimension is extracted THEN the System SHALL record name, value, unit, source span, and confidence score
4. WHEN a dimension is extracted THEN the System SHALL assign a unique identifier

### Requirement 10

**User Story:** As a user, I want the system to infer domain labels, so that I can understand the subject matter of the document.

#### Acceptance Criteria

1. WHEN pages are processed THEN the System SHALL compute TF-IDF scores across document text
2. WHEN TF-IDF scores are computed THEN the System SHALL extract top-ranked unigrams and bigrams as domain labels
3. WHEN domain labels are extracted THEN the System SHALL filter out English stop words
4. WHEN domain labels are extracted THEN the System SHALL return the top 8 terms by relevance score

### Requirement 11

**User Story:** As a user, I want to enrich extracted information with web search, so that I can augment document content with external knowledge.

#### Acceptance Criteria

1. WHEN web enrichment is enabled and domain labels exist THEN the System SHALL query web search APIs for each domain label
2. WHEN offline mode is enabled THEN the System SHALL skip web enrichment
3. WHEN web enrichment completes THEN the System SHALL record enrichment counts in document metadata
4. WHEN web enrichment fails THEN the System SHALL continue processing with local results only

### Requirement 12

**User Story:** As a user, I want the system to export results as a Turtle ontology, so that I can integrate with semantic web tools and knowledge graphs.

#### Acceptance Criteria

1. WHEN processing completes THEN the System SHALL serialize all extracted information to RDF Turtle format
2. WHEN exporting to Turtle THEN the System SHALL create URIs for documents, pages, entities, relations, stakeholders, dimensions, diagram nodes, and diagram edges
3. WHEN exporting to Turtle THEN the System SHALL include provenance metadata with source paths, page indices, and bounding boxes
4. WHEN exporting to Turtle THEN the System SHALL use standard vocabularies including RDF, RDFS, DCTERMS, and XSD
5. WHEN exporting to Turtle THEN the System SHALL write output to the specified file path

### Requirement 13

**User Story:** As a user, I want to export results as JSON, so that I can inspect and process results with standard tools.

#### Acceptance Criteria

1. WHEN a JSON output path is specified THEN the System SHALL serialize the document model to JSON format
2. WHEN exporting to JSON THEN the System SHALL include all entities, relations, stakeholders, dimensions, pages, and diagrams
3. WHEN exporting to JSON THEN the System SHALL write output to the specified file path

### Requirement 14

**User Story:** As a user, I want to configure the system via CLI arguments, so that I can control processing behavior without modifying code.

#### Acceptance Criteria

1. WHEN the user invokes the CLI THEN the System SHALL accept input file paths as positional arguments
2. WHEN the user invokes the CLI THEN the System SHALL accept --out flag to specify Turtle output path
3. WHEN the user invokes the CLI THEN the System SHALL accept --json flag to specify JSON output path
4. WHEN the user invokes the CLI THEN the System SHALL accept --ocr flag with values none, local, or auto
5. WHEN the user invokes the CLI THEN the System SHALL accept --cloud flag with comma-separated adapter names
6. WHEN the user invokes the CLI THEN the System SHALL accept --enrich-web flag to enable web enrichment
7. WHEN the user invokes the CLI THEN the System SHALL accept --offline flag to disable network calls
8. WHEN the user invokes the CLI THEN the System SHALL accept --base-uri flag to specify RDF namespace

### Requirement 15

**User Story:** As a user, I want to configure cloud services via environment variables, so that I can securely provide API credentials.

#### Acceptance Criteria

1. WHEN OpenAI adapter is enabled THEN the System SHALL read OPENAI_API_KEY from environment
2. WHEN Google Vision adapter is enabled THEN the System SHALL read GOOGLE_APPLICATION_CREDENTIALS from environment
3. WHEN AWS Textract adapter is enabled THEN the System SHALL read AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_REGION from environment
4. WHEN Azure adapters are enabled THEN the System SHALL read Azure credentials from environment per SDK requirements

### Requirement 16

**User Story:** As a user, I want the system to cache intermediate results, so that I can avoid redundant processing when re-running pipelines.

#### Acceptance Criteria

1. WHEN caching is enabled THEN the System SHALL store intermediate results in the specified cache directory
2. WHEN cached results exist for an input THEN the System SHALL reuse cached results instead of reprocessing
3. WHEN cache entries are created THEN the System SHALL include provenance metadata indicating cache source

### Requirement 17

**User Story:** As a user, I want the system to operate in offline mode, so that I can process documents without network access.

#### Acceptance Criteria

1. WHEN offline mode is enabled THEN the System SHALL skip all cloud adapter invocations
2. WHEN offline mode is enabled THEN the System SHALL skip web enrichment
3. WHEN offline mode is enabled THEN the System SHALL complete processing using only local capabilities
4. WHEN offline mode is enabled and local dependencies are missing THEN the System SHALL report an error

### Requirement 18

**User Story:** As a developer, I want the system to be extensible, so that I can add new cloud adapters and enrichment sources without modifying core logic.

#### Acceptance Criteria

1. WHEN a new cloud adapter is implemented THEN the System SHALL support it through the modular adapter interface
2. WHEN a new enrichment source is implemented THEN the System SHALL support it through the modular enrichment interface
3. WHEN adapter interfaces are defined THEN the System SHALL document expected input and output contracts

### Requirement 19

**User Story:** As a developer, I want the system to log pipeline operations, so that I can debug issues and audit processing steps.

#### Acceptance Criteria

1. WHEN pipeline steps execute THEN the System SHALL log step names and status
2. WHEN cloud adapters are invoked THEN the System SHALL log adapter names and invocation results
3. WHEN errors occur THEN the System SHALL log error messages with context
4. WHEN processing completes THEN the System SHALL log output file paths

### Requirement 20

**User Story:** As a user, I want the system to produce consistent results for the same inputs, so that I can rely on reproducible outputs.

#### Acceptance Criteria

1. WHEN the same inputs and configuration are provided THEN the System SHALL produce equivalent outputs
2. WHEN offline mode is enabled THEN the System SHALL produce deterministic results without network variability
3. WHEN random processes are used THEN the System SHALL use fixed seeds when determinism is required
