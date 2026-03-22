from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import platform
import secrets
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .templates import get_default_template_package, get_template_package

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
VENDOR_CONFIG_PATH = CONFIG_DIR / "vendor.json"
VENDOR_EXAMPLE_PATH = CONFIG_DIR / "vendor.example.json"
LICENSE_DIR = PROJECT_ROOT / ".goodpaper"
LICENSE_FILE = LICENSE_DIR / "license.json"
DEVICE_ID_FILE = LICENSE_DIR / "device_id.txt"


@dataclass
class LicenseStatus:
    activated: bool
    reason: str
    package_id: str | None
    expires_on: str | None
    device_id: str | None
    activated_at: str | None
    code_masked: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def is_open_source_mode() -> bool:
    forced = os.environ.get("GOODPAPER_REQUIRE_ACTIVATION")
    if forced == "1":
        return False
    if forced == "0":
        return True

    env_secret = os.environ.get("GOODPAPER_VENDOR_SECRET")
    if env_secret:
        return False

    if not VENDOR_CONFIG_PATH.exists():
        return True

    try:
        payload = json.loads(VENDOR_CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return True

    secret = str(payload.get("secret", "")).strip()
    if not secret or secret == "replace-this-dev-secret-before-real-distribution":
        return True

    return False


def _load_vendor_config() -> dict[str, Any]:
    env_secret = os.environ.get("GOODPAPER_VENDOR_SECRET")
    if env_secret:
        return {
            "issuer": os.environ.get("GOODPAPER_ISSUER", "GoodPaper"),
            "secret": env_secret,
        }

    if not VENDOR_CONFIG_PATH.exists():
        raise ValueError(
            f"Vendor config not found: {VENDOR_CONFIG_PATH}. Set GOODPAPER_VENDOR_SECRET or create config/vendor.json."
        )
    return json.loads(VENDOR_CONFIG_PATH.read_text(encoding="utf-8"))


def current_device_id() -> str:
    LICENSE_DIR.mkdir(parents=True, exist_ok=True)
    if DEVICE_ID_FILE.exists():
        return DEVICE_ID_FILE.read_text(encoding="utf-8").strip()

    raw = "|".join(
        [
            platform.system(),
            platform.machine(),
            platform.platform(),
            str(Path.home()),
        ]
    )
    device_id = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    DEVICE_ID_FILE.write_text(device_id, encoding="utf-8")
    return device_id


def _signature(secret: str, payload: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).digest()
    return base64.b32encode(digest).decode("ascii").rstrip("=").upper()[:10]


def issue_invite_code(
    package_id: str | None = None,
    days: int = 30,
    serial: str | None = None,
) -> dict[str, Any]:
    package = get_template_package(package_id) if package_id else get_default_template_package()
    vendor = _load_vendor_config()
    expires_on = (utc_now() + timedelta(days=days)).strftime("%Y%m%d")
    serial = (serial or secrets.token_hex(3)).upper()
    payload = f"{package.package_id}|{expires_on}|{serial}"
    sig = _signature(vendor["secret"], payload)
    code = f"GP-{package.package_id.upper()}-{expires_on}-{serial}-{sig}"
    return {
        "issuer": vendor.get("issuer", "GoodPaper"),
        "package_id": package.package_id,
        "package_name": package.name,
        "expires_on": expires_on,
        "serial": serial,
        "code": code,
    }


def parse_invite_code(code: str) -> dict[str, str]:
    parts = (code or "").strip().split("-")
    if len(parts) != 5 or parts[0] != "GP":
        raise ValueError("Invalid invite code format.")
    return {
        "package_id": parts[1].lower(),
        "expires_on": parts[2],
        "serial": parts[3],
        "signature": parts[4],
    }


def validate_invite_code(code: str) -> dict[str, Any]:
    vendor = _load_vendor_config()
    parsed = parse_invite_code(code)
    try:
        get_template_package(parsed["package_id"])
    except ValueError as exc:
        raise ValueError(str(exc)) from exc

    payload = f'{parsed["package_id"]}|{parsed["expires_on"]}|{parsed["serial"]}'
    expected = _signature(vendor["secret"], payload)
    if not hmac.compare_digest(expected, parsed["signature"]):
        raise ValueError("Invalid invite code signature.")

    expires_dt = datetime.strptime(parsed["expires_on"], "%Y%m%d").replace(tzinfo=timezone.utc)
    if expires_dt < utc_now().replace(hour=0, minute=0, second=0, microsecond=0):
        raise ValueError("Invite code has expired.")

    return parsed


def _mask_code(code: str) -> str:
    if len(code) <= 8:
        return code
    return f"{code[:6]}...{code[-4:]}"


def activate_invite_code(code: str, license_path: Path = LICENSE_FILE) -> dict[str, Any]:
    parsed = validate_invite_code(code)
    license_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "code": code,
        "code_masked": _mask_code(code),
        "package_id": parsed["package_id"],
        "expires_on": parsed["expires_on"],
        "serial": parsed["serial"],
        "device_id": current_device_id(),
        "activated_at": utc_now().isoformat(),
    }
    license_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def get_license_status(license_path: Path = LICENSE_FILE) -> LicenseStatus:
    if is_open_source_mode():
        return LicenseStatus(
            activated=True,
            reason="open_source_mode",
            package_id=None,
            expires_on=None,
            device_id=current_device_id(),
            activated_at=None,
            code_masked=None,
        )

    if not license_path.exists():
        return LicenseStatus(
            activated=False,
            reason="not_activated",
            package_id=None,
            expires_on=None,
            device_id=None,
            activated_at=None,
            code_masked=None,
        )

    payload = json.loads(license_path.read_text(encoding="utf-8"))
    try:
        validate_invite_code(payload["code"])
    except Exception as exc:
        return LicenseStatus(
            activated=False,
            reason=f"invalid_license:{exc}",
            package_id=payload.get("package_id"),
            expires_on=payload.get("expires_on"),
            device_id=payload.get("device_id"),
            activated_at=payload.get("activated_at"),
            code_masked=payload.get("code_masked"),
        )

    if payload.get("device_id") != current_device_id():
        return LicenseStatus(
            activated=False,
            reason="device_mismatch",
            package_id=payload.get("package_id"),
            expires_on=payload.get("expires_on"),
            device_id=payload.get("device_id"),
            activated_at=payload.get("activated_at"),
            code_masked=payload.get("code_masked"),
        )

    return LicenseStatus(
        activated=True,
        reason="ok",
        package_id=payload.get("package_id"),
        expires_on=payload.get("expires_on"),
        device_id=payload.get("device_id"),
        activated_at=payload.get("activated_at"),
        code_masked=payload.get("code_masked"),
    )


def require_activation() -> LicenseStatus:
    status = get_license_status()
    if not status.activated:
        raise PermissionError(
            f"GoodPaper is not activated: {status.reason}. Use 'python3 app.py activate --code <INVITE_CODE>'."
        )
    return status
