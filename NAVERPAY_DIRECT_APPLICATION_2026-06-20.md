# ITTEMMALL 네이버페이 직접 신청 준비

작성일: 2026-06-20
대상: https://ittemmall.com 본몰만

## 결론

잇템몰은 네이버페이 직접 신청 시 `주문형`을 우선 신청한다.

이유:

- 현재 판매 대상은 배송되는 실물 상품인 MARCE 피클볼 패들이다.
- 네이버페이 공식 소개 기준으로 주문형은 상품 상세 페이지에 `네이버페이 구매하기` 버튼을 노출하고, 주문/배송/클레임/정산까지 네이버페이 주문 프로세스를 이용하는 유형이다.
- 공식 가맹점 가이드 기준으로 주문형은 실물 배송 상품에 맞고, 결제형은 자사몰 주문서의 결제수단으로 네이버페이를 붙이는 방식이며 사이트 운영기간/취급상품 등에 따라 가입 가능 여부 확인이 필요하다.
- 종합형은 주문형 + 결제형이다. 현재 단계에서는 주문형만 먼저 신청하고, 나중에 자사몰 주문서 내 결제수단까지 필요하면 결제형 또는 종합형을 추가 검토한다.

## 공식 자료 기준 유형 구분

- 주문형: 상품 상세 또는 장바구니에 네이버페이 구매하기 버튼을 노출하고 네이버페이 주문서로 주문한다.
- 결제형: 자사몰 주문서 안에서 결제수단 중 하나로 네이버페이를 제공한다.
- 종합형: 상품 상세 구매하기와 자사몰 주문서 결제수단을 모두 제공한다.

공식 확인 링크:

- 네이버페이 간편결제 유형 소개: https://developers.pay.naver.com/introduce/naverpay
- 주문형 소개/가입 및 연동 프로세스: https://developers.pay.naver.com/introduce/order
- 결제형 소개: https://developers.pay.naver.com/introduce/payment
- 주문형 검수 안내: https://developers.pay.naver.com/support/inspection/order
- 결제형 검수 안내: https://developers.pay.naver.com/support/inspection/payment
- 네이버페이 가맹점 가이드: https://mkt.naver.com/naverpay_guide
- 주문형/결제형/종합형 비교 PDF: https://campaign-cdn.pstatic.net/nfs/commonParam/naverpayguide_files/20231110105236_9c2ada1c71577b492247712234236ee3.pdf

## 현재 사이트 점검

통과:

- 운영 URL: https://ittemmall.com
- 상품 상세: 실물 상품명, 가격, 이미지, 옵션, 수량, 상세 정보가 노출된다.
- 주문 흐름: 상품 상세 -> 주문서 -> 결제수단 확인 -> 완료/내역/상세 수정 흐름이 있다.
- 네이버페이 버튼 자리: 상품 상세 하단에 N pay 구매 버튼 자리가 있다.
- 사업자 정보: 상호, 대표자, 사업자등록번호, 통신판매업 신고번호, 주소, 고객센터, 이메일이 공개 페이지와 푸터에 노출된다.
- 정책 페이지: 이용약관, 개인정보처리방침, 배송/교환/환불 안내, 사업자 정보 페이지가 있다.
- 주문 내역: LocalStorage에 주문 내역이 누적되고 새로고침 후에도 남는다.
- 서버 주문 저장 레이어: `payment/order-store.php`와 private JSON 저장소 구조가 있다.
- 키 placeholder: public 설정, private 설정 예시, 승인/취소 API placeholder가 있다.
- 공개 보호: Markdown, private, example, 내부 스크립트는 `.htaccess`와 패키징 규칙으로 공개 제외/차단한다.

오너 게이트:

- 네이버페이 가맹점 신청/승인 전이므로 실제 네이버페이 주문등록/구매하기 SDK는 아직 연결하지 않는다.
- Hostinger 운영 서버의 private 주문 저장소 경로가 아직 설정되지 않았다.
- 네이버페이 주문형 인증값이 아직 발급되지 않았다.
- 실제 발급값은 GitHub와 public web root에 올리지 않는다.

## 네이버페이센터 신청 입력값

- 사이트 URL: `https://ittemmall.com`
- 신청 유형: `주문형`
- 상호: `공간`
- 대표자: `안뜰에해듬`
- 사업자등록번호: `221-31-17043`
- 개업일: `2019-04-11`
- 사업장 주소: `전북특별자치도 익산시 황등면 황금로 73`
- 통신판매업 신고번호: `제2022-전북익산-0083호`
- 이메일: `staysiaofficial@gmail.com`
- 고객센터 전화: `010-2400-3414`
- 판매 상품: `MARCE 스위트 피클볼 패들`
- 상품 유형: `실물 배송 상품`
- 배송비: `무료배송`
- 출고 기준: `결제 확인 후 영업일 기준 2일 이내`
- 반품 주소: `전북특별자치도 익산시 황등면 황금로 73`

## 승인 후 Codex 재개 지점

네이버페이센터에서 아래 값이나 공식 연동 가이드를 받으면 이 프로젝트에서 이어서 작업한다.

- 주문형 계정 ID
- 가맹점 인증키
- 버튼 인증키
- 네이버 공통 인증키
- 주문형 연동 버전 안내: v1.0 또는 v2.1
- 상품정보 XML/주문등록/주문관리 API 세부 명세
- 검수 요청에 필요한 가맹점 ID와 체크리스트

재개 작업:

- 공식 주문형 연동 버전에 맞춰 상품정보 응답과 주문등록 API를 구현한다.
- 상품 상세의 N pay 구매 버튼을 실제 네이버페이 구매하기 SDK로 교체한다.
- 장바구니를 추가해야 하는 경우 장바구니 N pay 버튼/빈 장바구니 비활성 처리를 추가한다.
- `payment/order-store.php`가 저장한 주문번호와 네이버페이 주문번호 매핑을 추가한다.
- 주문관리 API로 발주확인/발송/취소/반품/교환 상태를 동기화한다.
- 검수 체크리스트 기준으로 PC/모바일 버튼, 주문정보, 배송비, backUrl, 유입 스크립트, 오류 상태를 확인한다.

## 로컬/운영 검증 명령

```bash
python3 scripts/check_catalog_consistency.py
python3 scripts/build_deployment_package.py
python3 scripts/deployment_readiness_report.py --allow-owner-tasks
python3 scripts/smoke_test_deployment.py --base-url https://ittemmall.com
python3 scripts/live_deployment_report.py --base-url https://ittemmall.com
```

네이버페이 발급값과 private 주문 저장소 설정까지 끝난 뒤:

```bash
python3 scripts/smoke_test_deployment.py --base-url https://ittemmall.com --require-naver-config --write-test-order
python3 scripts/live_deployment_report.py --base-url https://ittemmall.com --require-naver-config --strict
```
