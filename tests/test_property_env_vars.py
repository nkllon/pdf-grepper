import os
from importlib import reload

import pdf_grepper.cloud.google_vision as gv
import pdf_grepper.cloud.aws_textract as aws
import pdf_grepper.cloud.azure_read as azure
import pytest


def test_google_vision_available(monkeypatch):
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    reload(gv)
    assert gv.available() is False
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "/tmp/creds.json")
    reload(gv)
    assert gv.available() is True


def test_aws_textract_available(monkeypatch):
    monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
    monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)
    reload(aws)
    assert aws.available() is False
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "id")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "secret")
    reload(aws)
    assert aws.available() is True


def test_azure_read_available(monkeypatch):
    monkeypatch.delenv("AZURE_FORM_RECOGNIZER_ENDPOINT", raising=False)
    monkeypatch.delenv("AZURE_FORM_RECOGNIZER_KEY", raising=False)
    reload(azure)
    assert azure.available() is False
    monkeypatch.setenv("AZURE_FORM_RECOGNIZER_ENDPOINT", "https://example.azure.com")
    monkeypatch.setenv("AZURE_FORM_RECOGNIZER_KEY", "key")
    reload(azure)
    assert azure.available() is True

