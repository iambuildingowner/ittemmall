# ITTEMMALL Toss PG Setup

잇템몰은 Toss PG를 우선 심사 대상으로 둔다. 현재 코드는 실제 키 없이 심사 전 준비 상태로 동작하며, 주문서에는 `토스페이먼츠` 결제수단이 기본 선택된다.

## 준비된 것

- 메인 페이지가 `payment/toss-config.js`를 로드한다.
- 주문서 기본 결제수단이 `토스페이먼츠`로 설정되어 있다.
- 서버 주문 저장소가 `toss_pg` 결제수단을 저장할 수 있다.
- 실제 키는 공개 파일이 아니라 private config 또는 서버 환경변수에 넣는 것을 전제로 한다.

## 오너 게이트

아래 값은 Toss 심사/계약 이후 사용자가 발급받아야 한다.

- 상점아이디/MID
- client key
- secret key
- 결제위젯 variantKey
- 운영 도메인과 성공/실패 URL 등록값
- 같은 사업자 추가 사이트/MID 등록 승인 여부

## 공개 설정 자리

`payment/toss-config.js`에는 브라우저에 공개되어도 되는 값만 둔다.

```js
window.ITTEMMALL_TOSS_PAYMENTS_CONFIG = {
  enabled: false,
  mode: "development",
  clientKey: "",
  customerKeyPrefix: "ittemmall-customer",
  paymentWidgetVariantKey: "DEFAULT",
  successUrl: "https://ittemmall.com/payment/toss-success.html",
  failUrl: "https://ittemmall.com/payment/toss-fail.html",
  orderEndpoint: "https://ittemmall.com/payment/order-store.php",
};
```

`secret key`는 절대 이 파일에 넣지 않는다.

## 다음 구현 지점

1. Toss 심사 신청 전, 잇템몰 사업자정보/정책/상품/주문 흐름을 먼저 완성한다.
2. Toss 계약 후 client key, secret key, MID를 발급받는다.
3. `payment/toss-config.js`의 `enabled`와 client key를 운영값으로 바꾼다.
4. 서버 승인 API를 별도 PHP 엔드포인트로 연결한다.
5. 운영 도메인에서 테스트 결제를 한 뒤 실제 결제 버튼을 활성화한다.

현재 단계에서는 심사 준비와 주문 접수까지만 안전하게 열어둔다.
