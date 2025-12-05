## pdf-grepper

Hybrid PDF intelligence to parse PDFs (incl. OCR), extract entities/relations/diagrams, infer domain, and export a fully articulated Turtle ontology.

- Local-first: PyMuPDF, Tesseract OCR, spaCy, OpenCV, rdflib
- Optional cloud add-ons: OpenAI IE, Google Vision/DocAI OCR, AWS Textract, Azure Read
- Multi-source: Accept multiple versions (native PDF, scanned PDF, OCR DOCX) and fuse results with provenance

### Install (uv)

```bash
uv venv
uv sync
# If you want enrichment and cloud add-ons:
uv add "pdf-grepper[openai,google,aws,azure,enrich]"
```

Ensure Tesseract is installed on your system and in PATH:
- macOS: `brew install tesseract`

Optional: spaCy model (offline-friendly fallback works without it)
```bash
python -m spacy download en_core_web_sm || true
```

### CLI usage

```bash
pdf-grepper parse input.pdf \
  --out model.ttl \
  --json model.json \
  --ocr auto \
  --cloud openai,google \
  --enrich-web \
  --cache .pgcache
```

Args:
- `--ocr`: none|local|auto (auto chooses OCR if page text is sparse)
- `--cloud`: comma-list of adapters: openai,google,aws,azure
- `--enrich-web`: optional web enrichment for domain inference and metadata
- `--offline`: disable all network

Environment:
- `OPENAI_API_KEY`
- `GOOGLE_APPLICATION_CREDENTIALS`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
- `AZURE_*` (per chosen SDK)

### Outputs
- Turtle ontology: classes and properties for document, sections, entities, relations, stakeholders, dimensions, diagrams, and provenance
- Optional JSON mirror for inspection

### Requirements and traceability
- See [docs/requirements.md](docs/requirements.md) for functional/non-functional requirements and the traceability matrix.

### Roadmap
- Improve diagram reverse engineering (node/edge association, swimlanes, chart axes)
- Add table structure recovery and CSV export
- Add domain-aligned mappings to schema.org/PROV-O when obvious

### License
MIT © 2025 nkllon


