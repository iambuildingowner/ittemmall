from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import build_deployment_package as package
import check_catalog_consistency as catalog


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ROOT = ROOT / "build" / "ittemmall-public"
ZIP_PATH = ROOT / "build" / "ittemmall-public.zip"
SHA256_PATH = ROOT / "build" / "ittemmall-public.zip.sha256"

Status = Literal["PASS", "OWNER", "WARN", "FAIL"]


@dataclass
class Check:
    status: Status
    area: str
    message: str
    next_step: str = ""


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def package_files() -> list[str]:
    if not PUBLIC_ROOT.is_dir():
        return []
    return sorted(path.relative_to(PUBLIC_ROOT).as_posix() for path in PUBLIC_ROOT.rglob("*") if path.is_file())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_config_value(text: str, key: str) -> str:
    pattern = re.compile(rf"\b{re.escape(key)}\s*:\s*([\"'])(.*?)\1")
    match = pattern.search(text)
    return match.group(2).strip() if match else ""


def is_placeholder(value: str) -> bool:
    markers = ["YOUR_", "PUBLIC_", "NAVER_PAY_", "ISSUED_", "TEST_"]
    upper = value.upper()
    return any(marker in upper for marker in markers)


def check_source_files() -> list[Check]:
    checks: list[Check] = []
    missing = [relative for relative in package.FILES if not (ROOT / relative).is_file()]
    if missing:
        checks.append(Check("FAIL", "source", "필수 public 소스 파일이 없습니다: " + ", ".join(missing)))
    else:
        checks.append(Check("PASS", "source", f"필수 public 소스 파일 {len(package.FILES)}개가 있습니다."))

    missing_assets = [relative for relative in package.referenced_assets() if not (ROOT / relative).is_file()]
    if missing_assets:
        checks.append(Check("FAIL", "assets", "HTML에서 참조하는 이미지가 없습니다: " + ", ".join(missing_assets)))
    else:
        checks.append(Check("PASS", "assets", "HTML 참조 이미지가 모두 존재합니다."))
    return checks


def check_catalog() -> list[Check]:
    try:
        frontend = catalog.frontend_products()
        backend = catalog.backend_products()
        problems = catalog.compare_catalogs(frontend, backend)
    except ValueError as error:
        return [Check("FAIL", "catalog", f"상품 카탈로그 검증 실패: {error}")]

    if problems:
        return [Check("FAIL", "catalog", " / ".join(problems))]
    return [Check("PASS", "catalog", f"프론트와 서버 상품 카탈로그가 일치합니다. 상품 {len(frontend)}개.")]


def check_order_store_safety() -> list[Check]:
    text = read_text(ROOT / "payment" / "order-store-lib.php")
    required_snippets = [
        "ittemmallWithOrderStoreLock",
        "flock($lock, LOCK_EX)",
        "ORDER_STORE_LOCK_FAILED",
        "ittemmallWriteServerOrders",
        "$path . '.bak'",
        "ittemmallOrderPaymentLocked",
    ]
    missing = [snippet for snippet in required_snippets if snippet not in text]
    if missing:
        return [Check("FAIL", "order-store", "주문 저장소 lock/backup 안전장치가 빠져 있습니다: " + ", ".join(missing))]
    return [Check("PASS", "order-store", "주문 저장소는 lock 기반 read/write와 .bak 백업 안전장치를 포함합니다.")]


def check_payment_safeguards() -> list[Check]:
    approve = read_text(ROOT / "payment" / "naverpay-approve.php")
    cancel = read_text(ROOT / "payment" / "naverpay-cancel.php")
    required = [
        "ORDER_NOT_NAVER_PAY",
        "ORDER_NOT_READY_FOR_APPROVAL",
        "ORDER_ALREADY_APPROVED",
        "'idempotent' => true",
        "PARTIAL_CANCEL_NOT_SUPPORTED",
    ]
    missing = [snippet for snippet in required if snippet not in approve + cancel]
    if missing:
        return [Check("FAIL", "payment", "네이버페이 승인/취소 안전장치가 빠져 있습니다: " + ", ".join(missing))]
    return [Check("PASS", "payment", "네이버페이 승인 전 상태 검증, 중복 승인 멱등 처리, 전체취소 보호 장치가 있습니다.")]


