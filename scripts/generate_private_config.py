from __future__ import annotations

import argparse
import secrets
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "build" / "ittemmall-private" / "ittemmall-server-config.php"


def php_string(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def build_config(args: argparse.Namespace) -> str:
    order_path = args.order_store_path
    track_path = args.track_log_path
    if not order_path:
        order_path = "/absolute/private/path/ittemmall-orders.json"
    if not track_path:
        track_path = "/absolute/private/path/ittemmall-track-events.jsonl"

    values = {
        "ITTEMMALL_ORDER_STORE_PATH": order_path,
        "ITTEMMALL_TRACK_LOG_PATH": track_path,
        "ITTEMMALL_RATE_LIMIT_PATH": args.rate_limit_path,
        "ITTEMMALL_TRACK_SALT": args.track_salt or secrets.token_urlsafe(32),
        "ITTEMMALL_ADMIN_TOKEN": args.admin_token or secrets.token_urlsafe(36),
        "ITTEMMALL_SITE_BASE_URL": args.site_base_url,
        "ITTEMMALL_NOTIFY_ENABLED": "1" if args.enable_notify else "0",
        "ITTEMMALL_NOTIFY_EMAIL": args.notify_email,
        "ITTEMMALL_NOTIFY_FROM": args.notify_from,
        "TOSS_PAYMENTS_MID": args.toss_mid,
        "TOSS_PAYMENTS_CLIENT_KEY": args.toss_client_key,
        "TOSS_PAYMENTS_SECRET_KEY": args.toss_secret_key,
        "TOSS_PAYMENTS_PAYMENT_WIDGET_VARIANT_KEY": args.toss_payment_widget_variant_key,
        "TOSS_PAYMENTS_APPROVE_ENABLED": "1" if args.enable_toss_approval else "0",
        "NAVER_PAY_CLIENT_ID": args.naver_client_id,
        "NAVER_PAY_CHAIN_ID": args.naver_chain_id,
        "NAVER_PAY_CLIENT_SECRET": args.naver_client_secret,
        "NAVER_PAY_MODE": args.naver_mode,
        "NAVER_PAY_APPROVE_URL": args.naver_approve_url,
        "NAVER_PAY_APPROVE_ENABLED": "1" if args.enable_approval else "0",
        "NAVER_PAY_CANCEL_URL": args.naver_cancel_url,
        "NAVER_PAY_CANCEL_ENABLED": "1" if args.enable_cancel else "0",
    }

    lines = [
        "<?php",
        "declare(strict_types=1);",
        "",
        "return [",
    ]
    for key, value in values.items():
        lines.append(f"    {php_string(key)} => {php_string(value)},")
    lines.extend([
        "];",
        "",
    ])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a ITTEMMALL private server config PHP file.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Private config output path.")
    parser.add_argument("--order-store-path", default="", help="Private JSON order store path on the server.")
    parser.add_argument("--track-log-path", default="", help="Private JSONL tracking log path on the server.")
    parser.add_argument("--rate-limit-path", default="", help="Optional private JSON rate-limit state path. Defaults to order-store path plus .rate-limit.json at runtime.")
    parser.add_argument("--track-salt", default="", help="Optional existing tracking salt.")
    parser.add_argument("--admin-token", default="", help="Optional existing admin token.")
    parser.add_argument("--site-base-url", default="https://ittemmall.com", help="Public site base URL.")
    parser.add_argument("--notify-email", default="", help="Optional order notification recipient email.")
    parser.add_argument("--notify-from", default="no-reply@ittemmall.com", help="Optional order notification sender email.")
    parser.add_argument("--enable-notify", action="store_true", help="Set ITTEMMALL_NOTIFY_ENABLED=1.")
    parser.add_argument("--toss-mid", default="", help="Issued Toss Payments MID.")
    parser.add_argument("--toss-client-key", default="", help="Issued Toss Payments public client key.")
    parser.add_argument("--toss-secret-key", default="", help="Issued Toss Payments server-only secret key.")
    parser.add_argument("--toss-payment-widget-variant-key", default="DEFAULT", help="Toss Payments payment widget variant key.")
    parser.add_argument("--enable-toss-approval", action="store_true", help="Set TOSS_PAYMENTS_APPROVE_ENABLED=1.")
    parser.add_argument("--naver-client-id", default="", help="Issued Naver Pay Client ID.")
    parser.add_argument("--naver-chain-id", default="", help="Issued Naver Pay Chain ID.")
    parser.add_argument("--naver-client-secret", default="", help="Issued Naver Pay Client Secret.")
    parser.add_argument("--naver-mode", choices=["development", "production"], default="development")
    parser.add_argument("--naver-approve-url", default="", help="Optional full HTTPS approval URL from Naver Pay.")
    parser.add_argument("--naver-cancel-url", default="", help="Optional full HTTPS cancel URL from Naver Pay.")
    parser.add_argument("--enable-approval", action="store_true", help="Set NAVER_PAY_APPROVE_ENABLED=1.")
    parser.add_argument("--enable-cancel", action="store_true", help="Set NAVER_PAY_CANCEL_ENABLED=1.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_config(args), encoding="utf-8")
    print(f"Private config written: {output}")
    print("Keep this file outside the public web root on production.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
