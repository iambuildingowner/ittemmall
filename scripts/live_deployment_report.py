from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "build" / "ittemmall-live-report.md"

Status = Literal["PASS", "OWNER", "WARN", "FAIL"]


@dataclass
class Response:
    status: int
    body: bytes
    content_type: str
    url: str

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


@dataclass
class Check:
    status: Status
    area: str
    name: str
    evidence: str
    next_step: str = ""


def build_url(base_url: str, path: str) -> str:
    return urllib.parse.urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))


def request(
    base_url: str,
    path: str,
    *,
    method: str = "GET",
    data: dict | None = None,
    headers: dict | None = None,
) -> Response:
    url = build_url(base_url, path)
    body = None
    merged_headers = {"User-Agent": "ITTEMMALL-LIVE-REPORT/1.0"}
    if headers:
        merged_headers.update(headers)
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        merged_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=merged_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            return Response(
                status=res.status,
                body=res.read(),
                content_type=res.headers.get("Content-Type", ""),
                url=url,
            )
    except urllib.error.HTTPError as error:
        return Response(
            status=error.code,
            body=error.read(),
            content_type=error.headers.get("Content-Type", ""),
            url=url,
        )
    except urllib.error.URLError as error:
        return Response(
            status=0,
            body=str(error.reason).encode("utf-8", errors="replace"),
            content_type="text/plain",
            url=url,
        )


def table_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


def bool_label(value: object) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    return str(value)


def json_get(data: dict, path: str) -> object:
    cursor: object = data
    for part in path.split("."):
        if not isinstance(cursor, dict) or part not in cursor:
            return None
        cursor = cursor[part]
    return cursor


def public_config_value(text: str, key: str) -> str:
    match = re.search(rf"\b{re.escape(key)}\s*:\s*([\"'])(.*?)\1", text)
    return match.group(2).strip() if match else ""


def looks_placeholder(value: str) -> bool:
    upper = value.upper()
    markers = ["YOUR_", "PUBLIC_", "NAVER_PAY_", "ISSUED_", "ISSUED-", "TEST_", "REPLACE"]
    return any(marker in upper for marker in markers)


