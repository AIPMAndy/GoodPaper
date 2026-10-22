"""Bound and validate untrusted Word OOXML uploads before parsing."""
from __future__ import annotations

import shutil
from pathlib import Path
from zipfile import BadZipFile, ZipFile

MAX_FILE_BYTES = 20 * 1024 * 1024
MAX_REQUEST_BYTES = 50 * 1024 * 1024
MAX_FILES = 10
MAX_ZIP_MEMBERS = 2500
MAX_UNCOMPRESSED_BYTES = 120 * 1024 * 1024


def validate_upload(source, destination: Path, *, kind: str = "paper") -> None:
    """Stream a bounded .docx into a unique temporary file and check ZIP metadata.

    ZIP size limits are a precaution, not a sandbox. Only use trusted template
    packages and never expose the built-in development server publicly.
    """
    if destination.suffix.lower() != ".docx":
        raise ValueError("Only .docx files are supported for this operation.")
    copied = 0
    with destination.open("xb") as sink:
        while True:
            block = source.read(256 * 1024)
            if not block:
                break
            copied += len(block)
            if copied > MAX_FILE_BYTES:
                raise ValueError("File exceeds the 20 MiB limit.")
            sink.write(block)
    if copied == 0:
        raise ValueError("Empty Word file.")
    try:
        with ZipFile(destination) as archive:
            infos = archive.infolist()
            if len(infos) > MAX_ZIP_MEMBERS:
                raise ValueError("Word file contains too many archive entries.")
            if sum(info.file_size for info in infos) > MAX_UNCOMPRESSED_BYTES:
                raise ValueError("Word file would expand beyond the safe limit.")
            if any(info.flag_bits & 1 for info in infos):
                raise ValueError("Encrypted archive entries are not supported.")
            names = {info.filename for info in infos}
            if "[Content_Types].xml" not in names or "word/document.xml" not in names:
                raise ValueError("Not a valid .docx Word document.")
    except BadZipFile as exc:
        raise ValueError("Invalid or damaged .docx archive.") from exc