def check_admin_operations() -> list[Check]:
    admin_api = read_text(ROOT / "payment" / "admin-orders.php")
    admin_ui = read_text(ROOT / "payment" / "admin.html")
    order_lib = read_text(ROOT / "payment" / "order-store-lib.php")
    required = [
        "ittemmallCleanShipment",
        "ittemmallShipmentTrackingUrl",
        "trackingUrlAuto",
        "trackingNumber",
        "shipmentCarrier",
        "shipmentTrackingNumber",
        "shipmentTrackingUrl",
        "발송일",
        "CSV",
    ]
    missing = [snippet for snippet in required if snippet not in admin_api + admin_ui + order_lib]
    if missing:
        return [Check("FAIL", "admin", "관리자 배송/송장 운영 필드가 빠져 있습니다: " + ", ".join(missing))]
    return [Check("PASS", "admin", "관리자 주문 상세에서 택배사, 송장번호, 배송조회 URL, 발송 메모를 저장하고 CSV로 내보낼 수 있으며 알려진 택배사는 배송조회 URL을 자동 생성합니다.")]


def check_customer_order_lookup() -> list[Check]:
    lookup_php = read_text(ROOT / "payment" / "order-lookup.php")
    lookup_html = read_text(ROOT / "payment" / "order-lookup.html")
    index = read_text(ROOT / "index.html")
    required = [
        "orderLookupContactMatches",
        "orderLookupPublicOrder",
        "order-lookup.php",
        "주문 조회",
        "개인정보 보호",
        "./payment/order-lookup.html",
    ]
    missing = [snippet for snippet in required if snippet not in lookup_php + lookup_html + index]
    if missing:
        return [Check("FAIL", "order-lookup", "고객 주문 조회 기능이 빠져 있습니다: " + ", ".join(missing))]
    return [Check("PASS", "order-lookup", "고객이 주문번호와 이메일/전화로 결제/배송 상태를 조회할 수 있고 개인정보는 공개 응답에서 제외됩니다.")]


def check_rate_limit_safety() -> list[Check]:
    text = read_text(ROOT / "payment" / "rate-limit-lib.php")
    endpoints = "\n".join([
        read_text(ROOT / "payment" / "order-store.php"),
        read_text(ROOT / "payment" / "naverpay-approve.php"),
        read_text(ROOT / "track.php"),
    ])
    required = [
        "ittemmallRateLimitCheck",
        "ITTEMMALL_RATE_LIMIT_PATH",
        "ITTEMMALL_ORDER_STORE_PATH",
        "RATE_LIMITED",
        "order-store",
        "naverpay-approve",
        "track",
    ]
    missing = [snippet for snippet in required if snippet not in text + endpoints]
    if missing:
        return [Check("FAIL", "rate-limit", "주문/승인/추적 호출 제한 장치가 빠져 있습니다: " + ", ".join(missing))]
    return [Check("PASS", "rate-limit", "주문 저장, 네이버페이 승인, 추적 POST에 private 파일 기반 호출 제한이 있습니다.")]


def check_public_package() -> list[Check]:
    checks: list[Check] = []
    files = package_files()
    if not files:
        return [
            Check(
                "FAIL",
                "package",
                "build/ittemmall-public 폴더가 없습니다.",
                "python3 scripts/build_deployment_package.py 를 실행하세요.",
            )
        ]

    problems = package.verify_package()
    if problems:
        checks.append(Check("FAIL", "package", "public 패키지 검증 실패: " + " / ".join(problems)))
    else:
        checks.append(Check("PASS", "package", f"public 업로드 폴더가 검증되었습니다. 포함 파일 {len(files)}개."))

    if not ZIP_PATH.is_file():
        checks.append(
            Check(
                "FAIL",
                "zip",
                "배포 ZIP이 없습니다.",
                "python3 scripts/build_deployment_package.py 를 실행하세요.",
            )
        )
    elif not SHA256_PATH.is_file():
        checks.append(Check("FAIL", "zip", "ZIP checksum 파일이 없습니다."))
    else:
        actual = sha256(ZIP_PATH)
        expected = SHA256_PATH.read_text(encoding="utf-8").split()[0]
        if actual == expected:
            checks.append(Check("PASS", "zip", f"ZIP SHA256이 일치합니다: {actual}"))
        else:
            checks.append(Check("FAIL", "zip", "ZIP SHA256이 checksum 파일과 다릅니다."))

        try:
            with zipfile.ZipFile(ZIP_PATH) as archive:
                zip_files = sorted(archive.namelist())
        except zipfile.BadZipFile:
            checks.append(Check("FAIL", "zip", "배포 ZIP을 열 수 없습니다."))
        else:
            if zip_files == files:
                checks.append(Check("PASS", "zip", "ZIP 파일 목록이 public 업로드 폴더와 일치합니다."))
            else:
                checks.append(Check("FAIL", "zip", "ZIP 파일 목록이 public 업로드 폴더와 다릅니다."))
    return checks


