import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _install_stub_fitz():
    if "fitz" in sys.modules:
        return
    stub = types.ModuleType("fitz")

    class _StubDocument:
        def __init__(self, *args, **kwargs):
            self.pages = []

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def __iter__(self):
            return iter(self.pages)

        def __len__(self):
            return len(self.pages)

        def __getitem__(self, idx):
            return self.pages[idx]

        def close(self):
            return None

    def _open(*args, **kwargs):
        return _StubDocument()

    stub.open = _open
    sys.modules["fitz"] = stub


def _install_stub_sklearn():
    if "sklearn" in sys.modules:
        return
    sklearn_mod = types.ModuleType("sklearn")
    feature_mod = types.ModuleType("sklearn.feature_extraction")
    text_mod = types.ModuleType("sklearn.feature_extraction.text")

    class TfidfVectorizer:
        def __init__(self, *args, **kwargs):
            self._terms: list[str] = []

        def fit_transform(self, docs):
            seen = []
            for doc in docs:
                for tok in doc.split():
                    tok = tok.strip().lower()
                    if not tok:
                        continue
                    if tok not in seen:
                        seen.append(tok)
            self._terms = seen

            class _DummySum:
                def __init__(self, data):
                    self.A1 = data

            class _DummyMatrix:
                def sum(self, axis=0):
                    return _DummySum([1.0 for _ in seen])

            return _DummyMatrix()

        def get_feature_names_out(self):
            return self._terms

    text_mod.TfidfVectorizer = TfidfVectorizer
    feature_mod.text = text_mod
    sklearn_mod.feature_extraction = feature_mod
    sys.modules["sklearn"] = sklearn_mod
    sys.modules["sklearn.feature_extraction"] = feature_mod
    sys.modules["sklearn.feature_extraction.text"] = text_mod


def _install_stub_docx():
    if "docx" in sys.modules:
        return
    docx_mod = types.ModuleType("docx")

    class _Paragraph:
        def __init__(self, text: str):
            self.text = text

    class Document:
        def __init__(self, path: str | None = None):
            self.paragraphs: list[_Paragraph] = []
            if path:
                try:
                    content = Path(path).read_text(encoding="utf-8")
                    for line in content.splitlines():
                        self.paragraphs.append(_Paragraph(line))
                except FileNotFoundError:
                    pass

        def add_paragraph(self, text: str):
            para = _Paragraph(text)
            self.paragraphs.append(para)
            return para

        def save(self, path: str):
            Path(path).write_text("\n".join(p.text for p in self.paragraphs), encoding="utf-8")

    docx_mod.Document = Document
    sys.modules["docx"] = docx_mod


def _install_stub_rdflib():
    if "rdflib" in sys.modules:
        return
    rdflib_mod = types.ModuleType("rdflib")
    ns_mod = types.ModuleType("rdflib.namespace")

    class URIRef(str):
        pass

    class Namespace(str):
        def __getattr__(self, item):
            return URIRef(f"{self}{item}")

        def __call__(self, suffix):
            return URIRef(f"{self}{suffix}")

    class Literal(str):
        def __new__(cls, value, datatype=None):
            return str.__new__(cls, str(value))

    class Graph:
        def __init__(self):
            self.triples = []

        def add(self, triple):
            self.triples.append(triple)

        def bind(self, prefix, namespace):
            return None

        def serialize(self, destination=None, format=None):
            content = "\n".join(f"{s} {p} {o}" for s, p, o in self.triples)
            if destination:
                Path(destination).write_text(content, encoding="utf-8")
            return content

    RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    DCTERMS = Namespace("http://purl.org/dc/terms/")
    XSD = Namespace("http://www.w3.org/2001/XMLSchema#")

    rdflib_mod.Graph = Graph
    rdflib_mod.Literal = Literal
    rdflib_mod.Namespace = Namespace
    rdflib_mod.RDF = RDF
    rdflib_mod.RDFS = RDFS
    rdflib_mod.URIRef = URIRef
    ns_mod.DCTERMS = DCTERMS
    ns_mod.XSD = XSD
    rdflib_mod.namespace = ns_mod
    sys.modules["rdflib"] = rdflib_mod
    sys.modules["rdflib.namespace"] = ns_mod


def _install_stub_pil():
    if "PIL" in sys.modules:
        return
    pil_mod = types.ModuleType("PIL")
    image_mod = types.ModuleType("PIL.Image")

    class Image:
        def __init__(self, *args, **kwargs):
            pass

        @classmethod
        def frombytes(cls, *args, **kwargs):
            return cls()

    image_mod.Image = Image
    pil_mod.Image = Image
    sys.modules["PIL"] = pil_mod
    sys.modules["PIL.Image"] = image_mod


def _install_stub_pytesseract():
    if "pytesseract" in sys.modules:
        return
    pytesseract_mod = types.ModuleType("pytesseract")

    def image_to_string(image, lang=None, config=None):
        return ""

    pytesseract_mod.image_to_string = image_to_string
    sys.modules["pytesseract"] = pytesseract_mod


@pytest.fixture(scope="session", autouse=True)
def install_stubs():
    """Install lightweight stubs for heavy optional dependencies."""
    _install_stub_fitz()
    _install_stub_sklearn()
    _install_stub_docx()
    _install_stub_rdflib()
    _install_stub_pil()
    _install_stub_pytesseract()
    yield


# Ensure stubs are in place during test collection, before pipeline imports occur.
_install_stub_fitz()
_install_stub_sklearn()
_install_stub_docx()
_install_stub_rdflib()
_install_stub_pil()
_install_stub_pytesseract()
