# AI-DLC and Spec-Driven Development

Kiro-style Spec Driven Development implementation on AI-DLC (AI Development Life Cycle)

## Project Context

### Paths
- Steering: `.kiro/steering/`
- Specs: `.kiro/specs/`

### Steering vs Specification

**Steering** (`.kiro/steering/`) - Guide AI with project-wide rules and context
**Specs** (`.kiro/specs/`) - Formalize development process for individual features

### Active Specifications
- Check `.kiro/specs/` for active specifications
- Use `/kiro/spec-status [feature-name]` to check progress

## Development Guidelines
- Think in English, generate responses in English. All Markdown content written to project files (e.g., requirements.md, design.md, tasks.md, research.md, validation reports) MUST be written in the target language configured for this specification (see spec.json.language).

## Minimal Workflow
- Phase 0 (optional): `/kiro/steering`, `/kiro/steering-custom`
- Phase 1 (Specification):
  - `/kiro/spec-init "description"`
  - `/kiro/spec-requirements {feature}`
  - `/kiro/validate-gap {feature}` (optional: for existing codebase)
  - `/kiro/spec-design {feature} [-y]`
  - `/kiro/validate-design {feature}` (optional: design review)
  - `/kiro/spec-tasks {feature} [-y]`
- Phase 2 (Implementation): `/kiro/spec-impl {feature} [tasks]`
  - `/kiro/validate-impl {feature}` (optional: after implementation)
- Progress check: `/kiro/spec-status {feature}` (use anytime)

## Development Rules
- 3-phase approval workflow: Requirements → Design → Tasks → Implementation
- Human review required each phase; use `-y` only for intentional fast-track
- Keep steering current and verify alignment with `/kiro/spec-status`
- Follow the user's instructions precisely, and within that scope act autonomously: gather the necessary context and complete the requested work end-to-end in this run, asking questions only when essential information is missing or the instructions are critically ambiguous.

## Steering Configuration
- Load entire `.kiro/steering/` as project memory
- Default files: `product.md`, `tech.md`, `structure.md`
- Custom files are supported (managed via `/kiro/steering-custom`)

## Docker-first Development (required for dev)

Docker is the required and preferred environment for development and test execution. Avoid macOS-local dependency loops; always run commands inside the dev container.

### Build the dev image
```bash
docker build -t pdf-grepper-dev -f Dockerfile .
```

### Run the full test suite
```bash
docker run --rm -it \
  -v "$PWD":/app -w /app \
  pdf-grepper-dev \
  bash -lc "uv run pytest -q || .venv/bin/python -m pytest -q"
```

Notes:
- The image includes system libs (e.g., Tesseract, libGL) so OCR and PyMuPDF tests work reliably.
- The container tries `uv` first; if `pyproject.toml` parsing blocks `uv sync`, it falls back to preinstalled deps and plain `pytest`.

### Run a single test file
```bash
docker run --rm -it -v "$PWD":/app -w /app pdf-grepper-dev \
  bash -lc "uv run pytest -q tests/test_property_export_ttl.py || .venv/bin/python -m pytest -q tests/test_property_export_ttl.py"
```

### Run the CLI via Docker
```bash
docker run --rm -it -v "$PWD":/app -w /app pdf-grepper-dev \
  bash -lc "uv run pdf-grepper parse samples/sample.pdf --out model.ttl --offline True || pdf-grepper parse samples/sample.pdf --out model.ttl --offline True"
```

### Guidance and Approach
- Always prefer containerized runs for tests and CI parity.
- Agents implementing features MUST:
  1) Write tests first.
  2) Run tests in Docker.
  3) Make minimal code to pass, then refactor.
- If you need additional system packages, update the `Dockerfile` rather than relying on host installs.