def check_public_naver_config() -> list[Check]:
    checks: list[Check] = []
    text = read_text(ROOT / "payment" / "naverpay-config.js")
    if "ITTEMMALL_NAVER_PAY_CONFIG" not in text:
        return [Check("FAIL", "naver-public", "payment/naverpay-config.js에 ITTEMMALL_NAVER_PAY_CONFIG가 없습니다.")]

    if "clientSecret" in text or "CLIENT_SECRET" in text:
        checks.append(Check("FAIL", "naver-public", "public JS에 clientSecret처럼 보이는 문자열이 있습니다."))
    else:
        checks.append(Check("PASS", "naver-public", "public JS에는 clientSecret 필드가 없습니다."))

    client_id = extract_config_value(text, "clientId")
    chain_id = extract_config_value(text, "chainId")
    mode = extract_config_value(text, "mode")

    if not client_id or not chain_id:
        checks.append(
            Check(
                "OWNER",
                "naver-public",
                "Naver Pay public clientId/chainId가 아직 비어 있습니다.",
                "가맹점 발급 후 scripts/generate_public_naverpay_config.py 로 payment/naverpay-config.js를 생성하세요.",
            )
        )
    elif is_placeholder(client_id) or is_placeholder(chain_id):
        checks.append(
            Check(
                "OWNER",
                "naver-public",
                "Naver Pay public 설정이 예시/테스트 값으로 보입니다.",
                "실제 발급 clientId/chainId로 다시 생성하세요.",
            )
        )
    else:
        checks.append(Check("PASS", "naver-public", "Naver Pay public clientId/chainId가 채워져 있습니다."))

    if mode == "production":
        checks.append(Check("PASS", "naver-public", "Naver Pay public mode가 production입니다."))
    elif mode == "development":
        checks.append(
            Check(
                "OWNER",
                "naver-public",
                "Naver Pay public mode가 development입니다.",
                "실운영 전 --mode production 으로 public config를 다시 생성하세요.",
            )
        )
    else:
        checks.append(Check("FAIL", "naver-public", "Naver Pay public mode 값을 읽지 못했습니다."))
    return checks


def check_public_toss_config() -> list[Check]:
    checks: list[Check] = []
    text = read_text(ROOT / "payment" / "toss-config.js")
    if "ITTEMMALL_TOSS_PAYMENTS_CONFIG" not in text:
        return [Check("FAIL", "toss-public", "payment/toss-config.js에 ITTEMMALL_TOSS_PAYMENTS_CONFIG가 없습니다.")]

    if "SECRET_KEY" in text or "secretKey" in text:
        checks.append(Check("FAIL", "toss-public", "public JS에 Toss secret처럼 보이는 문자열이 있습니다."))
    else:
        checks.append(Check("PASS", "toss-public", "public JS에는 Toss secret 필드가 없습니다."))

    client_key = extract_config_value(text, "clientKey")
    if not client_key:
        checks.append(
            Check(
                "OWNER",
                "toss-public",
                "Toss public clientKey가 아직 비어 있습니다.",
                "Toss PG 심사/계약 후 발급받은 client key를 payment/toss-config.js에 넣으세요.",
            )
        )
    elif is_placeholder(client_key):
        checks.append(
            Check(
                "OWNER",
                "toss-public",
                "Toss public 설정이 예시 값으로 보입니다.",
                "실제 발급 client key로 바꾸세요.",
            )
        )
    else:
        checks.append(Check("PASS", "toss-public", "Toss public clientKey가 채워져 있습니다."))

    if re.search(r"\benabled\s*:\s*true\b", text):
        checks.append(Check("PASS", "toss-public", "Toss 결제 활성화 플래그가 true입니다."))
    else:
        checks.append(Check("OWNER", "toss-public", "Toss 결제 활성화 플래그가 false입니다.", "실제 결제 검증 후 enabled=true로 바꾸세요."))
    return checks