class LiveReport:
    def __init__(self, base_url: str, require_naver_config: bool) -> None:
        self.base_url = base_url.rstrip("/")
        self.require_naver_config = require_naver_config
        self.checks: list[Check] = []
        self.health: dict = {}

    def add(self, status: Status, area: str, name: str, evidence: str, next_step: str = "") -> None:
        self.checks.append(Check(status, area, name, evidence, next_step))

    def add_bool(
        self,
        area: str,
        name: str,
        passed: object,
        *,
        fail_status: Status = "FAIL",
        next_step: str = "",
    ) -> None:
        if passed is True:
            self.add("PASS", area, name, "true")
        else:
            self.add(fail_status, area, name, bool_label(passed), next_step)

    def check_page(self, path: str, area: str, name: str, expected: list[str]) -> Response:
        response = request(self.base_url, path)
        if response.status == 200:
            self.add("PASS", area, name, f"200 {response.url}")
        else:
            self.add("FAIL", area, name, f"{response.status} {response.url}", "Upload or route this public file.")
            return response

        missing = [item for item in expected if item not in response.text]
        if missing:
            self.add("FAIL", area, f"{name} content", "missing: " + ", ".join(missing))
        else:
            self.add("PASS", area, f"{name} content", "expected text found")
        return response

    def check_public_pages(self) -> None:
        pages = [
            ("/", "public", "home", ["ITTEMMALL", "payment/toss-config.js"]),
            ("/404.html", "public", "404 recovery", ["페이지를 찾을 수 없습니다", "상품 보기"]),
            ("/payment/ops.html", "ops", "operations page", ["운영 점검", "healthcheck.php", "메일 알림 테스트"]),
            ("/payment/order-lookup.html", "order-lookup", "customer order lookup page", ["주문 조회", "order-lookup.php"]),
            ("/payment/admin.html", "admin", "admin dashboard", ["Orders Admin", "admin-orders.php", "ops.html"]),
            ("/legal/business.html", "legal", "business page", ["사업자 정보", "ITTEMMALL"]),
            ("/legal/terms.html", "legal", "terms page", ["이용약관", "ITTEMMALL"]),
            ("/legal/privacy.html", "legal", "privacy page", ["개인정보처리방침", "ITTEMMALL"]),
            ("/legal/refund.html", "legal", "refund page", ["배송·교환·환불 안내", "ITTEMMALL"]),
            ("/robots.txt", "seo", "robots", ["Sitemap: https://ittemmall.com/sitemap.xml"]),
            ("/sitemap.xml", "seo", "sitemap", ["https://ittemmall.com/", "legal/privacy.html"]),
        ]
        legal_todo_found = False
        for path, area, name, expected in pages:
            response = self.check_page(path, area, name, expected)
            if path.startswith("/legal/") and "ITTEMMALL_OWNER_TODO" in response.text:
                legal_todo_found = True
        if legal_todo_found:
            self.add(
                "OWNER",
                "legal",
                "owner legal values",
                "ITTEMMALL_OWNER_TODO remains",
                "Run scripts/fill_legal_owner_info.py with real business/shipping/privacy values.",
            )
        else:
            self.add("PASS", "legal", "owner legal values", "no ITTEMMALL_OWNER_TODO found")

    def check_payment_scope_config(self) -> None:
        toss_response = request(self.base_url, "/payment/toss-config.js")
        if toss_response.status != 200:
            self.add("FAIL", "toss-public", "runtime config", f"{toss_response.status} {toss_response.url}")
        elif "ITTEMMALL_TOSS_PAYMENTS_CONFIG" in toss_response.text:
            self.add("PASS", "toss-public", "runtime config object", "ITTEMMALL_TOSS_PAYMENTS_CONFIG found")
        else:
            self.add("FAIL", "toss-public", "runtime config object", "missing ITTEMMALL_TOSS_PAYMENTS_CONFIG")
        if "SECRET_KEY" in toss_response.text or "secretKey" in toss_response.text:
            self.add("FAIL", "toss-public", "secret exposure", "secret-like text found")
        else:
            self.add("PASS", "toss-public", "secret exposure", "no Toss secret in public JS")

        home = request(self.base_url, "/")
        if "payment/naverpay-config.js" in home.text or 'data-checkout-source="npay"' in home.text:
            self.add("FAIL", "payment-scope", "Naver Pay storefront entry", "still exposed on home")
        else:
            self.add("PASS", "payment-scope", "Naver Pay storefront entry", "not exposed")

    def check_protected_paths(self) -> None:
        admin = request(self.base_url, "/payment/admin-orders.php")
        if admin.status == 401:
            self.add("PASS", "security", "admin API guard", "401 without token")
        elif admin.status == 501:
            self.add(
                "OWNER",
                "security",
                "admin API guard",
                "501 admin token not configured",
                "Set ITTEMMALL_ADMIN_TOKEN in private server config.",
            )
        else:
            self.add("FAIL", "security", "admin API guard", f"{admin.status} without token")

        cancel = request(
            self.base_url,
            "/payment/naverpay-cancel.php",
            method="POST",
            data={"orderId": "IT-LIVE-REPORT-CANCEL"},
        )
        if cancel.status == 401:
            self.add("PASS", "security", "cancel API guard", "401 without token")
        elif cancel.status == 501:
            self.add(
                "OWNER",
                "security",
                "legacy cancel API guard",
                "501 admin token or cancel API not configured",
                "Set ITTEMMALL_ADMIN_TOKEN first; enable NAVER_PAY_CANCEL_ENABLED only after live approval tests.",
            )
        else:
            self.add("FAIL", "security", "cancel API guard", f"{cancel.status} without token")

        notify = request(
            self.base_url,
            "/payment/notification-test.php",
            method="POST",
            data={"message": "live deployment report guard check"},
        )
        if notify.status == 401:
            self.add("PASS", "security", "notification test guard", "401 without token")
        elif notify.status == 501:
            self.add(
                "OWNER",
                "security",
                "notification test guard",
                "501 admin token or notification not configured",
                "Set ITTEMMALL_ADMIN_TOKEN first; enable ITTEMMALL_NOTIFY_ENABLED only if email alerts are needed.",
            )
        else:
            self.add("FAIL", "security", "notification test guard", f"{notify.status} without token")

        lookup = request(
            self.base_url,
            "/payment/order-lookup.php",
            method="POST",
            data={"orderId": "IT-LIVE-REPORT-LOOKUP", "contact": "lookup@example.com"},
        )
        if lookup.status in {404, 429, 501}:
            self.add("PASS", "order-lookup", "API privacy guard", f"{lookup.status} without matching order")
        else:
            self.add("FAIL", "order-lookup", "API privacy guard", f"{lookup.status} without matching order")

        blocked_paths = [
            "/ITTEMMALL_LAUNCH_OWNER_CHECKLIST.md",
            "/DEPLOYMENT_MANIFEST.md",
            "/payment/NAVERPAY_SETUP.md",
            "/payment/TOSS_SETUP.md",
            "/payment/naverpay-config.example.js",
            "/payment/toss-config.example.js",
            "/private/ittemmall-server-config.example.php",
            "/scripts/build_deployment_package.py",
            "/outputs/",
        ]
        for path in blocked_paths:
            response = request(self.base_url, path)
            if response.status in {403, 404}:
                self.add("PASS", "security", f"protected path {path}", str(response.status))
            else:
                self.add("FAIL", "security", f"protected path {path}", str(response.status))

    def check_health(self) -> None:
        response = request(self.base_url, "/payment/healthcheck.php")
        if response.status != 200:
            self.add("FAIL", "health", "healthcheck", f"{response.status} {response.url}")
            return
        try:
            parsed = json.loads(response.text)
        except json.JSONDecodeError:
            self.add("FAIL", "health", "healthcheck JSON", "invalid JSON")
            return
        if not isinstance(parsed, dict):
            self.add("FAIL", "health", "healthcheck JSON", "top-level value is not object")
            return
        self.health = parsed
        self.add_bool("health", "ok", parsed.get("ok"))

        health_failures = [
            ("php", "curl", "php.curl", "Enable PHP cURL on hosting."),
            ("php", "json", "php.json", "Enable PHP JSON extension on hosting."),
            (
                "order-store",
                "configured",
                "serverOrderStore.configured",
                "Set ITTEMMALL_ORDER_STORE_PATH outside the public web root.",
            ),
            (
                "order-store",
                "directory writable",
                "serverOrderStore.directoryWritable",
                "Make the private order-store directory writable by PHP.",
            ),
            (
                "order-store",
                "lock writable",
                "serverOrderStore.lockWritable",
                "Make the order-store lock file or parent directory writable by PHP.",
            ),
        ]
        for area, name, path, next_step in health_failures:
            self.add_bool(area, name, json_get(parsed, path), next_step=next_step)

        file_exists = json_get(parsed, "serverOrderStore.fileExists")
        file_valid = json_get(parsed, "serverOrderStore.fileValidJson")
        if file_exists is True:
            self.add_bool("order-store", "order JSON valid", file_valid, next_step="Fix or replace the private order JSON.")
        else:
            self.add(
                "WARN",
                "order-store",
                "order JSON file",
                "not created yet",
                "Submit one safe test order before enabling live approval.",
            )

        backup_exists = json_get(parsed, "serverOrderStore.backupExists")
        backup_valid = json_get(parsed, "serverOrderStore.backupValidJson")
        if backup_exists is True:
            self.add_bool("order-store", "backup JSON valid", backup_valid, next_step="Fix or remove the invalid .bak backup.")
        else:
            self.add("WARN", "order-store", "backup JSON", "not created yet")

        rate_limit = parsed.get("rateLimit", {})
        if isinstance(rate_limit, dict) and rate_limit.get("configured") is True:
            self.add_bool("rate-limit", "directory writable", rate_limit.get("directoryWritable"), next_step="Make the private rate-limit directory writable by PHP.")
            self.add_bool("rate-limit", "lock writable", rate_limit.get("lockWritable"), next_step="Make the rate-limit lock file or parent directory writable by PHP.")
            if rate_limit.get("fileExists") is True:
                self.add_bool("rate-limit", "file JSON valid", rate_limit.get("fileValidJson"), next_step="Fix or remove the private rate-limit JSON file.")
            else:
                self.add("WARN", "rate-limit", "state file", "not created yet")
        else:
            self.add("WARN", "rate-limit", "configured", "false; private order or track path will enable it")

        if json_get(parsed, "serverConfig.privateConfigFileLoaded") is True:
            self.add("PASS", "config", "private config file", "loaded")
        else:
            self.add("WARN", "config", "private config file", "not loaded; env vars may be used")

        secret_exposed = json_get(parsed, "publicNaverPay.clientSecretExposed")
        if secret_exposed is True:
            self.add("FAIL", "legacy-payment", "public secret exposure", bool_label(secret_exposed), "Remove secrets from public JS.")

        self.add_bool(
            "admin",
            "admin token",
            json_get(parsed, "admin.adminTokenConfigured"),
            fail_status="OWNER",
            next_step="Set ITTEMMALL_ADMIN_TOKEN before using admin operations.",
        )

        notify_enabled = json_get(parsed, "notification.enabled")
        if notify_enabled is True:
            self.add_bool("notification", "recipient valid", json_get(parsed, "notification.recipientLooksValid"))
            self.add_bool("notification", "sender valid", json_get(parsed, "notification.fromLooksValid"))
            self.add_bool("notification", "mail function", json_get(parsed, "notification.mailFunctionAvailable"))
        else:
            self.add("WARN", "notification", "email notification", "disabled")

        readiness = parsed.get("readiness", {})
        if isinstance(readiness, dict):
            missing_operations = [
                item for item in readiness.get("missingForOperations") or []
                if "NAVER_PAY" not in str(item) and "publicNaverPay" not in str(item)
            ]
            self.add_bool(
                "readiness",
                "ready for order operations",
                readiness.get("readyForOrderOperations"),
                fail_status="OWNER",
                next_step="Resolve missingForOperations: " + ", ".join(map(str, missing_operations)),
            )

    def run(self) -> list[Check]:
        self.check_public_pages()
        self.check_payment_scope_config()
        self.check_protected_paths()
        self.check_health()
        return self.checks


