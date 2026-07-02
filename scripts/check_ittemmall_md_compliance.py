#!/usr/bin/env python3
from __future__ import annotations

import argparse
import struct
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


@dataclass
class Check:
    name: str
    status: str
    detail: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def product_block(source: str, slug: str) -> str:
    marker = f'slug: "{slug}"'
    marker_index = source.find(marker)
    if marker_index < 0:
        return ""

    start = source.rfind("{", 0, marker_index)
    if start < 0:
        return ""

    depth = 0
    in_string = False
    quote = ""
    escaped = False
    for index in range(start, len(source)):
        char = source[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                in_string = False
            continue

        if char in {'"', "'", "`"}:
            in_string = True
            quote = char
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start : index + 1]
    return ""


def png_size(path: Path) -> tuple[int, int] | None:
    if path.suffix.lower() != ".png" or not path.is_file():
        return None
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def add(checks: list[Check], name: str, passed: bool, detail: str) -> None:
    checks.append(Check(name=name, status="PASS" if passed else "FAIL", detail=detail))


def add_manual(checks: list[Check], name: str, detail: str) -> None:
    checks.append(Check(name=name, status="MANUAL", detail=detail))


def run_checks(args: argparse.Namespace) -> list[Check]:
    source = read_text(INDEX)
    block = product_block(source, args.product)
    checks: list[Check] = []

    add(checks, "상품 블록", bool(block), f"slug={args.product}")
    if not block:
        return checks

    add(checks, "가격 48,900원", "price: 48900" in block, "index.html product.price 확인")
    add(checks, "정상가/할인율 없음", "originalPrice: 0" in block and "discountRate: 0" in block, "old price/discount 노출 방지")
    add(checks, "N pay 버튼", 'data-checkout-source="npay"' in source and "NpayPurchaseClick" in source, "버튼 클릭 의향 측정 구조 확인")
    add(
        checks,
        "상품별 N pay 픽셀",
        "function productNpayEventName" in source
        and 'data-pixel-event="${escapeHtml(productNpayEventName(currentProduct()))}"' in source
        and 'eventName.startsWith("NpayPurchaseClick_")' in source,
        "NpayPurchaseClick_{상품slug} 이벤트 분리 확인",
    )

    if args.size_sensitive:
        add(checks, "사이즈 옵션", '{ label: "사이즈"' in block, "착용/반품 영향 상품 필수")
        add(checks, "사이즈 설명 이미지 데이터", "sizeGuide:" in block and "windcool-vest-size-guide-photo.jpg" in block, "상세페이지 이미지 필수")
        add(checks, "사이즈표 데이터", "sizeChart:" in block and all(f'size: "{size}"' in block for size in ["M", "L", "XL", "2XL", "3XL"]), "M~3XL 표기")
        add(checks, "측정/권장/오차 안내", "sizeNotes:" in block and "1~3cm" in block and "작업복" in block, "측정 기준과 권장 선택법")

        guide_path = ROOT / "assets/ittemmall/fan-vest/windcool-vest-size-guide-photo.jpg"
        add(checks, "사이즈 이미지 파일", guide_path.is_file(), guide_path.relative_to(ROOT).as_posix())

    add(checks, "상품 정보 중복 방지", "hideStandaloneInfo: true" in block, "사이즈/상품 정보 단일 블록 사용")
    add(checks, "사이즈/상품 정보 제목", 'specTitle: "사이즈 / 상품 정보"' in block, "중복 섹션 대신 단일 제목")

    if args.ad_image:
        ad_path = ROOT / args.ad_image
        add(checks, "광고 이미지 파일", ad_path.is_file(), args.ad_image)
        dimensions = png_size(ad_path)
        if dimensions:
            width, height = dimensions
            add(checks, "광고 이미지 정사각형", width == height, f"{width}x{height}")
        else:
            add(checks, "광고 이미지 정사각형", False, "PNG 파일 크기를 확인할 수 없음")

    add_manual(checks, "광고 이미지 참고 기준", "네이버 쇼핑/Meta 라이브러리 참고 이미지 1개 기준인지 눈으로 확인")
    add_manual(checks, "광고 이미지 단일 장면", "한 명/한 장면/한 시점으로 보이는지 눈으로 확인")
    add_manual(checks, "광고 이미지 문구", "카피 1개와 가격만 자연스럽게 들어갔는지 눈으로 확인")
    add_manual(checks, "운영 N pay 서버 로그 1차", "운영 URL에서 test_run_id로 클릭 후 stored:true 확인, 테스트 로그 삭제")
    add_manual(checks, "운영 N pay 서버 로그 2차", "같은 상품으로 재테스트 후 stored:true 재확인, 테스트 로그 재삭제")
    return checks


def render_markdown(checks: list[Check], args: argparse.Namespace) -> str:
    lines = [
        f"# 잇템몰 MD 준수 검토 - {args.product}",
        "",
        "## 자동/수동 검토 결과",
        "",
        "| 항목 | 상태 | 내용 |",
        "|---|---|---|",
    ]
    for check in checks:
        lines.append(f"| {check.name} | {check.status} | {check.detail} |")
    lines.extend(
        [
            "",
            "## 판정 기준",
            "",
            "- FAIL 항목은 완료 보고 전에 수정한다.",
            "- MANUAL 항목은 실제 이미지/화면을 눈으로 보고 통과 여부를 기록한다.",
            "- 자동 검토가 통과해도 이미지 품질과 상세페이지 중복은 별도 시각 검토가 필요하다.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check ittemmall item outputs against MD rules.")
    parser.add_argument("--product", required=True, help="Product slug, e.g. windcool-vest")
    parser.add_argument("--size-sensitive", action="store_true", help="Require size guide checks")
    parser.add_argument("--ad-image", help="Project-relative ad image path")
    parser.add_argument("--write-report", help="Project-relative markdown report path")
    args = parser.parse_args()

    checks = run_checks(args)
    markdown = render_markdown(checks, args)
    sys.stdout.write(markdown)

    if args.write_report:
        report_path = ROOT / args.write_report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(markdown, encoding="utf-8")

    return 1 if any(check.status == "FAIL" for check in checks) else 0


if __name__ == "__main__":
    raise SystemExit(main())
