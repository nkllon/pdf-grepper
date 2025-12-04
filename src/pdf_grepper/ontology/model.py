from __future__ import annotations

from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import DCTERMS, XSD


class OntologyContext:
	"""RDF namespaces and helpers."""

	def __init__(self, base_uri: str = "http://example.org/pdf-grepper/"):
		self.pg = Namespace(base_uri + "pg#")
		self.dom = Namespace(base_uri + "dom#")
		self.schema = Namespace("http://schema.org/")
		self.prov = Namespace("http://www.w3.org/ns/prov#")

	def bind(self, g: Graph) -> None:
		g.bind("pg", self.pg)
		g.bind("dom", self.dom)
		g.bind("schema", self.schema)
		g.bind("prov", self.prov)
		g.bind("dcterms", DCTERMS)
		g.bind("rdfs", RDFS)
		g.bind("xsd", XSD)


def make_graph(base_uri: str = "http://example.org/pdf-grepper/") -> tuple[Graph, OntologyContext]:
	g = Graph()
	ctx = OntologyContext(base_uri=base_uri)
	ctx.bind(g)
	return g, ctx


