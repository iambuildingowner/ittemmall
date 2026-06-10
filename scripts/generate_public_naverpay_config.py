from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "payment" / "naverpay-config.js"
DEFAULT_SITE_ORIGIN = "https://ittemmall.com"


def js_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=True)


def clean_required_value(name: str, value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{name} is required.")
    if any(ord(char) < 32 for char in cleaned):
        raise ValueError(f"{name} must not contain control characters.")
    return cleaned


def validate_url(name: str, value: str) -> str:
    cleaned = clean_required_value(name, value).rstrip("/")
    parsed = urlparse(cleaned)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"{name} must be a full http(s) URL.")
    host = parsed.hostname or ""
    is_local = host in {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme != "https" and not is_local:
        raise ValueError(f"{name} must use HTTPS outside localhost.")
    return cleaned


def validate_optional_url(name: str, value: str) -> str:
    if not value:
        return ""
    return validate_url(name, value)


def build_config(args: argparse.Namespace) -> str:
    client_id = clean_required_value("client id", args.client_id)
    chain_id = clean_required_value("chain id", args.chain_id)
    site_origin = validate_url("site origin", args.site_origin)
    return_url = validate_optional_url("return url", args.return_url)
    order_endpoint = validate_optional_url("order endpoint", args.order_endpoint)

    return_expr = js_string(return_url) if return_url else 'siteOrigin + "/payment/return.html"'
    order_expr = js_string(order_endpoint) if order_endpoint else 'siteOrigin + "/payment/order-store.php"'

    lines = [
        "(function () {",
        f"  var siteOrigin = window.location.origin || {js_string(site_origin)};",
        "  window.ITTEMMALL_NAVER_PAY_CONFIG = {",
        f"    mode: {js_string(args.mode)},",
        f"    clientId: {js_string(client_id)},",
        f"    chainId: {js_string(chain_id)},",
        f"    openType: {js_string(args.open_type)},",
        f"    returnUrl: {return_expr},",
        f"    orderEndpoint: {order_expr},",
        "  };",
        "})();",
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the public ITTEMMALL Naver Pay runtime config JavaScript file."
    )
    parser.add_argument("--client-id", required=True, help="Issued public Naver Pay Client ID.")
    parser.add_argument("--chain-id", required=True, help="Issued public Naver Pay Chain ID.")
    parser.add_argument("--mode", choices=["development", "production"], default="production")
    parser.add_argument("--open-type", choices=["page", "popup"], default="page")
    parser.add_argument("--site-origin", default=DEFAULT_SITE_ORIGIN, help="Fallback public site origin.")
    parser.add_argument("--return-url", default="", help="Optional fixed Naver Pay return URL.")
    parser.add_argument("--order-endpoint", default="", help="Optional fixed server order endpoint URL.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output JS path, or '-' for stdout.")
    args, unknown = parser.parse_known_args()

    secret_like = [item for item in unknown if "secret" in item.lower()]
    if secret_like:
        parser.error(
            "Do not pass a client secret to this public JavaScript generator. "
            "Use scripts/generate_private_config.py for NAVER_PAY_CLIENT_SECRET."
        )
    if unknown:
        parser.error("unrecognized arguments: " + " ".join(unknown))
    return args


def main() -> int:
    args = parse_args()
    try:
        config = build_config(args)
    except ValueError as error:
        raise SystemExit(str(error)) from error

    if args.output == "-":
        print(config, end="")
        return 0

    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(config, encoding="utf-8")
    print(f"Public Naver Pay config written: {output}")
    print("This file contains only public clientId/chainId settings. Keep clientSecret server-side.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
