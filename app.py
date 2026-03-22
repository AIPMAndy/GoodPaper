from __future__ import annotations

import argparse
from pathlib import Path

from goodpaper_mvp.core import analyze_document, format_document, to_pretty_json
from goodpaper_mvp.licensing import (
    activate_invite_code,
    get_license_status,
    issue_invite_code,
    require_activation,
)
from goodpaper_mvp.reports import collect_batch_report, write_batch_report_files
from goodpaper_mvp.server import run_server
from goodpaper_mvp.templates import discover_template_packages, resolve_template_context


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GoodPaper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    serve_parser = subparsers.add_parser("serve", help="Run the local web app")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8765)

    packages_parser = subparsers.add_parser("list-packages", help="List available template packages")

    issue_parser = subparsers.add_parser("issue-code", help="Issue a local invite code")
    issue_parser.add_argument("--package", dest="package_id")
    issue_parser.add_argument("--days", type=int, default=30)
    issue_parser.add_argument("--serial")

    activate_parser = subparsers.add_parser("activate", help="Activate this Mac using an invite code")
    activate_parser.add_argument("--code", required=True)

    subparsers.add_parser("license-status", help="Show local activation status")

    check_parser = subparsers.add_parser("check", help="Analyze a manuscript")
    check_parser.add_argument("--paper", required=True, type=Path)
    check_parser.add_argument("--template", type=Path)
    check_parser.add_argument("--package", dest="package_id")

    format_parser = subparsers.add_parser("format", help="Create a basic formatted .docx")
    format_parser.add_argument("--paper", required=True, type=Path)
    format_parser.add_argument("--output", required=True, type=Path)
    format_parser.add_argument("--template", type=Path)
    format_parser.add_argument("--package", dest="package_id")

    check_format_parser = subparsers.add_parser(
        "check-and-format",
        help="Analyze a manuscript, create a formatted .docx, and re-check the result",
    )
    check_format_parser.add_argument("--paper", required=True, type=Path)
    check_format_parser.add_argument("--output", required=True, type=Path)
    check_format_parser.add_argument("--template", type=Path)
    check_format_parser.add_argument("--package", dest="package_id")

    batch_parser = subparsers.add_parser(
        "batch-check", help="Analyze all manuscripts in a folder and export reports"
    )
    batch_parser.add_argument("--input-dir", required=True, type=Path)
    batch_parser.add_argument("--output-dir", required=True, type=Path)
    batch_parser.add_argument("--template", type=Path)
    batch_parser.add_argument("--package", dest="package_id")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "serve":
        run_server(host=args.host, port=args.port)
        return

    if args.command == "list-packages":
        discovery = discover_template_packages()
        payload = {
            "packages": [package.to_dict() for package in discovery["packages"]],
            "issues": [issue.to_dict() for issue in discovery["issues"]],
        }
        print(to_pretty_json(payload))
        return

    if args.command == "issue-code":
        payload = issue_invite_code(
            package_id=args.package_id,
            days=args.days,
            serial=args.serial,
        )
        print(to_pretty_json(payload))
        return

    if args.command == "activate":
        payload = activate_invite_code(args.code)
        print(to_pretty_json(payload))
        return

    if args.command == "license-status":
        print(to_pretty_json(get_license_status().to_dict()))
        return

    if args.command == "check":
        require_activation()
        context = resolve_template_context(template_path=args.template, package_id=args.package_id)
        payload = analyze_document(
            context["template_path"],
            args.paper,
            context["semantic_styles"],
        )
        payload["package"] = context["package"]
        print(to_pretty_json(payload))
        return

    if args.command == "format":
        require_activation()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        context = resolve_template_context(template_path=args.template, package_id=args.package_id)
        payload = format_document(
            context["template_path"],
            args.paper,
            args.output,
            context["semantic_styles"],
        )
        payload["package"] = context["package"]
        print(to_pretty_json(payload))
        return

    if args.command == "check-and-format":
        require_activation()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        context = resolve_template_context(template_path=args.template, package_id=args.package_id)
        before = analyze_document(
            context["template_path"],
            args.paper,
            context["semantic_styles"],
        )
        formatted = format_document(
            context["template_path"],
            args.paper,
            args.output,
            context["semantic_styles"],
        )
        after = analyze_document(
            context["template_path"],
            args.output,
            context["semantic_styles"],
        )
        payload = {
            "before": before,
            "formatted": formatted,
            "after": after,
            "package": context["package"],
        }
        print(to_pretty_json(payload))
        return

    if args.command == "batch-check":
        require_activation()
        args.output_dir.mkdir(parents=True, exist_ok=True)
        context = resolve_template_context(template_path=args.template, package_id=args.package_id)
        paper_paths = sorted(
            [
                path
                for path in args.input_dir.iterdir()
                if path.is_file() and path.suffix.lower() in {".docx", ".docm"}
            ]
        )
        payload = collect_batch_report(
            context["template_path"],
            paper_paths,
            context["semantic_styles"],
        )
        payload["package"] = context["package"]
        files = write_batch_report_files(payload, args.output_dir)
        print(to_pretty_json({"report": payload, "files": files}))
        return

    parser.error("Unsupported command.")


if __name__ == "__main__":
    main()
