# ITTEMMALL Naver Pay Setup

Use `ITTEMMALL_LAUNCH_OWNER_CHECKLIST.md` first when collecting the owner-provided Naver Pay, business, shipping, privacy, and private server values. This setup file explains the technical pieces after those values are available.

Toss PG is the first payment review target for Ittemmall. Use `payment/TOSS_SETUP.md` for the Toss owner gate and keep this document as the Naver Pay follow-up setup guide.

## What is already prepared

- Deployment manifest: `DEPLOYMENT_MANIFEST.md`
- Frontend config example: `payment/naverpay-config.example.js`
- Frontend runtime config file: `payment/naverpay-config.js`
- Public Naver Pay config generator: `scripts/generate_public_naverpay_config.py`
- Return page: `payment/return.html`
- Runtime healthcheck: `payment/healthcheck.php`
- Visual operations readiness page: `payment/ops.html`
- Protected email notification test endpoint: `payment/notification-test.php`
- Protected admin order dashboard: `payment/admin.html`
- Protected admin order API: `payment/admin-orders.php`
- Customer order lookup page/API: `payment/order-lookup.html`, `payment/order-lookup.php`
- Server order store endpoint: `payment/order-store.php`
- Server order store library: `payment/order-store-lib.php`
- Private server config loader: `payment/server-config-lib.php`
- Private server config example: `private/ittemmall-server-config.example.php`
- Catalog consistency guard: `scripts/check_catalog_consistency.py`
- Server approval endpoint, disabled until merchant settings are ready: `payment/naverpay-approve.php`
- Server cancel endpoint, admin protected and disabled until merchant settings are ready: `payment/naverpay-cancel.php`
- Server approval endpoint template backup: `payment/naverpay-approve.example.php`
- Frontend payment flow stores an order locally and tries to sync the order to the server before opening Naver Pay.
- Admin dashboard can search orders, inspect details, update fulfillment status/admin memo, export the visible list to CSV, and request Naver Pay cancellation for approved Naver Pay orders.
- Server order notifications can be sent by PHP mail when `ITTEMMALL_NOTIFY_ENABLED=1` and `ITTEMMALL_NOTIFY_EMAIL` are configured.
- Public business, terms, privacy, and refund policy pages are prepared under `legal/`.
- `index.html` loads `payment/naverpay-config.js` before the app starts.
- Root `.htaccess` blocks internal research folders, output artifacts, Markdown, spreadsheets, PDFs, and example files from public access.
- If public keys are missing, the page shows a safe pending/error state instead of pretending payment is complete.
- The approval endpoint contains the official one-time payment approval URL shape:
  `https://{API domain}/naverpay-partner/naverpay/payments/v2.2/apply/payment`.
- It sends `paymentId` as `application/x-www-form-urlencoded` with the required Naver Pay headers and a 60 second timeout.
- The approval endpoint now reads the expected order from the server order store and compares `merchantPayKey` and `totalPayAmount`.
- If Naver Pay gives a merchant-specific approval URL during review, set `NAVER_PAY_APPROVE_URL` in private server config to override the default endpoint.
- If Naver Pay gives a merchant-specific cancel URL during review, set `NAVER_PAY_CANCEL_URL` in private server config to override the default endpoint.
- Live approval is intentionally blocked until merchant keys and `NAVER_PAY_APPROVE_ENABLED=1` are set.
- Live cancellation is intentionally blocked until merchant keys, admin token, and `NAVER_PAY_CANCEL_ENABLED=1` are set.

## What the owner must do

1. Complete Naver Pay merchant onboarding.
2. Get `clientId`, `chainId`, and `clientSecret`.
3. Put `clientId` and `chainId` into `payment/naverpay-config.js` with `scripts/generate_public_naverpay_config.py`.
4. Put `clientSecret` only in server environment variables or a private config file outside the public web root.
5. Set `ITTEMMALL_ORDER_STORE_PATH` to a JSON file path outside the public web folder.
6. Replace `ITTEMMALL_OWNER_TODO_*` values in `legal/*.html` with actual business, privacy, shipping, and refund information.
7. Open `https://ittemmall.com/payment/healthcheck.php` and confirm PHP/cURL/order-store settings are ready.
8. Confirm `payment/order-store.php` can save a test order on the production PHP server.
9. Set `NAVER_PAY_APPROVE_ENABLED=1` only after the order store, policy pages, and merchant keys are confirmed.

