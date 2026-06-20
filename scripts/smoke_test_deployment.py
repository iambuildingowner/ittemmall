from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass


@dataclass
class Response:
    status: int
    body: bytes
    content_type: str
    url: str

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


def build_url(base_url: str, path: str) -> str:
    return urllib.parse.urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))


def request(
    base_url: str,
    path: str,
    method: str = "GET",
    data: dict | None = None,
    extra_headers: dict | None = None,
) -> Response:
    url = build_url(base_url, path)
    body = None
    headers = {"User-Agent": "ITTEMMALL-SMOKE-TEST/1.0"}
    if extra_headers:
        headers.update(extra_headers)
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=12) as res:
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


class Smoke:
    def __init__(
        self,
        base_url: str,
        static_local: bool,
        require_naver_config: bool,
        write_test_order: bool,
        admin_token: str,
    ) -> None:
        self.base_url = base_url
        self.static_local = static_local
        self.require_naver_config = require_naver_config
        self.write_test_order = write_test_order
        self.admin_token = admin_token
        self.failures: list[str] = []
        self.warnings: list[str] = []

    def ok(self, label: str) -> None:
        print(f"OK   {label}")

    def warn(self, label: str) -> None:
        self.warnings.append(label)
        print(f"WARN {label}")

    def fail(self, label: str) -> None:
        self.failures.append(label)
        print(f"FAIL {label}")

    def assert_status(self, response: Response, expected: set[int], label: str) -> None:
        if response.status in expected:
            self.ok(f"{label} ({response.status})")
        else:
            self.fail(f"{label}: expected {sorted(expected)}, got {response.status} at {response.url}")

    def check_home(self) -> None:
        response = request(self.base_url, "/")
        self.assert_status(response, {200}, "home loads")
        text = response.text
        if "ITTEMMALL" in text and "payment/toss-config.js" in text:
            self.ok("home contains brand and Toss runtime config script")
        else:
            self.fail("home is missing ITTEMMALL or Toss payment runtime config script")
        if "payment/naverpay-config.js" in text or 'data-checkout-source="npay"' in text:
            self.fail("home still exposes a Naver Pay storefront entry")
        else:
            self.ok("home does not expose a Naver Pay storefront entry")
        if "application/ld+json" in text and "schema.org" in text:
            self.ok("home contains structured data")
        else:
            self.fail("home is missing structured data")

    def check_static_assets(self) -> None:
        for path in [
            "/404.html",
            "/robots.txt",
            "/sitemap.xml",
            "/legal/business.html",
            "/legal/terms.html",
            "/legal/privacy.html",
            "/legal/refund.html",
            "/payment/ops.html",
            "/payment/order-lookup.html",
            "/payment/toss-config.js",
            "/assets/ittemmall/favicon.svg",
            "/assets/ittemmall/ittemmall-model-floor.png",
            "/assets/ittemmall/ittemmall-c-pink-thumb-main.png",
            "/assets/ittemmall/ittemmall-c-black-thumb-main.png",
        ]:
            response = request(self.base_url, path)
            self.assert_status(response, {200}, f"asset loads {path}")

        robots = request(self.base_url, "/robots.txt")
        if "Sitemap: https://ittemmall.com/sitemap.xml" in robots.text:
            self.ok("robots.txt includes sitemap")
        else:
            self.fail("robots.txt is missing sitemap")

        sitemap = request(self.base_url, "/sitemap.xml")
        if "<loc>https://ittemmall.com/</loc>" in sitemap.text:
            self.ok("sitemap.xml includes home URL")
        else:
            self.fail("sitemap.xml is missing home URL")
        for path in [
            "/legal/business.html",
            "/legal/terms.html",
            "/legal/privacy.html",
            "/legal/refund.html",
        ]:
            expected_url = f"https://ittemmall.com{path}"
            if expected_url in sitemap.text:
                self.ok(f"sitemap.xml includes {path}")
            else:
                self.fail(f"sitemap.xml is missing {path}")

        for path, expected in [
            ("/legal/business.html", "사업자 정보"),
            ("/legal/terms.html", "이용약관"),
            ("/legal/privacy.html", "개인정보처리방침"),
            ("/legal/refund.html", "배송·교환·환불 안내"),
        ]:
            legal = request(self.base_url, path)
            if expected in legal.text and "ITTEMMALL" in legal.text:
                self.ok(f"legal page content {path}")
            else:
                self.fail(f"legal page content is unexpected {path}")
            if "ITTEMMALL_OWNER_TODO" in legal.text:
                self.warn(f"legal page still has owner TODO values {path}")

        not_found = request(self.base_url, "/404.html")
        if "페이지를 찾을 수 없습니다" in not_found.text and "/#/home" in not_found.text:
            self.ok("404 page has recovery actions")
        else:
            self.fail("404 page is missing recovery actions")

        config = request(self.base_url, "/payment/toss-config.js")
        text = config.text
        if "ITTEMMALL_TOSS_PAYMENTS_CONFIG" not in text:
            self.fail("runtime config does not define ITTEMMALL_TOSS_PAYMENTS_CONFIG")
        elif "SECRET_KEY" in text or "secretKey" in text:
            self.fail("runtime config appears to expose a Toss secret field")
        else:
            self.ok("Toss runtime config exposes only public fields")

        if "clientKey" in text:
            self.ok("Toss runtime config includes clientKey field")
        else:
            self.fail("Toss runtime config is missing clientKey field")

    def check_payment_pages(self) -> None:
        payment = request(self.base_url, "/payment/")
        self.assert_status(payment, {200}, "payment helper page loads")
        if "ITTEMMALL" in payment.text and "결제" in payment.text:
            self.ok("payment helper page has expected content")
        else:
            self.fail("payment helper page content is unexpected")

        admin_page = request(self.base_url, "/payment/admin.html")
        self.assert_status(admin_page, {200}, "admin dashboard page loads")
        if "Orders Admin" in admin_page.text and "admin-orders.php" in admin_page.text and "ops.html" in admin_page.text:
            self.ok("admin dashboard has expected content")
        else:
            self.fail("admin dashboard content is unexpected")

        ops_page = request(self.base_url, "/payment/ops.html")
        self.assert_status(ops_page, {200}, "ops readiness page loads")
        if (
            "Operations Readiness" in ops_page.text
            and "healthcheck.php" in ops_page.text
            and "공개 런칭 점검" in ops_page.text
            and "notification-test.php" in ops_page.text
        ):
            self.ok("ops readiness page has expected content")
        else:
            self.fail("ops readiness page content is unexpected")

        lookup_page = request(self.base_url, "/payment/order-lookup.html")
        self.assert_status(lookup_page, {200}, "customer order lookup page loads")
        if "주문 조회" in lookup_page.text and "order-lookup.php" in lookup_page.text:
            self.ok("customer order lookup page has expected content")
        else:
            self.fail("customer order lookup page content is unexpected")

    def check_protected_paths(self) -> None:
        if self.static_local:
            self.warn("protected path checks skipped in static-local mode")
            return

        protected_paths = [
            "/ITTEMMALL_LAUNCH_OWNER_CHECKLIST.md",
            "/DEPLOYMENT_MANIFEST.md",
            "/payment/NAVERPAY_SETUP.md",
            "/payment/server-config-lib.php",
            "/payment/order-store-lib.php",
            "/payment/naverpay-config.example.js",
            "/payment/naverpay-approve.example.php",
            "/private/ittemmall-server-config.example.php",
            "/ittemmall-private/ittemmall-server-config.php",
            "/notes/ittemmall-tracking-status-2026-05-21.md",
            "/outputs/",
            "/output/",
            "/scripts/build_deployment_package.py",
        ]
        for path in protected_paths:
            response = request(self.base_url, path)
            if response.status in {403, 404}:
                self.ok(f"protected path blocked {path} ({response.status})")
            else:
                self.fail(f"protected path is public {path}: got {response.status}")

        admin = request(self.base_url, "/payment/admin-orders.php")
        if admin.status in {401, 501}:
            self.ok(f"admin orders API is guarded ({admin.status})")
        else:
            self.fail(f"admin orders API is not guarded: got {admin.status}")

        cancel = request(
            self.base_url,
            "/payment/naverpay-cancel.php",
            method="POST",
            data={"orderId": "IT-SMOKE-CANCEL"},
        )
        if cancel.status in {401, 501}:
            self.ok(f"legacy cancel API is guarded ({cancel.status})")
        else:
            self.fail(f"legacy cancel API is not guarded: got {cancel.status}")

        notification = request(
            self.base_url,
            "/payment/notification-test.php",
            method="POST",
            data={"message": "deployment smoke test"},
        )
        if notification.status in {401, 501}:
            self.ok(f"notification test API is guarded ({notification.status})")
        else:
            self.fail(f"notification test API is not guarded: got {notification.status}")

        lookup = request(
            self.base_url,
            "/payment/order-lookup.php",
            method="POST",
            data={"orderId": "IT-SMOKE-LOOKUP", "contact": "smoke@example.com"},
        )
        if lookup.status in {404, 429, 501}:
            self.ok(f"customer order lookup API is non-public without a matching order ({lookup.status})")
        else:
            self.fail(f"customer order lookup API returned unexpected status without a matching order: got {lookup.status}")

    def check_php_health(self) -> None:
        if self.static_local:
            self.warn("PHP healthcheck skipped in static-local mode")
            return

        response = request(self.base_url, "/payment/healthcheck.php")
        self.assert_status(response, {200}, "healthcheck loads")
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.fail("healthcheck did not return JSON")
            return

        if data.get("ok") is True:
            self.ok("healthcheck ok=true")
        else:
            self.fail("healthcheck ok is not true")

        checks = [
            ("php.curl", data.get("php", {}).get("curl") is True),
            ("php.json", data.get("php", {}).get("json") is True),
            ("serverOrderStore.configured", data.get("serverOrderStore", {}).get("configured") is True),
            ("serverOrderStore.directoryWritable", data.get("serverOrderStore", {}).get("directoryWritable") is True),
        ]
        for label, passed in checks:
            if passed:
                self.ok(f"healthcheck {label}")
            else:
                self.fail(f"healthcheck {label} is not ready")

        order_store = data.get("serverOrderStore", {})
        if isinstance(order_store, dict):
            if order_store.get("fileExists") is True and order_store.get("fileValidJson") is not True:
                self.fail("healthcheck serverOrderStore.fileValidJson is not true")
            elif order_store.get("fileExists") is True:
                self.ok("healthcheck serverOrderStore.fileValidJson")
            else:
                self.warn("healthcheck order store file does not exist yet")
            if order_store.get("backupExists") is True and order_store.get("backupValidJson") is not True:
                self.fail("healthcheck serverOrderStore.backupValidJson is not true")
            elif order_store.get("backupExists") is True:
                self.ok("healthcheck serverOrderStore.backupValidJson")
            if order_store.get("lockWritable") is True:
                self.ok("healthcheck serverOrderStore.lockWritable")
            else:
                self.fail("healthcheck serverOrderStore.lockWritable is not true")

        rate_limit = data.get("rateLimit", {})
        if isinstance(rate_limit, dict):
            if rate_limit.get("configured") is True:
                if rate_limit.get("directoryWritable") is True:
                    self.ok("healthcheck rateLimit.directoryWritable")
                else:
                    self.fail("healthcheck rateLimit.directoryWritable is not true")
                if rate_limit.get("lockWritable") is True:
                    self.ok("healthcheck rateLimit.lockWritable")
                else:
                    self.fail("healthcheck rateLimit.lockWritable is not true")
                if rate_limit.get("fileExists") is True and rate_limit.get("fileValidJson") is not True:
                    self.fail("healthcheck rateLimit.fileValidJson is not true")
                elif rate_limit.get("fileExists") is True:
                    self.ok("healthcheck rateLimit.fileValidJson")
            else:
                self.warn("healthcheck rateLimit is not configured")

        naver = data.get("naverPay", {})
        for key in ["clientIdConfigured", "clientSecretConfigured", "chainIdConfigured"]:
            if naver.get(key) is True:
                self.ok(f"healthcheck naverPay.{key}")
            elif self.require_naver_config:
                self.fail(f"healthcheck naverPay.{key} is false")
            else:
                self.warn(f"healthcheck naverPay.{key} is false")

        if data.get("serverConfig", {}).get("privateConfigFileLoaded") is True:
            self.ok("healthcheck private config file loaded")
        else:
            self.warn("healthcheck private config file not loaded; env vars may still be used")

        if data.get("admin", {}).get("adminTokenConfigured") is True:
            self.ok("healthcheck admin token configured")
        else:
            self.warn("healthcheck admin token is not configured")

        notification = data.get("notification", {})
        if isinstance(notification, dict):
            if notification.get("enabled") is True and notification.get("recipientConfigured") is True:
                self.ok("healthcheck order notification configured")
            elif notification.get("enabled") is True:
                self.warn("healthcheck order notification enabled without recipient")
            else:
                self.warn("healthcheck order notification disabled")
            if notification.get("enabled") is True and notification.get("mailFunctionAvailable") is not True:
                self.fail("healthcheck PHP mail function is unavailable while notification is enabled")
            if notification.get("enabled") is True and notification.get("recipientLooksValid") is not True:
                self.fail("healthcheck order notification recipient is not a valid email")
            if notification.get("enabled") is True and notification.get("fromLooksValid") is not True:
                self.fail("healthcheck order notification sender is not a valid email")

        public_naver = data.get("publicNaverPay", {})
        if isinstance(public_naver, dict) and public_naver.get("clientSecretExposed") is True:
            self.fail("healthcheck legacy Naver Pay public config exposes clientSecret")

        readiness = data.get("readiness", {})
        if isinstance(readiness, dict):
            missing_operations = readiness.get("missingForOperations") or []
            if readiness.get("readyForOrderOperations") is True:
                self.ok("healthcheck readyForOrderOperations")
            else:
                self.warn(f"healthcheck operations readiness missing: {missing_operations}")
        else:
            self.warn("healthcheck readiness field is missing")

    def check_tracking_endpoint(self) -> None:
        if self.static_local:
            self.warn("track.php POST skipped in static-local mode")
            return

        response = request(
            self.base_url,
            "/track.php",
            method="POST",
            data={"event": "SmokeTest", "payload": {"source": "deployment-smoke-test"}},
        )
        self.assert_status(response, {200}, "track.php accepts POST")
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.fail("track.php did not return JSON")
            return
        if data.get("ok") is True:
            self.ok("track.php ok=true")
        else:
            self.fail("track.php ok is not true")

    def check_order_store(self) -> None:
        if self.static_local:
            self.warn("order-store POST skipped in static-local mode")
            return
        if not self.write_test_order:
            self.warn("order-store write skipped; pass --write-test-order to test it")
            return

        order_id = f"IT-SMOKE-{int(time.time())}"
        order_payload = {
            "id": order_id,
            "productId": "product-001",
            "selectedOptions": {"색상": "핑크", "타입": "잇템몰 스위트"},
            "quantity": 1,
            "customer": {
                "name": "Smoke Test",
                "phone": "01000000000",
                "email": "smoke@example.com",
                "fulfillmentPrimary": "deployment smoke test",
                "request": "delete if needed",
                "agreeNotice": True,
                "agreeTermsPrivacy": True,
                "agreeContact": False,
            },
            "paymentMethod": "toss_pg",
            "origin": {"page": "smoke-test"},
        }

        invalid_payload = json.loads(json.dumps(order_payload))
        invalid_payload["id"] = f"{order_id}-BAD"
        invalid_payload["customer"]["agreeTermsPrivacy"] = False
        invalid = request(
            self.base_url,
            "/payment/order-store.php",
            method="POST",
            data={"order": invalid_payload},
        )
        self.assert_status(invalid, {400}, "order-store rejects missing terms/privacy consent")
        try:
            invalid_data = json.loads(invalid.text)
        except json.JSONDecodeError:
            self.fail("invalid order-store response did not return JSON")
            return
        if invalid_data.get("error") == "TERMS_PRIVACY_CONSENT_REQUIRED":
            self.ok("order-store reports missing terms/privacy consent")
        else:
            self.fail("order-store invalid consent error was unexpected")

        response = request(
            self.base_url,
            "/payment/order-store.php",
            method="POST",
            data={"order": order_payload},
        )
        self.assert_status(response, {200}, "order-store accepts test order")
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.fail("order-store did not return JSON")
            return
        if data.get("ok") is True and data.get("order", {}).get("id") == order_id:
            self.ok("order-store saved normalized test order")
        else:
            self.fail("order-store response did not confirm saved order")
            return

        if not self.admin_token:
            self.warn("admin fulfillment update skipped; pass --admin-token to test it")
            return

        update = request(
            self.base_url,
            "/payment/admin-orders.php",
            method="POST",
            data={
                "action": "update_fulfillment",
                "orderId": order_id,
                "fulfillmentStatus": "contacted",
                "shipment": {
                    "carrier": "CJ대한통운",
                    "trackingNumber": "SMOKE123456",
                    "trackingUrl": "",
                    "memo": "deployment smoke shipment",
                },
                "adminNote": "deployment smoke test update",
            },
            extra_headers={"X-Ittemmall-Admin-Token": self.admin_token},
        )
        self.assert_status(update, {200}, "admin-orders updates fulfillment")
        try:
            update_data = json.loads(update.text)
        except json.JSONDecodeError:
            self.fail("admin-orders update did not return JSON")
            return
        order = update_data.get("order", {})
        if update_data.get("ok") is True and order.get("fulfillmentStatus") == "contacted":
            self.ok("admin-orders saved fulfillment status")
        else:
            self.fail("admin-orders response did not confirm fulfillment update")
        shipment = order.get("shipment", {})
        if isinstance(shipment, dict) and shipment.get("trackingNumber") == "SMOKE123456":
            self.ok("admin-orders saved shipment tracking")
        else:
            self.fail("admin-orders response did not confirm shipment tracking")
        tracking_url = shipment.get("trackingUrl") if isinstance(shipment, dict) else ""
        if isinstance(tracking_url, str) and "trace.cjlogistics.com" in tracking_url and "SMOKE123456" in tracking_url:
            self.ok("admin-orders auto-generated CJ shipment tracking URL")
        else:
            self.fail("admin-orders did not auto-generate CJ shipment tracking URL")

    def run(self) -> int:
        self.check_home()
        self.check_static_assets()
        self.check_payment_pages()
        self.check_protected_paths()
        self.check_php_health()
        self.check_tracking_endpoint()
        self.check_order_store()

        print("")
        if self.warnings:
            print("Warnings:")
            for warning in self.warnings:
                print(f"- {warning}")
        if self.failures:
            print("Failures:")
            for failure in self.failures:
                print(f"- {failure}")
            return 1
        print("Smoke test passed.")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test a ITTEMMALL deployment.")
    parser.add_argument("--base-url", default="https://ittemmall.com", help="Deployment base URL")
    parser.add_argument(
        "--static-local",
        action="store_true",
        help="Use when testing with python -m http.server where PHP and .htaccess are not executed.",
    )
    parser.add_argument(
        "--require-naver-config",
        action="store_true",
        help="Legacy no-op option kept for old command compatibility.",
    )
    parser.add_argument(
        "--write-test-order",
        action="store_true",
        help="POST a smoke-test order to payment/order-store.php.",
    )
    parser.add_argument(
        "--admin-token",
        default="",
        help="Optional ITTEMMALL_ADMIN_TOKEN. With --write-test-order, also tests admin fulfillment updates.",
    )
    args = parser.parse_args()

    return Smoke(
        base_url=args.base_url,
        static_local=args.static_local,
        require_naver_config=args.require_naver_config,
        write_test_order=args.write_test_order,
        admin_token=args.admin_token,
    ).run()


if __name__ == "__main__":
    sys.exit(main())
