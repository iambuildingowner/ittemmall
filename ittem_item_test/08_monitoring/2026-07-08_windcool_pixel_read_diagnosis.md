# 2026-07-08 윈드쿨 선풍기 조끼 구매의사 픽셀 조회 진단

## 결론

- `N pay 구매` 버튼 클릭 픽셀은 정상 생성된다.
- 운영 서버 `track.php`도 `NpayPurchaseClick_windcool_vest`를 정상 저장한다.
- 테스트 로그 삭제도 정상 동작한다.
- 기존 감시에서 `Read paths: MISS:0`을 구매의사 0건처럼 해석한 것은 잘못이다.
- `MISS:0`은 "클릭 없음"이 아니라 "감시 워크플로우가 서버 로그 파일 위치를 못 찾음"으로 봐야 한다.

## 테스트 기록

- 테스트 ID: `windcool-live-pixel-proof-20260708-072346`
- 직접 서버 저장 테스트:
  - 이벤트: `NpayPurchaseClick_windcool_vest`
  - 응답: `stored:true`
  - 삭제: `removed:1`
  - 삭제 이벤트: `NpayPurchaseClick_windcool_vest: 1`

- 테스트 ID: `windcool-live-button-proof-20260708-072510`
- 실제 버튼 클릭 테스트:
  - URL: `https://ittemmall.com/?pixel_test=1&test_run_id=windcool-live-button-proof-20260708-072510#/product/windcool-vest`
  - 프론트 이벤트: `ViewContent`, `NpayPurchaseClick`, `NpayPurchaseClick_windcool_vest`, `CheckoutPageView`
  - 상품: `windcool-vest`
  - 금액: `59,900`
  - 테스트 삭제: `removed:4`
  - 삭제 이벤트: `CheckoutPageView: 1`, `NpayPurchaseClick: 1`, `NpayPurchaseClick_windcool_vest: 1`, `ViewContent: 1`

## 조치

- `read-server-tracking.yml`에서 서버 로그 경로를 못 찾으면 `LOG_PATH_NOT_FOUND`로 표시하게 변경한다.
- 이 상태에서는 구매의사 클릭을 0건으로 해석하지 않는다.
- `payment/tracking-report.php`를 배포 패키지에 포함해, 추후 관리자 토큰이 설정되면 서버가 직접 공식 로그를 읽는 방식으로 전환할 수 있게 한다.