def check_private_setup() -> list[Check]:
    checks: list[Check] = []
    if (ROOT / "scripts" / "generate_private_config.py").is_file():
        checks.append(Check("PASS", "naver-private", "private PHP 설정 생성 스크립트가 있습니다."))
    else:
        checks.append(Check("FAIL", "naver-private", "scripts/generate_private_config.py가 없습니다."))

    if (ROOT / "private" / "ittemmall-server-config.example.php").is_file():
        checks.append(Check("PASS", "naver-private", "private server config 예시가 있습니다."))
    else:
        checks.append(Check("FAIL", "naver-private", "private/ittemmall-server-config.example.php가 없습니다."))

    release_script = read_text(ROOT / "scripts" / "prepare_production_release.py")
    if (ROOT / "scripts" / "prepare_production_release.py").is_file() and (
        ROOT / "private" / "ittemmall-production-release.example.json"
    ).is_file():
        checks.append(Check("PASS", "release", "통합 production release 준비 스크립트와 예시 JSON이 있습니다."))
    else:
        checks.append(Check("FAIL", "release", "통합 production release 준비 스크립트 또는 예시 JSON이 없습니다."))

    release_backup_required = [
        "backup_release_sources",
        "DEFAULT_BACKUP_DIR",
        "manifest.json",
        "--no-backup",
    ]
    missing_release_backup = [snippet for snippet in release_backup_required if snippet not in release_script]
    if missing_release_backup:
        checks.append(Check("FAIL", "release", "production release 원본 백업 장치가 빠져 있습니다: " + ", ".join(missing_release_backup)))
    else:
        checks.append(Check("PASS", "release", "production release 전에 legal/public config 원본 백업과 manifest를 남깁니다."))

    packaged = set(package_files())
    leaked_private = [name for name in packaged if name.startswith("private/") or "ittemmall-private" in name]
    leaked_examples = [name for name in packaged if name.endswith(".example.php") or name.endswith(".example.js")]
    leaked_internal_docs = [
        name for name in packaged
        if name.endswith(".md") or name in {"DEPLOYMENT_MANIFEST.md", "ITTEMMALL_LAUNCH_OWNER_CHECKLIST.md"}
    ]
    if leaked_private or leaked_examples or leaked_internal_docs:
        checks.append(
            Check(
                "FAIL",
                "security",
                "public 패키지에 private/example/internal 문서가 포함되었습니다: "
                + ", ".join(sorted(leaked_private + leaked_examples + leaked_internal_docs)),
            )
        )
    else:
        checks.append(Check("PASS", "security", "public 패키지에 private/example/internal 문서가 없습니다."))

    root_htaccess = read_text(ROOT / ".htaccess")
    if "ITTEMMALL_LAUNCH_OWNER_CHECKLIST" in root_htaccess or r"\.(md|xlsx?" in root_htaccess:
        checks.append(Check("PASS", "security", "루트 .htaccess가 Markdown 등 내부 문서 공개를 차단합니다."))
    else:
        checks.append(Check("FAIL", "security", "루트 .htaccess에 내부 문서 차단 규칙이 없습니다."))

    checks.append(
        Check(
            "OWNER",
            "naver-private",
            "실제 NAVER_PAY_CLIENT_SECRET과 ITTEMMALL_ADMIN_TOKEN은 운영 서버 private config에 넣어야 합니다.",
            "build/ittemmall-private/ittemmall-server-config.php를 생성한 뒤 public web root 밖에 업로드하세요.",
        )
    )
    return checks


def check_legal_pages() -> list[Check]:
    checks: list[Check] = []
    legal_pages = [
        "legal/business.html",
        "legal/terms.html",
        "legal/privacy.html",
        "legal/refund.html",
    ]
    missing = [relative for relative in legal_pages if not (ROOT / relative).is_file()]
    if missing:
        checks.append(Check("FAIL", "legal", "정책 페이지가 없습니다: " + ", ".join(missing)))
        return checks

    if (ROOT / "scripts" / "fill_legal_owner_info.py").is_file():
        checks.append(Check("PASS", "legal", "정책 페이지 OWNER 정보 자동 주입 스크립트가 있습니다."))
    else:
        checks.append(Check("FAIL", "legal", "scripts/fill_legal_owner_info.py가 없습니다."))

    packaged = set(package_files())
    missing_from_package = [relative for relative in legal_pages if relative not in packaged]
    if missing_from_package:
        checks.append(Check("FAIL", "legal", "정책 페이지가 public 패키지에 없습니다: " + ", ".join(missing_from_package)))
    else:
        checks.append(Check("PASS", "legal", "사업자 정보/이용약관/개인정보/환불 안내 페이지가 public 패키지에 포함되어 있습니다."))

    combined = "\n".join(read_text(ROOT / relative) for relative in legal_pages)
    if "ITTEMMALL_OWNER_TODO" in combined:
        checks.append(
            Check(
                "OWNER",
                "legal",
                "정책 페이지에 실제 사업자/배송/개인정보 책임자 입력값이 남아 있습니다.",
                "legal/*.html의 ITTEMMALL_OWNER_TODO_* 값을 실제 운영 정보로 교체하세요.",
            )
        )
    else:
        checks.append(Check("PASS", "legal", "정책 페이지의 OWNER TODO 값이 모두 교체되었습니다."))

    sitemap = read_text(ROOT / "sitemap.xml")
    missing_sitemap = [
        relative for relative in legal_pages if f"https://ittemmall.com/{relative}" not in sitemap
    ]
    if missing_sitemap:
        checks.append(Check("FAIL", "seo", "sitemap.xml에 빠진 정책 페이지가 있습니다: " + ", ".join(missing_sitemap)))
    else:
        checks.append(Check("PASS", "seo", "sitemap.xml에 정책 페이지 URL이 포함되어 있습니다."))

    index = read_text(ROOT / "index.html")
    if "agreeTermsPrivacy" in index and "./legal/terms.html" in index and "./legal/privacy.html" in index:
        checks.append(Check("PASS", "legal", "주문서가 이용약관/개인정보처리방침 필수 동의와 연결되어 있습니다."))
    else:
        checks.append(Check("FAIL", "legal", "주문서에 이용약관/개인정보처리방침 필수 동의 연결이 없습니다."))
    return checks


