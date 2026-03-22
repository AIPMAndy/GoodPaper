from __future__ import annotations

import base64
import cgi
import json
import tempfile
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .core import analyze_document, format_document
from .licensing import activate_invite_code, get_license_status, require_activation
from .reports import build_batch_report_zip, collect_batch_report
from .templates import (
    get_default_template_package,
    list_template_packages,
    resolve_template_context,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML_PATH = PROJECT_ROOT / "goodpaper_mvp" / "static" / "index.html"


class GoodPaperHandler(BaseHTTPRequestHandler):
    server_version = "GoodPaper_Beta/0.1"

    def do_GET(self) -> None:
        try:
            parsed = urlparse(self.path)
            if parsed.path == "/":
                self._serve_index()
                return
            if parsed.path == "/api/health":
                self._send_json(
                    {
                        "status": "ok",
                        "license": get_license_status().to_dict(),
                    }
                )
                return
            if parsed.path == "/api/status":
                self._send_json(self._status_payload())
                return
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
        except Exception as exc:
            self._send_json_error(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))

    def do_POST(self) -> None:
        try:
            parsed = urlparse(self.path)
            if parsed.path == "/api/activate":
                self._handle_activate()
                return
            if parsed.path == "/api/check":
                self._handle_check()
                return
            if parsed.path == "/api/format":
                self._handle_format()
                return
            if parsed.path == "/api/check-and-format":
                self._handle_check_and_format()
                return
            if parsed.path == "/api/batch-check":
                self._handle_batch_check()
                return
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
        except ValueError as exc:
            self._send_json_error(HTTPStatus.BAD_REQUEST, str(exc))
        except PermissionError as exc:
            self._send_json_error(HTTPStatus.FORBIDDEN, str(exc))
        except Exception as exc:
            self._send_json_error(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))

    def _serve_index(self) -> None:
        content = INDEX_HTML_PATH.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _handle_check(self) -> None:
        require_activation()
        with tempfile.TemporaryDirectory(prefix="goodpaper-check-") as temp_dir:
            temp_root = Path(temp_dir)
            fields = self._parse_form_data()
            context = self._resolve_template_for_request(fields, temp_root)
            template_path = context["template_path"]
            paper_path = self._resolve_upload(fields, "paper", temp_root)

            report = analyze_document(
                template_path,
                paper_path,
                context["semantic_styles"],
            )
            report["package"] = context["package"]
            self._send_json(report)

    def _handle_format(self) -> None:
        require_activation()
        with tempfile.TemporaryDirectory(prefix="goodpaper-format-") as temp_dir:
            temp_root = Path(temp_dir)
            fields = self._parse_form_data()
            context = self._resolve_template_for_request(fields, temp_root)
            template_path = context["template_path"]
            paper_path = self._resolve_upload(fields, "paper", temp_root)

            output_path = temp_root / f"{paper_path.stem}-formatted.docx"
            result = format_document(
                template_path,
                paper_path,
                output_path,
                context["semantic_styles"],
            )
            payload = output_path.read_bytes()

            self.send_response(HTTPStatus.OK)
            self.send_header(
                "Content-Type",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            self.send_header(
                "Content-Disposition",
                f'attachment; filename="{Path(result["output_path"]).name}"',
            )
            self.send_header("X-GoodPaper-Change-Count", str(result["change_count"]))
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    def _handle_check_and_format(self) -> None:
        require_activation()
        with tempfile.TemporaryDirectory(prefix="goodpaper-check-format-") as temp_dir:
            temp_root = Path(temp_dir)
            fields = self._parse_form_data()
            context = self._resolve_template_for_request(fields, temp_root)
            template_path = context["template_path"]
            paper_path = self._resolve_upload(fields, "paper", temp_root)

            before = analyze_document(
                template_path,
                paper_path,
                context["semantic_styles"],
            )
            output_path = temp_root / f"{paper_path.stem}-formatted.docx"
            formatted = format_document(
                template_path,
                paper_path,
                output_path,
                context["semantic_styles"],
            )
            after = analyze_document(
                template_path,
                output_path,
                context["semantic_styles"],
            )
            payload = {
                "before": before,
                "formatted": formatted,
                "after": after,
                "package": context["package"],
                "download_name": Path(formatted["output_path"]).name,
                "document_base64": base64.b64encode(output_path.read_bytes()).decode("ascii"),
            }
            self._send_json(payload)

    def _handle_batch_check(self) -> None:
        require_activation()
        with tempfile.TemporaryDirectory(prefix="goodpaper-batch-") as temp_dir:
            temp_root = Path(temp_dir)
            fields = self._parse_form_data()
            context = self._resolve_template_for_request(fields, temp_root)
            paper_paths = self._resolve_uploads(fields, "papers", temp_root)
            if not paper_paths:
                raise ValueError("Missing upload field 'papers'.")

            report = collect_batch_report(
                context["template_path"],
                paper_paths,
                context["semantic_styles"],
            )
            report["package"] = context["package"]
            payload = build_batch_report_zip(report)

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/zip")
            self.send_header(
                "Content-Disposition",
                'attachment; filename="goodpaper-batch-report.zip"',
            )
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    def _handle_activate(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        payload = json.loads(raw or "{}")
        code = (payload.get("code") or "").strip()
        if not code:
            raise ValueError("Missing activation code.")
        activation = activate_invite_code(code)
        self._send_json(
            {
                "message": "Activation successful.",
                "activation": activation,
                "status": self._status_payload(),
            }
        )

    def _parse_form_data(self) -> cgi.FieldStorage:
        return cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": self.headers.get("Content-Type", ""),
            },
        )

    def _resolve_upload(
        self,
        fields: cgi.FieldStorage,
        field_name: str,
        temp_root: Path,
        optional: bool = False,
    ) -> Path | None:
        field = fields[field_name] if field_name in fields else None
        if field is None or not getattr(field, "filename", ""):
            if optional:
                return None
            raise ValueError(f"Missing upload field '{field_name}'.")

        safe_name = Path(field.filename).name
        target_path = temp_root / safe_name
        target_path.write_bytes(field.file.read())
        return target_path

    def _resolve_uploads(
        self,
        fields: cgi.FieldStorage,
        field_name: str,
        temp_root: Path,
    ) -> list[Path]:
        if field_name not in fields:
            return []
        raw_fields = fields[field_name]
        field_items = raw_fields if isinstance(raw_fields, list) else [raw_fields]
        resolved: list[Path] = []
        for field in field_items:
            if not getattr(field, "filename", ""):
                continue
            safe_name = Path(field.filename).name
            target_path = temp_root / safe_name
            target_path.write_bytes(field.file.read())
            resolved.append(target_path)
        return resolved

    def _resolve_text_field(
        self,
        fields: cgi.FieldStorage,
        field_name: str,
        optional: bool = False,
    ) -> str | None:
        if field_name not in fields:
            if optional:
                return None
            raise ValueError(f"Missing field '{field_name}'.")
        field = fields[field_name]
        if isinstance(field, list):
            field = field[0]
        value = getattr(field, "value", None)
        if value is None or str(value).strip() == "":
            if optional:
                return None
            raise ValueError(f"Missing field '{field_name}'.")
        return str(value).strip()

    def _resolve_template_for_request(
        self,
        fields: cgi.FieldStorage,
        temp_root: Path,
    ) -> dict:
        template_path = self._resolve_upload(fields, "template", temp_root, optional=True)
        package_id = self._resolve_text_field(fields, "package_id", optional=True)
        return resolve_template_context(template_path=template_path, package_id=package_id)

    def _status_payload(self) -> dict:
        packages = [package.to_dict() for package in list_template_packages()]
        default_package_id = None
        try:
            default_package_id = get_default_template_package().package_id
        except Exception:
            default_package_id = None
        return {
            "license": get_license_status().to_dict(),
            "packages": packages,
            "default_package_id": default_package_id,
        }

    def _send_json(self, payload: dict) -> None:
        data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json_error(self, status: HTTPStatus, message: str) -> None:
        data = json.dumps({"error": message}, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args) -> None:
        return


def run_server(host: str = "127.0.0.1", port: int = 8765) -> None:
    server = ThreadingHTTPServer((host, port), GoodPaperHandler)
    print(f"GoodPaper_Beta listening at http://{host}:{port}")
    server.serve_forever()
