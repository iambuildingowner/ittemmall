from __future__ import annotations

import hashlib
import re
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD_ROOT = ROOT / "build"
PUBLIC_ROOT = BUILD_ROOT / "ittemmall-public"
ZIP_PATH = BUILD_ROOT / "ittemmall-public.zip"
SHA256_PATH = BUILD_ROOT / "ittemmall-public.zip.sha256"

FILES = [
    ".htaccess",
    "404.html",
    "index.html",
    "제주도/index.html",
    "robots.txt",
    "sitemap.xml",
    "track.php",
    "legal/business.html",
    "legal/privacy.html",
    "legal/refund.html",
    "legal/terms.html",
    "payment/.htaccess",
    "payment/admin.html",
    "payment/index.html",
    "payment/ops.html",
    "payment/order-lookup.html",
    "payment/toss-checkout.html",
    "payment/toss-success.html",
    "payment/toss-fail.html",
    "payment/order-lookup.php",
    "payment/return.html",
    "payment/healthcheck.php",
    "payment/tracking-report.php",
    "payment/admin-orders.php",
    "payment/order-store.php",
    "payment/order-store-lib.php",
    "payment/rate-limit-lib.php",
    "payment/server-config-lib.php",
    "payment/naverpay-approve.php",
    "payment/naverpay-cancel.php",
    "payment/toss-config.js",
    "payment/naverpay-config.js",
    "payment/notification-test.php",
]

ASSET_SOURCE_FILES = [
    "index.html",
    "legal/business.html",
    "legal/privacy.html",
    "legal/refund.html",
    "legal/terms.html",
    "payment/index.html",
    "payment/toss-checkout.html",
    "payment/toss-success.html",
    "payment/toss-fail.html",
    "payment/return.html",
    "payment/admin.html",
    "payment/toss-config.js",
    "payment/naverpay-config.js",
]

EXTRA_PUBLIC_ASSETS = [
    "assets/ittemmall/fan-vest/windcool-vest-meta-ad-senior-charcoal-blue-air-v1.png",
    "assets/ittemmall/fan-vest/windcool-vest-meta-ad-young-blue-air-v1.png",
    "assets/ittemmall/fan-vest/windcool-vest-meta-ad-young-blue-air-59900-v1.png",
]

FORBIDDEN_PARTS = {
    "notes",
    "output",
    "outputs",
    "scripts",
    "private",
    "ittemmall-private",
    "피클볼파트",
}

FORBIDDEN_SUFFIXES = {
    ".md",
    ".xlsx",
    ".xls",
    ".csv",
    ".tsv",
    ".pdf",
    ".txt",
    ".mp4",
    ".wav",
    ".zip",
    ".bak",
    ".log",
    ".json",
    ".jsonl",
}

ALLOWED_SPECIAL_FILES = {
    ".htaccess",
    "payment/.htaccess",
    "assets/ittemmall/favicon.svg",
    "robots.txt",
}


def clean_public_root() -> None:
    if PUBLIC_ROOT.exists():
        shutil.rmtree(PUBLIC_ROOT)
    PUBLIC_ROOT.mkdir(parents=True)
    ZIP_PATH.unlink(missing_ok=True)
    SHA256_PATH.unlink(missing_ok=True)


def copy_file(relative_path: str) -> None:
    source = ROOT / relative_path
    destination = PUBLIC_ROOT / relative_path
    if not source.is_file():
        raise FileNotFoundError(relative_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def relative_posix(path: Path) -> str:
    return path.relative_to(PUBLIC_ROOT).as_posix()


def normalize_asset_path(raw_path: str) -> str:
    while raw_path.startswith("../"):
        raw_path = raw_path[3:]
    if raw_path.startswith("./"):
        raw_path = raw_path[2:]
    return raw_path


def referenced_assets() -> list[str]:
    pattern = re.compile(r"(?:\.\./|\./)?assets/(?:ittemmall|images|fonts)/[A-Za-z0-9._/-]+")
    assets: set[str] = set()
    for relative_path in ASSET_SOURCE_FILES:
        source = ROOT / relative_path
        if not source.is_file():
            raise FileNotFoundError(relative_path)
        for match in pattern.findall(source.read_text(encoding="utf-8")):
            assets.add(normalize_asset_path(match))
    return sorted(assets)


def verify_package() -> list[str]:
    problems: list[str] = []
    for path in PUBLIC_ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = relative_posix(path)
        parts = set(path.relative_to(PUBLIC_ROOT).parts)
        if parts & FORBIDDEN_PARTS:
            problems.append(f"forbidden directory included: {rel}")
        if path.suffix.lower() in FORBIDDEN_SUFFIXES and rel not in ALLOWED_SPECIAL_FILES:
            problems.append(f"forbidden file type included: {rel}")
    for relative_path in FILES:
        if not (PUBLIC_ROOT / relative_path).is_file():
            problems.append(f"required file missing: {relative_path}")
    for relative_path in referenced_assets():
        if not (PUBLIC_ROOT / relative_path).is_file():
            problems.append(f"referenced asset missing: {relative_path}")
    for relative_path in EXTRA_PUBLIC_ASSETS:
        if not (PUBLIC_ROOT / relative_path).is_file():
            problems.append(f"extra public asset missing: {relative_path}")
    return problems


def write_manifest(included_files: list[str]) -> None:
    manifest = BUILD_ROOT / "ittemmall-public-contents.txt"
    manifest.write_text(
        "\n".join(
            [
                "ITTEMMALL public deployment package",
                "Upload the contents of this folder to the ittemmall.com public web root.",
                "",
                "Included files:",
                *included_files,
                "",
                "Do not add private env files, Naver Pay client secret, order JSON, logs, research files, or supplier documents to this folder.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_archive(included_files: list[str]) -> None:
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative_path in included_files:
            archive.write(PUBLIC_ROOT / relative_path, relative_path)

    with ZIP_PATH.open("rb") as source:
        checksum = hashlib.sha256(source.read()).hexdigest()
    SHA256_PATH.write_text(f"{checksum}  {ZIP_PATH.name}\n", encoding="utf-8")

    with zipfile.ZipFile(ZIP_PATH) as archive:
        archived_files = sorted(archive.namelist())
    if archived_files != included_files:
        missing = sorted(set(included_files) - set(archived_files))
        extra = sorted(set(archived_files) - set(included_files))
        raise RuntimeError(f"archive content mismatch; missing={missing}; extra={extra}")


def main() -> None:
    clean_public_root()
    for relative_path in FILES:
        copy_file(relative_path)
    for relative_path in sorted(set(referenced_assets()) | set(EXTRA_PUBLIC_ASSETS)):
        copy_file(relative_path)

    included_files = sorted(relative_posix(path) for path in PUBLIC_ROOT.rglob("*") if path.is_file())
    write_manifest(included_files)
    problems = verify_package()
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        raise SystemExit(1)

    write_archive(included_files)

    print(f"Deployment package ready: {PUBLIC_ROOT}")
    print(f"Files included: {len(included_files)}")
    print(f"Contents report: {BUILD_ROOT / 'ittemmall-public-contents.txt'}")
    print(f"Upload ZIP: {ZIP_PATH}")
    print(f"SHA256: {SHA256_PATH}")


if __name__ == "__main__":
    main()