## Required environment variables

```bash
ITTEMMALL_SERVER_CONFIG_PATH=/absolute/private/path/ittemmall-server-config.php
ITTEMMALL_ORDER_STORE_PATH=/absolute/private/path/ittemmall-orders.json
ITTEMMALL_TRACK_LOG_PATH=/absolute/private/path/ittemmall-track-events.jsonl
ITTEMMALL_RATE_LIMIT_PATH=
ITTEMMALL_TRACK_SALT=random-long-string-for-ip-hash
ITTEMMALL_ADMIN_TOKEN=random-long-admin-token
ITTEMMALL_SITE_BASE_URL=https://ittemmall.com
ITTEMMALL_NOTIFY_ENABLED=0
ITTEMMALL_NOTIFY_EMAIL=orders@ittemmall.com
ITTEMMALL_NOTIFY_FROM=no-reply@ittemmall.com
NAVER_PAY_CLIENT_ID=...
NAVER_PAY_CHAIN_ID=...
NAVER_PAY_CLIENT_SECRET=...
NAVER_PAY_MODE=development
NAVER_PAY_APPROVE_URL=
NAVER_PAY_APPROVE_ENABLED=0
NAVER_PAY_CANCEL_URL=
NAVER_PAY_CANCEL_ENABLED=0
```

Never commit the real `NAVER_PAY_CLIENT_SECRET`.
Never put `ITTEMMALL_ORDER_STORE_PATH` inside `public_html`, `www`, `htdocs`, or this public site folder.
The order store uses a `.lock` file to avoid concurrent write loss and writes a `.bak` copy before replacing the JSON file. Keep those files in the same private directory and out of the public web root.
Order creation, Naver Pay approval, and tracking POST requests use a private JSON rate-limit file. Leave `ITTEMMALL_RATE_LIMIT_PATH` empty to derive it from `ITTEMMALL_ORDER_STORE_PATH`, or set it to a private absolute path outside `public_html`, `www`, or `htdocs`.
After a Naver Pay order reaches approved, canceled, or cancel-pending state, the server keeps its product, quantity, and amount immutable against later client resubmits. The approval endpoint also checks that the stored order is a Naver Pay order in `payment_ready/ready` state before calling Naver Pay.
If `ITTEMMALL_TRACK_LOG_PATH` is omitted, `track.php` writes tracking logs to the default private sibling folder outside the public web root: `../ittemmall-private/data/pixel-events/{KST-date}.ndjson`.
Test events must include a `testRunId`, and cleanup must remove those `__test=true` rows before reporting the test complete.
If hosting cannot set environment variables, copy `private/ittemmall-server-config.example.php` to a private non-public path and set `ITTEMMALL_SERVER_CONFIG_PATH`. If that env var is also unavailable, place the real config at the default sibling path `../ittemmall-private/ittemmall-server-config.php` relative to the public web root.

You can generate a private config file skeleton with random `ITTEMMALL_TRACK_SALT` and `ITTEMMALL_ADMIN_TOKEN`:

```bash
python3 scripts/generate_private_config.py \
  --output build/ittemmall-private/ittemmall-server-config.php \
  --order-store-path /absolute/private/path/ittemmall-orders.json \
  --track-log-path /absolute/private/path/ittemmall-track-events.jsonl \
  --rate-limit-path /absolute/private/path/ittemmall-rate-limit.json \
  --notify-email orders@ittemmall.com \
  --naver-client-id YOUR_CLIENT_ID \
  --naver-chain-id YOUR_CHAIN_ID \
  --naver-client-secret YOUR_CLIENT_SECRET
```

Upload that generated `ittemmall-server-config.php` only to a private folder outside the public web root.
Add `--enable-notify` only after the hosting PHP `mail()` function has been verified in `payment/healthcheck.php`.

After Naver Pay keys and actual business/shipping information are available, the full production preparation can be run from one private JSON config:

```bash
cp private/ittemmall-production-release.example.json private/ittemmall-production-release.production.json
python3 scripts/prepare_production_release.py --config private/ittemmall-production-release.production.json
```

