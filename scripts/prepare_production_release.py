from __future__ import annotations

import argparse
import hashlib
import re
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PRIVATE_OUTPUT = ROOT / "build" / "ittemmall-private" / "ittemmall-server-config.php"
DEFAULT_BACKUP_DIR = ROOT / "build" / "release-backups"
RELEASE_SOURCE_FILES = [
    ROOT / "legal" / "business.html",
    ROOT / "legal" / "terms.html",
    ROOT / "legal" / "privacy.html",
    ROOT / "legal" / "refund.html",
    ROOT / "payment" / "naverpay-config.js",
]

LEGAL_FIELDS = [
    "representative",
    "business_registration_number",
    "ecommerce_license",
    "business_address",
    "privacy_officer",
    "shipping_carrier",
    "shipping_fee",
    "shipping_days",
    "return_address",
]

PLACEHOLDER_MARKERS = [
    "YOUR_",
    "PUBLIC_",
    "NAVER_PAY_",
    "ISSUED_",
    "ISSUED-",
    "REPLACE",
    "TODO",
    "EXAMPLE",
    "000-00-00000",
    "제0000-지역-0000호",
    "/ABSOLUTE/PRIVATE/PATH",
    "대표자명",
    "사업장 주소",
    "개인정보 책임자명",
    "택배사명",
    "반품 주소",
]


def load_json_config(path: str) -> dict:
    config_path = Path(path).expanduser().resolve()
    data = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("--config must point to a JSON object.")
    return data


def value(config: dict, path: str, default: str = "") -> str:
    cursor = config
    for part in path.split("."):
        if not isinstance(cursor, dict) or part not in cursor:
            return default
        cursor = cursor[part]
    return "" if cursor is None else str(cursor)


def looks_placeholder(raw: str) -> bool:
    normalized = raw.strip()
    upper = normalized.upper()
    if not normalized:
        return False
    return any(marker in upper or marker in normalized for marker in PLACEHOLDER_MARKERS)


def flag(config: dict, path: str, default: bool = False) -> bool:
    raw = value(config, path, "1" if default else "0").strip().lower()
    return raw in {"1", "true", "yes", "y", "on"}


def required(config: dict, path: str) -> str:
    raw = value(config, path).strip()
    if not raw:
        raise ValueError(f"Missing required config value: {path}")
    if looks_placeholder(raw):
        raise ValueError(f"Replace example config value before release: {path}")
    return raw


def require_choice(config: dict, path: str, allowed: set[str], default: str = "") -> str:
    raw = value(config, path, default).strip()
    if raw not in allowed:
        raise ValueError(f"{path} must be one of: {', '.join(sorted(allowed))}")
    return raw


def require_https_url(config: dict, path: str, default: str = "", *, allow_empty: bool = False) -> str:
    raw = value(config, path, default).strip()
    if raw == "" and allow_empty:
        return raw
    if not raw:
        raise ValueError(f"Missing required config value: {path}")
    if looks_placeholder(raw):
        raise ValueError(f"Replace example config value before release: {path}")
    parsed = urlparse(raw)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"{path} must be a full HTTPS URL.")
    return raw.rstrip("/")


def require_absolute_private_path(config: dict, path: str, *, allow_empty: bool = False) -> str:
    raw = value(config, path).strip()
    if raw == "" and allow_empty:
        return raw
    if not raw:
        raise ValueError(f"Missing required config value: {path}")
    if looks_placeholder(raw):
        raise ValueError(f"Replace example config value before release: {path}")
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        raise ValueError(f"{path} must be an absolute private server path.")
    forbidden_parts = {"public_html", "www", "htdocs", "ittemmall-public"}
    if forbidden_parts & set(candidate.parts):
        raise ValueError(f"{path} must stay outside the public web root.")
    return raw


def require_email(config: dict, path: str, *, allow_empty: bool = False) -> str:
    raw = value(config, path).strip()
    if raw == "" and allow_empty:
        return raw
    if not raw:
        raise ValueError(f"Missing required config value: {path}")
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", raw):
        raise ValueError(f"{path} must be an email address.")
    return raw