def check_docs() -> list[Check]:
    checks: list[Check] = []
    manifest = read_text(ROOT / "DEPLOYMENT_MANIFEST.md")
    setup = read_text(ROOT / "payment" / "NAVERPAY_SETUP.md")
    owner_checklist = read_text(ROOT / "ITTEMMALL_LAUNCH_OWNER_CHECKLIST.md")
    required_snippets = [
        "ITTEMMALL_LAUNCH_OWNER_CHECKLIST.md",
        "private/ittemmall-production-release.production.json",
        "check_catalog_consistency.py",
        "generate_public_naverpay_config.py",
        "generate_private_config.py",
        "prepare_production_release.py",
        "release-backups",
        "--no-backup",
        "smoke_test_deployment.py",
        "live_deployment_report.py",
        "rate-limit-lib.php",
        "ITTEMMALL_RATE_LIMIT_PATH",
        "payment/healthcheck.php",
        "payment/ops.html",
        "payment/notification-test.php",
        "legal/business.html",
        "legal/privacy.html",
        "legal/refund.html",
        "NAVER_PAY_APPROVE_ENABLED=1",
        "NAVER_PAY_CANCEL_ENABLED=1",
    ]
    missing = [snippet for snippet in required_snippets if snippet not in manifest + setup + owner_checklist]
    if missing:
        checks.append(Check("FAIL", "docs", "운영 문서에 빠진 절차가 있습니다: " + ", ".join(missing)))
    else:
        checks.append(Check("PASS", "docs", "운영 문서에 오너 입력 체크리스트, 설정 생성, 헬스체크, 스모크 테스트 절차가 있습니다."))
    return checks


def build_report() -> list[Check]:
    checks: list[Check] = []
    checks.extend(check_source_files())
    checks.extend(check_catalog())
    checks.extend(check_order_store_safety())
    checks.extend(check_payment_safeguards())
    checks.extend(check_admin_operations())
    checks.extend(check_customer_order_lookup())
    checks.extend(check_rate_limit_safety())
    checks.extend(check_public_package())
    checks.extend(check_public_toss_config())
    checks.extend(check_public_naver_config())
    checks.extend(check_private_setup())
    checks.extend(check_legal_pages())
    checks.extend(check_docs())
    return checks


def render_text(checks: list[Check]) -> str:
    labels = {
        "PASS": "OK",
        "OWNER": "OWNER",
        "WARN": "WARN",
        "FAIL": "FAIL",
    }
    lines = [
        "ITTEMMALL deployment readiness report",
        "",
    ]
    for check in checks:
        lines.append(f"[{labels[check.status]}] {check.area}: {check.message}")
        if check.next_step:
            lines.append(f"      next: {check.next_step}")
    lines.append("")
    summary = {status: sum(1 for check in checks if check.status == status) for status in ["PASS", "OWNER", "WARN", "FAIL"]}
    lines.append(
        "Summary: "
        + ", ".join(f"{key}={value}" for key, value in summary.items())
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Report ITTEMMALL local deployment readiness.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument(
        "--allow-owner-tasks",
        action="store_true",
        help="Exit 0 when only owner-provided production keys/hosting tasks remain.",
    )
    args = parser.parse_args()

    checks = build_report()
    if args.json:
        print(json.dumps([check.__dict__ for check in checks], ensure_ascii=False, indent=2))
    else:
        print(render_text(checks))

    if any(check.status == "FAIL" for check in checks):
        return 1
    if any(check.status == "OWNER" for check in checks) and not args.allow_owner_tasks:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
