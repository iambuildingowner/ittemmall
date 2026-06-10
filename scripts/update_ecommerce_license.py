from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Replacement:
    path: Path
    description: str
    pattern: re.Pattern[str]
    template: str


def clean_license(value: str) -> str:
    license_number = str(value or "").strip()
    if not license_number:
        raise ValueError("--license is required.")
    if any(ord(char) < 32 for char in license_number):
        raise ValueError("--license must not contain control characters.")
    if len(license_number) > 80:
        raise ValueError("--license looks too long.")
    return license_number


def replacements(license_number: str) -> list[Replacement]:
    html_text = license_number.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    quoted_js = license_number.replace("\\", "\\\\").replace('"', '\\"')
    markdown_text = license_number.replace("|", "\\|")
    return [
        Replacement(
            ROOT / "index.html",
            "front-end legal config",
            re.compile(r'(ecommerceLicense:\s*")[^"]*(")'),
            rf"\g<1>{quoted_js}\g<2>",
        ),
        Replacement(
            ROOT / "legal" / "business.html",
            "business info page definition list",
            re.compile(r"(<dt>통신판매업 신고번호</dt>\s*<dd>)[^<]*(</dd>)"),
            rf"\g<1>{html_text}\g<2>",
        ),
        Replacement(
            ROOT / "legal" / "business.html",
            "business info intro copy",
            re.compile(r"통신판매업 신고번호는 발급 후 추가 반영합니다\."),
            "통신판매업 신고번호를 반영했습니다.",
        ),
        Replacement(
            ROOT / "legal" / "business.html",
            "business info notice",
            re.compile(r"통신판매업 신고번호와 고객센터 번호는 운영 확정 후 최종값으로 다시 확인해야 합니다\."),
            "통신판매업 신고번호와 고객센터 번호를 운영 기준으로 반영했습니다.",
        ),
        Replacement(
            ROOT / "legal" / "terms.html",
            "terms business info",
            re.compile(r"(통신판매업 신고번호:\s*)[^<]*(<br />)"),
            rf"\g<1>{html_text}\g<2>",
        ),
        Replacement(
            ROOT / "legal" / "terms.html",
            "terms notice",
            re.compile(r"본 약관은 운영 준비용 기본안입니다\. 통신판매업 신고번호와 최종 약관 문구는 운영자가 확정해야 합니다\."),
            "본 약관은 운영 기준에 따라 통신판매업 신고번호를 반영한 기본안입니다.",
        ),
        Replacement(
            ROOT / "ITTEMMALL_LAUNCH_OWNER_CHECKLIST.md",
            "owner checklist status",
            re.compile(r"잇템몰 표시용 통신판매업 신고정보: 정부24 변경신고 완료 후 반영"),
            f"잇템몰 표시용 통신판매업 신고번호: {markdown_text}",
        ),
        Replacement(
            ROOT / "ITTEMMALL_OWNER_GATE_SUBMISSION_PACKET_2026-06-10.md",
            "submission packet common value",
            re.compile(r"(\| 통신판매업 신고정보 \| )기존 신고 변경 완료 후 잇템몰 기준으로 반영( \|)"),
            rf"| 통신판매업 신고번호 | {markdown_text} |",
        ),
        Replacement(
            ROOT / "ITTEMMALL_OWNER_GATE_ACTION_BOARD_2026-06-10.md",
            "action board toss prerequisite",
            re.compile(r"(\| \[ \] \| )통신판매업 신고정보( \| )정부24 변경 완료 후 반영( \|)"),
            rf"\g<1>통신판매업 신고번호\g<2>{markdown_text}\g<3>",
        ),
    ]


def apply_replacement(replacement: Replacement, dry_run: bool) -> bool:
    if not replacement.path.is_file():
        raise FileNotFoundError(replacement.path)
    source = replacement.path.read_text(encoding="utf-8")
    rendered, count = replacement.pattern.subn(replacement.template, source, count=1)
    if count != 1:
        raise RuntimeError(f"Expected exactly one match for {replacement.description}: {replacement.path}")
    if rendered == source:
        return False
    if not dry_run:
        replacement.path.write_text(rendered, encoding="utf-8")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update ITTEMMALL ecommerce license number across source pages.")
    parser.add_argument("--license", required=True, help="Issued mail-order/ecommerce license number.")
    parser.add_argument("--dry-run", action="store_true", help="Validate replacements without writing files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        license_number = clean_license(args.license)
        changed: list[str] = []
        for replacement in replacements(license_number):
            if apply_replacement(replacement, args.dry_run):
                changed.append(str(replacement.path.relative_to(ROOT)))
    except (ValueError, FileNotFoundError, RuntimeError) as error:
        raise SystemExit(str(error)) from error

    action = "Would update" if args.dry_run else "Updated"
    print(f"{action} ecommerce license: {license_number}")
    for path in changed:
        print(f"- {path}")
    if args.dry_run:
        print("Dry run only. Re-run without --dry-run after the issued number is confirmed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
