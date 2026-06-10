from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEGAL_ROOT = ROOT / "legal"
DEFAULT_OUTPUT_DIR = ROOT / "build" / "ittemmall-legal-preview"

LEGAL_FILES = [
    "business.html",
    "terms.html",
    "privacy.html",
    "refund.html",
]

FIELD_TO_PLACEHOLDER = {
    "representative": "ITTEMMALL_OWNER_TODO_REPRESENTATIVE",
    "business_registration_number": "ITTEMMALL_OWNER_TODO_BUSINESS_REGISTRATION_NUMBER",
    "ecommerce_license": "ITTEMMALL_OWNER_TODO_ECOMMERCE_LICENSE",
    "business_address": "ITTEMMALL_OWNER_TODO_BUSINESS_ADDRESS",
    "privacy_officer": "ITTEMMALL_OWNER_TODO_PRIVACY_OFFICER",
    "shipping_carrier": "ITTEMMALL_OWNER_TODO_SHIPPING_CARRIER",
    "shipping_fee": "ITTEMMALL_OWNER_TODO_SHIPPING_FEE",
    "shipping_days": "ITTEMMALL_OWNER_TODO_SHIPPING_DAYS",
    "return_address": "ITTEMMALL_OWNER_TODO_RETURN_ADDRESS",
}


def clean_value(name: str, value: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        raise ValueError(f"{name} is required.")
    if any(ord(char) < 32 and char not in "\t\n\r" for char in cleaned):
        raise ValueError(f"{name} must not contain control characters.")
    return cleaned


def load_config(path: str) -> dict[str, str]:
    if not path:
        return {}
    config_path = Path(path).expanduser().resolve()
    data = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("--config must point to a JSON object.")
    return {str(key): str(value) for key, value in data.items()}


def owner_values(args: argparse.Namespace) -> dict[str, str]:
    config = load_config(args.config)
    values: dict[str, str] = {}
    for field in FIELD_TO_PLACEHOLDER:
        raw = getattr(args, field) or config.get(field) or ""
        values[field] = clean_value(field, raw)
    return values


def render_page(source: str, values: dict[str, str]) -> str:
    rendered = source
    for field, placeholder in FIELD_TO_PLACEHOLDER.items():
        rendered = rendered.replace(placeholder, html.escape(values[field], quote=False))
    if "ITTEMMALL_OWNER_TODO" in rendered:
        raise ValueError("Not all ITTEMMALL_OWNER_TODO placeholders were replaced.")
    return rendered


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fill ITTEMMALL legal policy pages with owner-provided business and shipping info."
    )
    parser.add_argument("--config", default="", help="Optional JSON config with snake_case field names.")
    parser.add_argument("--representative", default="", help="Business representative name.")
    parser.add_argument("--business-registration-number", default="", help="Business registration number.")
    parser.add_argument("--ecommerce-license", default="", help="Mail-order/ecommerce license number.")
    parser.add_argument("--business-address", default="", help="Business address.")
    parser.add_argument("--privacy-officer", default="", help="Privacy officer name.")
    parser.add_argument("--shipping-carrier", default="", help="Shipping carrier name.")
    parser.add_argument("--shipping-fee", default="", help="Base shipping fee text, such as 3,000원.")
    parser.add_argument("--shipping-days", default="", help="Business days until shipment.")
    parser.add_argument("--return-address", default="", help="Return address.")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Output directory for filled legal files. Defaults to a preview folder.",
    )
    parser.add_argument(
        "--apply-to-source",
        action="store_true",
        help="Write directly to legal/*.html instead of the preview output directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        values = owner_values(args)
    except (ValueError, json.JSONDecodeError) as error:
        raise SystemExit(str(error)) from error

    output_dir = LEGAL_ROOT if args.apply_to_source else Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    for filename in LEGAL_FILES:
        source_path = LEGAL_ROOT / filename
        if not source_path.is_file():
            raise SystemExit(f"Missing legal page: {source_path}")
        rendered = render_page(source_path.read_text(encoding="utf-8"), values)
        output_path = output_dir / filename
        output_path.write_text(rendered, encoding="utf-8")
        written.append(output_path)

    print("Legal policy pages written:")
    for path in written:
        print(f"- {path}")
    if not args.apply_to_source:
        print("Preview only. Re-run with --apply-to-source to update legal/*.html.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