def validate_release_config(config: dict, *, allow_development_mode: bool, skip_private: bool) -> None:
    origin = require_https_url(config, "site.origin", "https://ittemmall.com")
    base_url = require_https_url(config, "site.base_url", origin)
    if origin.rstrip("/") != base_url.rstrip("/"):
        raise ValueError("site.origin and site.base_url must match for production release.")

    for field in LEGAL_FIELDS:
        required(config, f"legal.{field}")

    require_absolute_private_path(config, "server.order_store_path")
    require_absolute_private_path(config, "server.track_log_path", allow_empty=True)
    require_absolute_private_path(config, "server.rate_limit_path", allow_empty=True)
    required(config, "naver_pay.client_id")
    required(config, "naver_pay.chain_id")
    if not skip_private:
        required(config, "naver_pay.client_secret")
    mode = require_choice(config, "naver_pay.mode", {"development", "production"}, "production")
    if mode != "production" and not allow_development_mode:
        raise ValueError("naver_pay.mode must be production. Pass --allow-development-mode only for review/sandbox runs.")
    require_choice(config, "naver_pay.open_type", {"page", "popup"}, "page")
    require_https_url(config, "naver_pay.return_url", allow_empty=True)
    require_https_url(config, "naver_pay.order_endpoint", allow_empty=True)
    require_https_url(config, "naver_pay.approve_url", allow_empty=True)
    require_https_url(config, "naver_pay.cancel_url", allow_empty=True)

    if flag(config, "notification.enable"):
        require_email(config, "notification.email")
        require_email(config, "notification.from")
    else:
        require_email(config, "notification.email", allow_empty=True)
        require_email(config, "notification.from", allow_empty=True)

    if flag(config, "naver_pay.enable_cancel") and not flag(config, "naver_pay.enable_approval"):
        raise ValueError("naver_pay.enable_cancel requires naver_pay.enable_approval=true first.")


def display_command(command: list[str]) -> str:
    sensitive_flags = {
        "--naver-client-secret",
        "--naver-order-merchant-auth-key",
        "--naver-order-button-auth-key",
        "--naver-order-common-auth-key",
        "--admin-token",
        "--track-salt",
    }
    display: list[str] = []
    hide_next = False
    for token in command:
        if hide_next:
            display.append("[redacted]")
            hide_next = False
            continue
        display.append(token)
        if token in sensitive_flags:
            hide_next = True
    return " ".join(display)