Copy the example JSON to a private working file before entering real secrets. The release command refuses obvious example values before writing files, then fills legal pages, writes `payment/naverpay-config.js`, creates `build/ittemmall-private/ittemmall-server-config.php`, rebuilds `build/ittemmall-public.zip`, and runs readiness.
It also backs up the original `legal/*.html` and `payment/naverpay-config.js` to `build/release-backups/ittemmall-release-*/manifest.json` before writing production values. Do not upload `build/release-backups/`.

To check the copied JSON before writing files:

```bash
python3 scripts/prepare_production_release.py --config private/ittemmall-production-release.production.json --validate-only
```

Generate the public JavaScript config after Naver Pay issues `clientId` and `chainId`:

```bash
python3 scripts/generate_public_naverpay_config.py \
  --client-id YOUR_CLIENT_ID \
  --chain-id YOUR_CHAIN_ID \
  --mode production \
  --output payment/naverpay-config.js
```

Do not pass `clientSecret` to the public JavaScript generator. It intentionally accepts only public Naver Pay fields.

Generate legal policy pages with actual owner information before production review:

```bash
python3 scripts/fill_legal_owner_info.py \
  --representative "대표자명" \
  --business-registration-number "000-00-00000" \
  --ecommerce-license "제0000-지역-0000호" \
  --business-address "사업장 주소" \
  --privacy-officer "개인정보 책임자명" \
  --shipping-carrier "택배사명" \
  --shipping-fee "3,000원" \
  --shipping-days "2" \
  --return-address "반품 주소"
```

Review `build/ittemmall-legal-preview/` first. Re-run the command with `--apply-to-source` only after the values are confirmed.

## Official flow reference

- Payment window SDK: https://docs.pay.naver.com/docs/onetime-payment/payment/payment-auth-window
- One-time payment approval: https://docs.pay.naver.com/docs/onetime-payment/payment/apply
- One-time payment cancel: https://docs.pay.naver.com/docs/onetime-payment/payment/cancel
- API URL format: https://docs.pay.naver.com/docs/common/url-format
- The payment window returns `paymentId` to `returnUrl` after the user finishes authentication.
- The server must call the approval API with `Client ID`, `Client Secret`, and `Chain ID` headers.
- Naver Pay documents the development API domain as `dev-pay.paygate.naver.com` and production as `pay.paygate.naver.com`.
- Naver Pay says approval can take time, so the approval request timeout should be 60 seconds.
- Naver Pay says cancellation can take time, so the cancel request timeout should also be 60 seconds or more.
- Naver Pay also provides independent-mall onboarding/checklist material. If your issued guide contains a partner-specific approval URL, use `NAVER_PAY_APPROVE_URL` rather than editing PHP code.

## Production smoke test

After setting `ITTEMMALL_ORDER_STORE_PATH`, open the site and submit a Naver Pay order form. The payment page should show both:

- `SDK 설정 확인 완료` after public Naver Pay config is added.
- `서버 주문 저장 완료` after `order-store.php` writes the order.

Only then should the Naver Pay window be allowed to open.

`payment/healthcheck.php` should report:

- `php.curl: true`
- `serverConfig.privateConfigFileLoaded: true` if using a private config file
- `serverOrderStore.configured: true`
- `serverOrderStore.directoryWritable: true`
- `serverOrderStore.fileValidJson: true` if the order JSON already exists
- `serverOrderStore.backupValidJson: true` if a `.bak` backup already exists
- `serverOrderStore.lockWritable: true`
- `rateLimit.configured: true`
- `rateLimit.directoryWritable: true`
- `rateLimit.lockWritable: true`
- `rateLimit.fileValidJson: true` if the rate-limit JSON already exists
- `naverPay.clientIdConfigured: true`
- `naverPay.clientSecretConfigured: true`
- `naverPay.chainIdConfigured: true`
- `publicNaverPay.clientIdConfigured: true`
- `publicNaverPay.chainIdConfigured: true`
- `publicNaverPay.modeMatchesServer: true`
- `publicNaverPay.clientIdMatchesServer: true`
- `publicNaverPay.chainIdMatchesServer: true`
- `publicNaverPay.clientSecretExposed: false`
- `naverPay.approveUrlLooksHttps: true`
- `naverPay.cancelUrlLooksHttps: true`
- `admin.adminTokenConfigured: true`
- `notification.mailFunctionAvailable: true` if order email alerts will be used
- `readiness.readyToEnableNaverPayApproval: true`
- `readiness.readyForOrderOperations: true`

