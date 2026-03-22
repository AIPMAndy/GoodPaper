from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile

from .core import analyze_document


def collect_batch_report(
    template_path: Path,
    paper_paths: list[Path],
    semantic_style_ids: dict[str, str] | None = None,
) -> dict[str, Any]:
    documents: list[dict[str, Any]] = []

    for paper_path in sorted(paper_paths, key=lambda item: item.name.lower()):
        report = analyze_document(template_path, paper_path, semantic_style_ids)
        documents.append(
            {
                "file_name": paper_path.name,
                "file_path": str(paper_path),
                "summary": report["summary"],
                "issue_count": len(report["issues"]),
                "issues": report["issues"],
            }
        )

    aggregate = {
        "document_count": len(documents),
        "documents_with_errors": sum(item["summary"]["error_count"] > 0 for item in documents),
        "documents_with_warnings": sum(item["summary"]["warn_count"] > 0 for item in documents),
        "total_errors": sum(item["summary"]["error_count"] for item in documents),
        "total_warnings": sum(item["summary"]["warn_count"] for item in documents),
        "total_infos": sum(item["summary"]["info_count"] for item in documents),
        "total_issues": sum(item["issue_count"] for item in documents),
    }

    return {
        "template_path": str(template_path),
        "documents": documents,
        "aggregate": aggregate,
    }


def _documents_csv(report: dict[str, Any]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "file_name",
            "error_count",
            "warn_count",
            "info_count",
            "issue_count",
        ],
    )
    writer.writeheader()
    for item in report["documents"]:
        writer.writerow(
            {
                "file_name": item["file_name"],
                "error_count": item["summary"]["error_count"],
                "warn_count": item["summary"]["warn_count"],
                "info_count": item["summary"]["info_count"],
                "issue_count": item["issue_count"],
            }
        )
    return output.getvalue()


def _issues_csv(report: dict[str, Any]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "file_name",
            "severity",
            "severity_label_zh",
            "code",
            "title_zh",
            "message",
            "why_zh",
            "fix_zh",
            "paragraph_index",
            "paragraph_text",
            "expected_style",
            "actual_style",
        ],
    )
    writer.writeheader()
    for item in report["documents"]:
        for issue in item["issues"]:
            writer.writerow(
                {
                    "file_name": item["file_name"],
                    "severity": issue["severity"],
                    "severity_label_zh": issue.get("severity_label_zh"),
                    "code": issue["code"],
                    "title_zh": issue.get("title_zh"),
                    "message": issue["message"],
                    "why_zh": issue.get("why_zh"),
                    "fix_zh": issue.get("fix_zh"),
                    "paragraph_index": issue.get("paragraph_index"),
                    "paragraph_text": issue.get("paragraph_text"),
                    "expected_style": issue.get("expected_style"),
                    "actual_style": issue.get("actual_style"),
                }
            )
    return output.getvalue()


def write_batch_report_files(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_json_path = output_dir / "summary.json"
    documents_csv_path = output_dir / "documents.csv"
    issues_csv_path = output_dir / "issues.csv"

    summary_json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    documents_csv_path.write_text(_documents_csv(report), encoding="utf-8")
    issues_csv_path.write_text(_issues_csv(report), encoding="utf-8")

    return {
        "summary_json": str(summary_json_path),
        "documents_csv": str(documents_csv_path),
        "issues_csv": str(issues_csv_path),
    }


def build_batch_report_zip(report: dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as archive:
        archive.writestr(
            "summary.json", json.dumps(report, ensure_ascii=False, indent=2).encode("utf-8")
        )
        archive.writestr("documents.csv", _documents_csv(report).encode("utf-8"))
        archive.writestr("issues.csv", _issues_csv(report).encode("utf-8"))
    return buffer.getvalue()