def render_markdown(base_url: str, checks: list[Check], health: dict) -> str:
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    summary = {status: sum(1 for check in checks if check.status == status) for status in ["PASS", "OWNER", "WARN", "FAIL"]}
    lines = [
        "# ITTEMMALL Live Deployment Report",
        "",
        f"- Base URL: {base_url.rstrip('/')}",
        f"- Generated: {generated_at}",
        "",
        "## Summary",
        "",
        "| Status | Count |",
        "|---|---:|",
    ]
    for status in ["PASS", "OWNER", "WARN", "FAIL"]:
        lines.append(f"| {status} | {summary[status]} |")

    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Status | Area | Check | Evidence | Next |",
            "|---|---|---|---|---|",
        ]
    )
    for check in checks:
        lines.append(
            "| "
            + " | ".join(
                [
                    check.status,
                    table_cell(check.area),
                    table_cell(check.name),
                    table_cell(check.evidence),
                    table_cell(check.next_step),
                ]
            )
            + " |"
        )

    readiness = health.get("readiness") if isinstance(health, dict) else None
    if isinstance(readiness, dict):
        lines.extend(["", "## Healthcheck Missing Items", ""])
        for key in ["missingForApproval", "missingForOperations"]:
            values = readiness.get(key) or []
            formatted = ", ".join(map(str, values)) if values else "none"
            lines.append(f"- `{key}`: {formatted}")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Markdown report for a live ITTEMMALL deployment.")
    parser.add_argument("--base-url", default="https://ittemmall.com", help="Live deployment base URL.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Markdown report output path.")
    parser.add_argument(
        "--require-naver-config",
        action="store_true",
        help="Legacy no-op option kept for old command compatibility.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when OWNER items remain.",
    )
    args = parser.parse_args()

    report = LiveReport(args.base_url, args.require_naver_config)
    checks = report.run()
    output = Path(args.output).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_markdown(args.base_url, checks, report.health), encoding="utf-8")

    summary = {status: sum(1 for check in checks if check.status == status) for status in ["PASS", "OWNER", "WARN", "FAIL"]}
    print(
        "Live deployment report written: "
        + str(output)
        + "\nSummary: "
        + ", ".join(f"{key}={value}" for key, value in summary.items())
    )

    if summary["FAIL"]:
        return 1
    if args.strict and summary["OWNER"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
