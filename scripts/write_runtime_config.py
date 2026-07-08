#!/usr/bin/env python3
"""Write production runtime config from GitHub Actions secrets.

The generated PHP file is uploaded outside the public web root. This script
only writes values that are present in the environment, so an omitted optional
secret cannot overwrite runtime defaults with placeholder paths.
"""

from __future__ import annotations

import os
import stat
import sys
from pathlib import Path


ALLOWED_KEYS = [
    "ITTEMMALL_ADMIN_TOKEN",
    "ITTEMMALL_TRACK_LOG_PATH",
    "ITTEMMALL_TRACK_SALT",
    "ITTEMMALL_ORDER_STORE_PATH",
    "ITTEMMALL_RATE_LIMIT_PATH",
    "ITTEMMALL_SITE_BASE_URL",
    "ITTEMMALL_NOTIFY_ENABLED",
    "ITTEMMALL_NOTIFY_EMAIL",
    "ITTEMMALL_NOTIFY_FROM",
    "TOSS_PAYMENTS_MID",
    "TOSS_PAYMENTS_CLIENT_KEY",
    "TOSS_PAYMENTS_SECRET_KEY",
    "TOSS_PAYMENTS_PAYMENT_WIDGET_VARIANT_KEY",
    "TOSS_PAYMENTS_APPROVE_ENABLED",
    "NAVER_PAY_CLIENT_ID",
    "NAVER_PAY_CHAIN_ID",
    "NAVER_PAY_CLIENT_SECRET",
    "NAVER_PAY_MODE",
    "NAVER_PAY_APPROVE_URL",
    "NAVER_PAY_APPROVE_ENABLED",
    "NAVER_PAY_CANCEL_URL",
    "NAVER_PAY_CANCEL_ENABLED",
]


def php_string(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: write_runtime_config.py <output>", file=sys.stderr)
        return 2

    values = {
        key: value.strip()
        for key in ALLOWED_KEYS
        if (value := os.environ.get(key, "")).strip()
    }
    values.setdefault("ITTEMMALL_SITE_BASE_URL", "https://ittemmall.com")

    if not values.get("ITTEMMALL_ADMIN_TOKEN"):
        print("ITTEMMALL_ADMIN_TOKEN is required for protected tracking reports.", file=sys.stderr)
        return 1

    output = Path(sys.argv[1]).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "<?php",
        "declare(strict_types=1);",
        "",
        "return [",
    ]
    for key in ALLOWED_KEYS:
        if key in values:
            lines.append(f"    {php_string(key)} => {php_string(values[key])},")
    lines.extend(["];", ""])
    output.write_text("\n".join(lines), encoding="utf-8")
    output.chmod(stat.S_IRUSR | stat.S_IWUSR)
    print(f"Runtime config written: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