Also confirm these public policy pages load and no longer contain `ITTEMMALL_OWNER_TODO`:

- `https://ittemmall.com/legal/business.html`
- `https://ittemmall.com/legal/terms.html`
- `https://ittemmall.com/legal/privacy.html`
- `https://ittemmall.com/legal/refund.html`

Protected order lookup example:

```bash
curl -H "X-Ittemmall-Admin-Token: YOUR_ADMIN_TOKEN" https://ittemmall.com/payment/admin-orders.php
```

Browser admin dashboard:

```text
https://ittemmall.com/payment/admin.html
```

The admin detail panel can update fulfillment status, admin memo, shipment carrier, tracking number, tracking URL, and shipment memo. Those fields are saved in the private order JSON and included in CSV export.
If the tracking URL field is left empty, the server automatically generates an HTTPS tracking URL for known carriers: CJ대한통운, 우체국/EMS, 롯데택배, 한진택배, and 로젠택배. A manually entered tracking URL always takes priority.

Customer order lookup:

```text
https://ittemmall.com/payment/order-lookup.html
```

The lookup requires order number plus the original email or phone number. The public response excludes customer name, phone, email, and address, and only returns product, payment status, fulfillment status, and shipment tracking fields.

Visual operations readiness page:

```text
https://ittemmall.com/payment/ops.html
```

This page checks both server readiness from `payment/healthcheck.php` and public launch items such as `payment/naverpay-config.js`, policy page owner placeholders, `robots.txt`, and `sitemap.xml`.

If order email notifications will be used, set `ITTEMMALL_NOTIFY_ENABLED=1`, confirm `ITTEMMALL_NOTIFY_EMAIL` and `ITTEMMALL_NOTIFY_FROM`, then use the protected test button on `payment/ops.html`. The test requires `ITTEMMALL_ADMIN_TOKEN`.

Recommended admin fulfillment statuses:

- `신규`
- `연락 완료`
- `수동 입금 확인`
- `발송 준비`
- `발송 완료`
- `처리 완료`
- `종결`

The current admin Naver Pay cancel button is full-cancel only. Keep `NAVER_PAY_CANCEL_ENABLED=0` until a real approved test order, refund policy, and full-cancel operation are verified. Add a separate partial-cancel UI/policy before sending smaller cancel amounts.

Run the deployment smoke test:

```bash
python3 scripts/smoke_test_deployment.py --base-url https://ittemmall.com
```

Create a human-readable live deployment report:

```bash
python3 scripts/live_deployment_report.py --base-url https://ittemmall.com
```

After Naver Pay production keys are configured, run it in strict mode:

```bash
python3 scripts/live_deployment_report.py --base-url https://ittemmall.com --require-naver-config --strict
```

Run the local readiness report before upload:

```bash
python3 scripts/deployment_readiness_report.py
```

This readiness report also verifies that the customer-facing product names/prices in `index.html` match the server-side order catalog in `payment/order-store-lib.php`. To run only that guard:

```bash
python3 scripts/check_catalog_consistency.py
```

`FAIL` means the package or code setup needs fixing before upload. `OWNER` means the remaining item needs issued Naver Pay keys, private hosting configuration, or a production server action.

After all Naver Pay keys are configured, run the stricter check:

```bash
python3 scripts/smoke_test_deployment.py --base-url https://ittemmall.com --require-naver-config --write-test-order
```

If `ITTEMMALL_ADMIN_TOKEN` is configured and you want to verify admin status updates too:

```bash
python3 scripts/smoke_test_deployment.py --base-url https://ittemmall.com --write-test-order --admin-token YOUR_ADMIN_TOKEN
```

Enable `NAVER_PAY_CANCEL_ENABLED=1` only after a real approved test order exists and the Naver Pay merchant console cancellation policy is confirmed.

## Upload package

Generate the clean upload folder and ZIP:

```bash
python3 scripts/build_deployment_package.py
```

Upload either `build/ittemmall-public/` contents or `build/ittemmall-public.zip`. The ZIP extracts directly into the public web root.
