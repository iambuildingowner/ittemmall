from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class CatalogProduct:
    id: str
    name: str
    price: int


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def frontend_products(index_path: Path = ROOT / "index.html") -> dict[str, CatalogProduct]:
    text = read_text(index_path)
    match = re.search(r"\bconst\s+products\s*=\s*\[(?P<body>.*?)\n\s*\];", text, re.DOTALL)
    if not match:
        raise ValueError("index.html에서 const products 배열을 찾지 못했습니다.")

    products: dict[str, CatalogProduct] = {}
    product_pattern = re.compile(
        r"\{\s*id:\s*\"(?P<id>product-[^\"]+)\"(?P<body>.*?)(?=\n\s*\{\s*id:\s*\"product-|\n\s*\])",
        re.DOTALL,
    )
    for item in product_pattern.finditer(match.group("body")):
        body = item.group("body")
        if re.search(r"\bretired:\s*true\b", body):
            continue
        name = re.search(r"\bname:\s*\"(?P<name>[^\"]+)\"", body)
        price = re.search(r"\bprice:\s*(?P<price>\d+)", body)
        if not name or not price:
            raise ValueError(f"프론트 상품 {item.group('id')}의 name/price를 읽지 못했습니다.")
        products[item.group("id")] = CatalogProduct(
            id=item.group("id"),
            name=name.group("name").strip(),
            price=int(price.group("price")),
        )

    if not products:
        raise ValueError("index.html에서 상품 항목을 찾지 못했습니다.")
    return products


def backend_products(order_lib_path: Path = ROOT / "payment" / "order-store-lib.php") -> dict[str, CatalogProduct]:
    text = read_text(order_lib_path)
    match = re.search(r"function\s+ittemmallProductCatalog\s*\(\)\s*:\s*array\s*\{(?P<body>.*?)\n\}", text, re.DOTALL)
    if not match:
        raise ValueError("payment/order-store-lib.php에서 ittemmallProductCatalog()를 찾지 못했습니다.")

    products: dict[str, CatalogProduct] = {}
    product_pattern = re.compile(
        r"'(?P<id>product-[^']+)'\s*=>\s*\[(?P<body>.*?)\n\s*\]",
        re.DOTALL,
    )
    for item in product_pattern.finditer(match.group("body")):
        body = item.group("body")
        name = re.search(r"'name'\s*=>\s*'(?P<name>[^']+)'", body)
        price = re.search(r"'price'\s*=>\s*(?P<price>\d+)", body)
        if not name or not price:
            raise ValueError(f"서버 상품 {item.group('id')}의 name/price를 읽지 못했습니다.")
        products[item.group("id")] = CatalogProduct(
            id=item.group("id"),
            name=name.group("name").strip(),
            price=int(price.group("price")),
        )

    if not products:
        raise ValueError("payment/order-store-lib.php에서 상품 항목을 찾지 못했습니다.")
    return products


def compare_catalogs(
    frontend: dict[str, CatalogProduct] | None = None,
    backend: dict[str, CatalogProduct] | None = None,
) -> list[str]:
    frontend = frontend if frontend is not None else frontend_products()
    backend = backend if backend is not None else backend_products()
    problems: list[str] = []

    frontend_ids = set(frontend)
    backend_ids = set(backend)
    for product_id in sorted(frontend_ids - backend_ids):
        problems.append(f"서버 카탈로그에 없는 프론트 상품: {product_id}")
    for product_id in sorted(backend_ids - frontend_ids):
        problems.append(f"프론트 카탈로그에 없는 서버 상품: {product_id}")

    for product_id in sorted(frontend_ids & backend_ids):
        front = frontend[product_id]
        back = backend[product_id]
        if front.name != back.name:
            problems.append(
                f"{product_id} 상품명 불일치: frontend={front.name!r}, backend={back.name!r}"
            )
        if front.price != back.price:
            problems.append(
                f"{product_id} 가격 불일치: frontend={front.price}, backend={back.price}"
            )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that frontend product data matches the server order catalog."
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON for automation.")
    args = parser.parse_args()

    try:
        frontend = frontend_products()
        backend = backend_products()
        problems = compare_catalogs(frontend, backend)
    except ValueError as error:
        print(f"FAIL: {error}")
        return 1

    if problems:
        for problem in problems:
            print(f"FAIL: {problem}")
        return 1

    if args.json:
        print(
            json.dumps(
                [
                    {"id": product.id, "name": product.name, "price": product.price}
                    for product in frontend.values()
                ],
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(f"OK: product catalog matches across frontend and server ({len(frontend)} products).")
        for product_id in sorted(frontend):
            product = frontend[product_id]
            print(f" - {product.id}: {product.name} / {product.price} KRW")
    return 0


if __name__ == "__main__":
    sys.exit(main())
