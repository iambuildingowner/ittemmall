from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SHOP_NAME = "잇템몰"
EXPECTED_URL = "https://ittemmall.com"
EXPECTED_BUSINESS_NUMBER = "221-31-17043"
OLD_DOMAIN = "byuljangdaejang.com"

Status = Literal["PASS", "OWNER", "WARN", "FAIL"]
ALLOWED_STAGE_STATUS = {"pending", "ready", "complete"}


@dataclass
class Check:
    status: Status
    area: str
    message: str


def normalize_url(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    raw = raw.rstrip("/")
    if raw.startswith("http://"):
        raw = "https://" + raw[len("http://") :]
    return raw.lower()


def normalize_business_number(value: str) -> str:
    digits = re.sub(r"\D+", "", str(value or ""))
    if len(digits) != 10:
        return str(value or "").strip()
    return f"{digits[:3]}-{digits[3:5]}-{digits[5:]}"


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise SystemExit(f"Intake file not found: {path}") from error
    except json.JSONDecodeError as error:
        raise SystemExit(f"Invalid JSON in {path}: {error}") from error
    if not isinstance(data, dict):
        raise SystemExit("Intake JSON must be an object.")
    return data


def section(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key, {})
    return value if isinstance(value, dict) else {}


def stage_status(value: dict[str, Any]) -> str:
    status = str(value.get("status", "pending") or "pending").strip().lower()
    return status


def check_stage_status(area: str, value: dict[str, Any]) -> list[Check]:
    status = stage_status(value)
    if status not in ALLOWED_STAGE_STATUS:
        return [Check("FAIL", area, f"status must be one of {sorted(ALLOWED_STAGE_STATUS)}.")]
    if status == "pending":
        return [Check("OWNER", area, "아직 오너 인증/발급 대기 상태입니다.")]
    return []


def check_file(area: str, value: dict[str, Any], require_files: bool) -> list[Check]:
    file_path = str(value.get("file_path", "") or "").strip()
    if not file_path:
        return [Check("OWNER", area, "증빙 파일 경로가 아직 비어 있습니다.")]
    path = Path(file_path).expanduser()
    if not path.is_absolute():
        path = ROOT / path
    if require_files and not path.is_file():
        return [Check("FAIL", area, f"증빙 파일이 없습니다: {path}")]
    return [Check("PASS", area, f"증빙 파일 경로가 입력되었습니다: {path}")]


def check_purchase_certificate(data: dict[str, Any], require_files: bool) -> list[Check]:
    cert = section(data, "purchase_safety_certificate")
    checks = check_stage_status("purchase-safety", cert)
    if stage_status(cert) == "pending":
        return checks

    checks.extend(check_file("purchase-safety", cert, require_files))
    issuer = str(cert.get("issuer", "") or "").strip()
    issued_at = str(cert.get("issued_at", "") or "").strip()
    shop_name = str(cert.get("shop_name", "") or "").strip()
    shop_url = normalize_url(str(cert.get("shop_url", "") or ""))
    business_number = normalize_business_number(str(cert.get("business_registration_number", "") or ""))

    if issuer:
        checks.append(Check("PASS", "purchase-safety", f"발급기관 입력됨: {issuer}"))
    else:
        checks.append(Check("OWNER", "purchase-safety", "발급기관명이 필요합니다."))

    if issued_at:
        checks.append(Check("PASS", "purchase-safety", f"발급일 입력됨: {issued_at}"))
    else:
        checks.append(Check("OWNER", "purchase-safety", "발급일이 필요합니다."))

    if shop_name == EXPECTED_SHOP_NAME:
        checks.append(Check("PASS", "purchase-safety", "쇼핑몰명이 잇템몰입니다."))
    else:
        checks.append(Check("FAIL", "purchase-safety", f"쇼핑몰명이 잇템몰이 아닙니다: {shop_name or '(empty)'}"))

    if shop_url == EXPECTED_URL:
        checks.append(Check("PASS", "purchase-safety", "URL이 잇템몰 기준입니다."))
    else:
        checks.append(Check("FAIL", "purchase-safety", f"URL이 잇템몰 기준이 아닙니다: {shop_url or '(empty)'}"))

    if business_number == EXPECTED_BUSINESS_NUMBER:
        checks.append(Check("PASS", "purchase-safety", "사업자등록번호가 일치합니다."))
    else:
        checks.append(Check("FAIL", "purchase-safety", f"사업자등록번호가 다릅니다: {business_number or '(empty)'}"))

    return checks


def check_change_report(data: dict[str, Any], require_files: bool) -> list[Check]:
    report = section(data, "ecommerce_change_report")
    checks = check_stage_status("ecommerce-change", report)
    if stage_status(report) == "pending":
        return checks

    checks.extend(check_file("ecommerce-change", report, require_files))
    license_number = str(report.get("license_number", "") or "").strip()
    registered_domain = normalize_url(str(report.get("registered_domain", "") or ""))
    processed_at = str(report.get("processed_at", "") or "").strip()
    agency = str(report.get("agency", "") or "").strip()

    if license_number:
        checks.append(Check("PASS", "ecommerce-change", f"통신판매번호 입력됨: {license_number}"))
    else:
        checks.append(Check("FAIL", "ecommerce-change", "통신판매번호가 필요합니다."))

    if registered_domain == EXPECTED_URL:
        checks.append(Check("PASS", "ecommerce-change", "등록 도메인이 잇템몰 기준입니다."))
    else:
        checks.append(Check("FAIL", "ecommerce-change", f"등록 도메인이 잇템몰 기준이 아닙니다: {registered_domain or '(empty)'}"))

    if processed_at:
        checks.append(Check("PASS", "ecommerce-change", f"변경 처리일 입력됨: {processed_at}"))
    else:
        checks.append(Check("OWNER", "ecommerce-change", "변경 처리일이 필요합니다."))

    if agency:
        checks.append(Check("PASS", "ecommerce-change", f"신고기관 입력됨: {agency}"))
    else:
        checks.append(Check("OWNER", "ecommerce-change", "신고기관명이 필요합니다."))

    return checks


def check_hostinger(data: dict[str, Any]) -> list[Check]:
    hostinger = section(data, "hostinger")
    checks = check_stage_status("hostinger", hostinger)
    if stage_status(hostinger) == "pending":
        return checks

    server_location = str(hostinger.get("server_location", "") or "").strip()
    private_available = bool(hostinger.get("private_storage_available", False))
    public_web_root = str(hostinger.get("public_web_root", "") or "").strip()

    if server_location:
        checks.append(Check("PASS", "hostinger", f"호스트서버 소재지 입력됨: {server_location}"))
    else:
        checks.append(Check("OWNER", "hostinger", "hPanel 기준 호스트서버 소재지가 필요합니다."))

    if public_web_root:
        checks.append(Check("PASS", "hostinger", f"public web root 입력됨: {public_web_root}"))
    else:
        checks.append(Check("OWNER", "hostinger", "public web root 확인값이 필요합니다."))

    if private_available:
        checks.append(Check("PASS", "hostinger", "public web root 밖 private 저장소 사용 가능으로 표시됐습니다."))
    else:
        checks.append(Check("OWNER", "hostinger", "운영 서버 private 저장소 가능 여부 확인이 필요합니다."))

    return checks


def check_notes(data: dict[str, Any]) -> list[Check]:
    haystack = json.dumps(data, ensure_ascii=False).lower()
    if OLD_DOMAIN in haystack:
        return [Check("WARN", "notes", "기존 별장대장 도메인이 입력값에 남아 있습니다. 기준값 메모인지 실제 신청값인지 확인하세요.")]
    return []


def render(checks: list[Check]) -> str:
    lines = ["ITTEMMALL owner gate intake report"]
    counts = {status: 0 for status in ("PASS", "OWNER", "WARN", "FAIL")}
    for check in checks:
        counts[check.status] += 1
        lines.append(f"[{check.status}] {check.area}: {check.message}")
    lines.append("")
    lines.append(
        "Summary: "
        + ", ".join(f"{status}={counts[status]}" for status in ("PASS", "OWNER", "WARN", "FAIL"))
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Ittemmall owner gate intake values before site updates.")
    parser.add_argument(
        "--intake",
        default="private/owner-gate-intake.example.json",
        help="Path to owner gate intake JSON. Use a local private copy for real files.",
    )
    parser.add_argument("--require-files", action="store_true", help="Fail when referenced evidence files do not exist.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    intake_path = Path(args.intake)
    if not intake_path.is_absolute():
        intake_path = ROOT / intake_path
    data = read_json(intake_path)
    checks: list[Check] = []
    checks.extend(check_purchase_certificate(data, args.require_files))
    checks.extend(check_change_report(data, args.require_files))
    checks.extend(check_hostinger(data))
    checks.extend(check_notes(data))

    print(render(checks))
    return 1 if any(check.status == "FAIL" for check in checks) else 0


if __name__ == "__main__":
    raise SystemExit(main())
