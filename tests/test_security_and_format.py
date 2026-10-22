"""Security and regression tests for Word uploads and list-preserving formatting."""
from __future__ import annotations
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import tempfile
import pytest

from goodpaper_mvp.upload_guard import validate_upload, MAX_FILE_BYTES
from goodpaper_mvp.core import merge_template_parts


def make_docx(data: bytes = b"sample", *, compressed_size: int = 0) -> BytesIO:
    buf = BytesIO()
    with ZipFile(buf, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", b"<Types/>")
        archive.writestr("word/document.xml", data)
    buf.seek(0)
    return buf


def test_upload_is_bounded_and_validated(tmp_path):
    good = tmp_path / "paper.docx"
    validate_upload(make_docx(), good)
    assert good.exists()
    with pytest.raises(ValueError, match="Only .docx"):
        validate_upload(make_docx(), tmp_path / "macro.docm")
    with pytest.raises(ValueError, match="Invalid"):
        validate_upload(BytesIO(b"not-a-word-file"), tmp_path / "broken.docx")
    with pytest.raises(ValueError, match="20 MiB"):
        validate_upload(BytesIO(b"x" * (MAX_FILE_BYTES + 1)), tmp_path / "big.docx")


def test_duplicate_paths_fail_closed(tmp_path):
    path=tmp_path/"same.docx"
    validate_upload(make_docx(),path)
    with pytest.raises(FileExistsError):
        validate_upload(make_docx(),path)


def test_merge_does_not_destroy_existing_numbering(tmp_path):
    template = tmp_path/"template.docx"
    source = tmp_path/"output.docx"
    with ZipFile(template, "w", ZIP_DEFLATED) as z:
        z.writestr("word/numbering.xml", b"TEMPLATE-NUMBERING")
        z.writestr("word/styles.xml", b'<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>')
    with ZipFile(source, "w", ZIP_DEFLATED) as z:
        z.writestr("word/numbering.xml", b"PAPER-NUMBERING")
        z.writestr("word/styles.xml", b'<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>')
    merge_template_parts(template,source)
    with ZipFile(source) as z:
        assert z.read("word/numbering.xml") == b"PAPER-NUMBERING"


def test_origin_guard_blocks_other_websites():
    from goodpaper_mvp.server import GoodPaperHandler
    class Dummy:
        headers={"Origin":"https://malicious.example"}
        class Server:
            server_address=("127.0.0.1",8787)
        server=Server()
    with pytest.raises(PermissionError):
        GoodPaperHandler._validate_local_origin(Dummy())
