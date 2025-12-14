from __future__ import annotations

from typing import List

from pdf_grepper.pipeline import _infer_domain_labels
from pdf_grepper.types import Page, TextSpan


# Feature: pdf-intelligence-system, Property 24: Domain label stop word filtering
def test_domain_labels_exclude_stop_words():
    # Build a page with many stop words and a couple meaningful terms
    text = "the and or is are was were be been being system architecture system"
    page = Page(index=0, text_blocks=[TextSpan(text=text)])
    labels = _infer_domain_labels([page], top_k=8)
    stop_words = {"the", "and", "or", "is", "are", "was", "were", "be", "been", "being"}
    assert not any(w in stop_words for w in labels)


# Feature: pdf-intelligence-system, Property 25: Domain label count limit
def test_domain_label_count_limit():
    # Create more than 8 distinct candidate terms; ensure result limited to <= 8
    words = [
        "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota", "kappa"
    ]
    text = " ".join(words) + " " + " ".join(words)  # duplicate to give TF-IDF some weight
    page = Page(index=0, text_blocks=[TextSpan(text=text)])
    labels = _infer_domain_labels([page], top_k=8)
    assert len(labels) <= 8

