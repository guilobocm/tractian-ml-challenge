import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.downloader import sanitize_filename, get_file_extension


def test_sanitize_filename_replaces_invalid_chars():
    original = 'bad<name>:with|chars?*'
    sanitized = sanitize_filename(original)
    assert sanitized == 'bad_name__with_chars__'
    for ch in '<>:"/\\|?*':
        assert ch not in sanitized


def test_get_file_extension_from_url():
    url = 'https://example.com/files/document.pdf'
    assert get_file_extension(url) == '.pdf'


def test_get_file_extension_extensionless_manual():
    url = 'https://example.com/downloads/manual'
    assert get_file_extension(url) == '.pdf'


def test_get_file_extension_extensionless_cad():
    url = 'https://example.com/assets/cad/model'
    assert get_file_extension(url) == '.dwg'

