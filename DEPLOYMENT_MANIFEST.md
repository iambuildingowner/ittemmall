# 잇템몰 배포 매니페스트

잇템몰은 기존 사업자의 대표 쇼핑몰 및 PG 심사용 허브다. 공개 웹루트에는 고객이 보는 화면과 결제 준비용 public 파일만 업로드하고, 실제 사업자정보/비밀키/주문 데이터는 private 영역에 둔다.

## 공개 포함

- `index.html`
- `404.html`
- `robots.txt`
- `sitemap.xml`
- `track.php`
- `assets/ittemmall/`
- `legal/business.html`
- `legal/terms.html`
- `legal/privacy.html`
- `legal/refund.html`
- `payment/toss-config.js`
- `payment/naverpay-config.js`
- `payment/healthcheck.php`
- `payment/ops.html`
- `payment/order-store.php`
- `payment/order-store-lib.php`
- `payment/rate-limit-lib.php`
- `payment/order-lookup.html`
- `payment/order-lookup.php`
- `payment/notification-test.php`
- `payment/admin.html`
- `payment/admin-orders.php`
- `payment/naverpay-approve.php` (비활성 레거시 엔드포인트, 고객 화면 진입 없음)
- `payment/naverpay-cancel.php` (비활성 레거시 엔드포인트, 고객 화면 진입 없음)

## 공개 제외

- `ITTEMMALL_LAUNCH_OWNER_CHECKLIST.md`
- `ITTEMMALL_PG_REBRAND_WORKPLAN_2026-06-10.md`
- `payment/TOSS_SETUP.md`
- `payment/NAVERPAY_SETUP.md`
- `private/ittemmall-server-config.example.php`
- `private/ittemmall-production-release.example.json`
- `private/ittemmall-production-release.production.json`
- `build/ittemmall-private/`
- 실제 주문/고객/로그 JSON 또는 JSONL 파일
- API key, secret, token, credentials

## 준비 명령

1. 카탈로그 확인:
   `python3 scripts/check_catalog_consistency.py`
2. 공개 패키지 생성:
   `python3 scripts/build_deployment_package.py`
3. readiness 확인:
   `python3 scripts/deployment_readiness_report.py`
4. 운영 서버 smoke test:
   `python3 scripts/smoke_test_deployment.py --base-url https://ittemmall.com`
5. 운영 서버 live report:
   `python3 scripts/live_deployment_report.py --base-url https://ittemmall.com`

## 오너 입력 후 production release

1. `ITTEMMALL_LAUNCH_OWNER_CHECKLIST.md`를 기준으로 사업자/배송/환불/Toss PG 값을 수집한다.
2. `private/ittemmall-production-release.example.json`을 `private/ittemmall-production-release.production.json`으로 복사한다.
3. 실제 값을 넣은 뒤 먼저 검증한다:
   `python3 scripts/prepare_production_release.py --config private/ittemmall-production-release.production.json --validate-only`
4. 값이 맞으면 release를 실행한다:
   `python3 scripts/prepare_production_release.py --config private/ittemmall-production-release.production.json`
5. 기본값은 `release-backups`에 원본 백업과 manifest를 남긴다.
6. 백업이 필요 없는 별도 상황에서만 `--no-backup`을 쓴다.

## private config

`scripts/generate_private_config.py`로 `build/ittemmall-private/ittemmall-server-config.php`를 만들고, 운영 서버 public web root 밖에 업로드한다.

필수 private 값:

- `ITTEMMALL_ORDER_STORE_PATH`
- `ITTEMMALL_RATE_LIMIT_PATH`
- `ITTEMMALL_ADMIN_TOKEN`
- `TOSS_PAYMENTS_SECRET_KEY`

추적 로그는 `ITTEMMALL_TRACK_LOG_PATH`와 `ITTEMMALL_TRACK_SALT`가 있으면 해당 값을 쓰고, 없으면 public web root 밖 기본 private 폴더 `../ittemmall-private/data/pixel-events/{KST-date}.ndjson`에 저장한다.

Toss 실제 결제는 운영 검증 전까지 `TOSS_PAYMENTS_APPROVE_ENABLED=0`과 `payment/toss-config.js`의 `enabled=false`를 유지한다.

네이버페이 신청/연동은 잇템몰 본몰 범위가 아니며, 마르세 스포츠 프로젝트에서 별도로 진행한다.

## 완료 기준

- 공개 패키지에 private/example/internal 문서가 포함되지 않는다.
- `payment/healthcheck.php`에서 주문 저장소, rate-limit, public/private 설정 일치 여부를 확인한다.
- `payment/ops.html`에서 운영 체크 상태를 확인한다.
- 메인, 주문서, 주문내역, 주문조회, 관리자, 정책 페이지가 운영 URL에서 로드된다.
