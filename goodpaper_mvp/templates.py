from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class TemplatePackageLoadIssue:
    manifest_path: str
    error: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

from .core import SEMANTIC_STYLE_IDS, get_template_profile

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PACKAGES_DIR = PROJECT_ROOT / "template_packages"


@dataclass
class TemplatePackage:
    package_id: str
    name: str
    description: str
    version: str
    template_path: str
    manifest_path: str
    default: bool
    semantic_styles: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _load_manifest(manifest_path: Path) -> dict[str, Any]:
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _build_package(manifest_path: Path) -> TemplatePackage:
    manifest = _load_manifest(manifest_path)
    package_dir = manifest_path.parent
    template_file = manifest.get("template_file")
    if not template_file:
        raise ValueError(f"Package manifest missing template_file: {manifest_path}")
    template_path = (package_dir / template_file).resolve()
    if not template_path.exists():
        raise ValueError(f"Package template file not found: {template_path}")

    return TemplatePackage(
        package_id=manifest["package_id"],
        name=manifest.get("name", manifest["package_id"]),
        description=manifest.get("description", ""),
        version=manifest.get("version", "0.1"),
        template_path=str(template_path),
        manifest_path=str(manifest_path),
        default=bool(manifest.get("default", False)),
        semantic_styles=manifest.get("semantic_styles", dict(SEMANTIC_STYLE_IDS)),
    )


def discover_template_packages() -> dict[str, Any]:
    packages: list[TemplatePackage] = []
    issues: list[TemplatePackageLoadIssue] = []
    if not TEMPLATE_PACKAGES_DIR.exists():
        return {"packages": packages, "issues": issues}

    for manifest_path in sorted(TEMPLATE_PACKAGES_DIR.glob("*/manifest.json")):
        try:
            packages.append(_build_package(manifest_path))
        except Exception as exc:
            issues.append(
                TemplatePackageLoadIssue(
                    manifest_path=str(manifest_path),
                    error=str(exc),
                )
            )

    packages.sort(key=lambda item: (not item.default, item.package_id))
    return {"packages": packages, "issues": issues}


def list_template_packages() -> list[TemplatePackage]:
    return discover_template_packages()["packages"]


def get_template_package(package_id: str) -> TemplatePackage:
    for package in list_template_packages():
        if package.package_id == package_id:
            return package
    raise ValueError(f"Unknown template package '{package_id}'.")


def get_default_template_package() -> TemplatePackage:
    packages = list_template_packages()
    if not packages:
        raise ValueError(
            "No template packages are available. Provide --template with your own .docx/.docm template, or add a manifest under template_packages/."
        )
    for package in packages:
        if package.default:
            return package
    return packages[0]


def resolve_template_context(
    template_path: Path | None = None,
    package_id: str | None = None,
) -> dict[str, Any]:
    if template_path is not None:
        if not template_path.exists():
            raise ValueError(f"Template file not found: {template_path}")
        if template_path.suffix.lower() not in {".docx", ".docm", ".dotx", ".dotm"}:
            raise ValueError("Template file must be a .docx, .docm, .dotx, or .dotm Word template/document.")
        return {
            "template_path": template_path,
            "package": None,
            "semantic_styles": dict(SEMANTIC_STYLE_IDS),
        }

    try:
        package = get_template_package(package_id) if package_id else get_default_template_package()
    except ValueError as exc:
        raise ValueError(
            f"{exc} Upload a Word template with --template, or add a valid package under template_packages/."
        ) from exc
    return {
        "template_path": Path(package.template_path),
        "package": package.to_dict(),
        "semantic_styles": package.semantic_styles,
    }


def describe_template_package(package_id: str | None = None) -> dict[str, Any]:
    context = resolve_template_context(package_id=package_id)
    package = context["package"]
    profile = get_template_profile(context["template_path"], context["semantic_styles"])
    return {
        "package": package,
        "profile": {
            "template_path": str(context["template_path"]),
            "semantic_styles": profile["semantic_styles"],
            "paragraph_style_ids": profile["paragraph_style_ids"],
            "custom_paragraph_style_ids": profile["custom_paragraph_style_ids"],
        },
    }