def run_step(command: list[str], dry_run: bool) -> None:
    print("+ " + display_command(command))
    if dry_run:
        return
    subprocess.run(command, cwd=ROOT, check=True)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def backup_release_sources(backup_root: Path) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%SZ")
    backup_dir = backup_root / f"ittemmall-release-{timestamp}"
    suffix = 1
    while backup_dir.exists():
        suffix += 1
        backup_dir = backup_root / f"ittemmall-release-{timestamp}-{suffix}"
    backup_dir.mkdir(parents=True, exist_ok=False)
    manifest = {
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "reason": "Backup before prepare_production_release.py modifies public source files.",
        "files": [],
    }

    for source_path in RELEASE_SOURCE_FILES:
        if not source_path.is_file():
            continue
        relative = source_path.relative_to(ROOT)
        destination = backup_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination)
        manifest["files"].append(
            {
                "path": str(relative),
                "size": source_path.stat().st_size,
                "sha256": file_sha256(source_path),
            }
        )

    (backup_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return backup_dir


def build_legal_command(config: dict) -> list[str]:
    command = [sys.executable, "scripts/fill_legal_owner_info.py", "--apply-to-source"]
    for field in LEGAL_FIELDS:
        cli_name = "--" + field.replace("_", "-")
        command.extend([cli_name, required(config, f"legal.{field}")])
    return command


def build_public_naver_command(config: dict) -> list[str]:
    site_origin = value(config, "site.origin", "https://ittemmall.com")
    command = [
        sys.executable,
        "scripts/generate_public_naverpay_config.py",
        "--client-id",
        required(config, "naver_pay.client_id"),
        "--chain-id",
        required(config, "naver_pay.chain_id"),
        "--mode",
        value(config, "naver_pay.mode", "production"),
        "--open-type",
        value(config, "naver_pay.open_type", "page"),
        "--site-origin",
        site_origin,
        "--output",
        "payment/naverpay-config.js",
    ]
    return_url = value(config, "naver_pay.return_url")
    order_endpoint = value(config, "naver_pay.order_endpoint")
    if return_url:
        command.extend(["--return-url", return_url])
    if order_endpoint:
        command.extend(["--order-endpoint", order_endpoint])
    return command


def build_private_config_command(config: dict) -> list[str]:
    command = [
        sys.executable,
        "scripts/generate_private_config.py",
        "--output",
        value(config, "private.output", str(DEFAULT_PRIVATE_OUTPUT)),
        "--order-store-path",
        required(config, "server.order_store_path"),
        "--track-log-path",
        value(config, "server.track_log_path", ""),
        "--site-base-url",
        value(config, "site.base_url", "https://ittemmall.com"),
        "--notify-email",
        value(config, "notification.email", ""),
        "--notify-from",
        value(config, "notification.from", "no-reply@ittemmall.com"),
        "--toss-mid",
        value(config, "toss_payments.mid", ""),
        "--toss-client-key",
        value(config, "toss_payments.client_key", ""),
        "--toss-secret-key",
        value(config, "toss_payments.secret_key", ""),
        "--toss-payment-widget-variant-key",
        value(config, "toss_payments.payment_widget_variant_key", "DEFAULT"),
        "--naver-client-id",
        required(config, "naver_pay.client_id"),
        "--naver-chain-id",
        required(config, "naver_pay.chain_id"),
        "--naver-client-secret",
        required(config, "naver_pay.client_secret"),
        "--naver-application-type",
        value(config, "naver_pay.application_type", "order"),
        "--naver-order-account-id",
        value(config, "naver_pay.order_account_id", ""),
        "--naver-order-merchant-auth-key",
        value(config, "naver_pay.order_merchant_auth_key", ""),
        "--naver-order-button-auth-key",
        value(config, "naver_pay.order_button_auth_key", ""),
        "--naver-order-common-auth-key",
        value(config, "naver_pay.order_common_auth_key", ""),
        "--naver-mode",
        value(config, "naver_pay.mode", "production"),
        "--naver-approve-url",
        value(config, "naver_pay.approve_url", ""),
        "--naver-cancel-url",
        value(config, "naver_pay.cancel_url", ""),
    ]
    track_salt = value(config, "server.track_salt")
    admin_token = value(config, "server.admin_token")
    rate_limit_path = value(config, "server.rate_limit_path")
    if rate_limit_path:
        command.extend(["--rate-limit-path", rate_limit_path])
    if track_salt:
        command.extend(["--track-salt", track_salt])
    if admin_token:
        command.extend(["--admin-token", admin_token])
    if flag(config, "notification.enable"):
        command.append("--enable-notify")
    if flag(config, "toss_payments.enable_approval"):
        command.append("--enable-toss-approval")
    if flag(config, "naver_pay.enable_approval"):
        command.append("--enable-approval")
    if flag(config, "naver_pay.enable_cancel"):
        command.append("--enable-cancel")
    return command


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a ITTEMMALL production release from one JSON config.")
    parser.add_argument("--config", required=True, help="JSON release config path.")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without writing files.")
    parser.add_argument(
        "--skip-private",
        action="store_true",
        help="Skip private PHP config generation if server secrets will be set manually.",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip public package rebuild and readiness report.",
    )
    parser.add_argument(
        "--allow-development-mode",
        action="store_true",
        help="Allow naver_pay.mode=development for Naver Pay review/sandbox runs.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate the release JSON and exit without printing or running release commands.",
    )
    parser.add_argument(
        "--backup-dir",
        default=str(DEFAULT_BACKUP_DIR),
        help="Directory where source backups are written before modifying legal pages and public Naver Pay config.",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Do not create a source backup before writing release files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        config = load_json_config(args.config)
        validate_release_config(
            config,
            allow_development_mode=args.allow_development_mode,
            skip_private=args.skip_private,
        )
        if args.validate_only:
            print("Production release config validation passed.")
            return 0
        commands = [
            build_legal_command(config),
            build_public_naver_command(config),
        ]
        if not args.skip_private:
            commands.append(build_private_config_command(config))
        if not args.skip_build:
            commands.extend(
                [
                    [sys.executable, "scripts/build_deployment_package.py"],
                    [sys.executable, "scripts/deployment_readiness_report.py", "--allow-owner-tasks"],
                ]
            )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(str(error)) from error

    backup_path = None
    if not args.dry_run and not args.no_backup:
        backup_path = backup_release_sources(Path(args.backup_dir).expanduser().resolve())
        print(f"Source backup written: {backup_path}")
    elif args.dry_run and not args.no_backup:
        print(f"Dry run: source backup would be written under {Path(args.backup_dir).expanduser().resolve()}")
    elif args.no_backup:
        print("Source backup skipped by --no-backup.")

    for command in commands:
        run_step(command, args.dry_run)

    if args.dry_run:
        print("Dry run complete. No files were changed.")
    else:
        print("Production release preparation complete.")
        if backup_path is not None:
            print(f"Original source backup: {backup_path}")
        print("Upload build/ittemmall-public.zip to the public web root.")
        if not args.skip_private:
            print("Upload the generated private config outside the public web root.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
