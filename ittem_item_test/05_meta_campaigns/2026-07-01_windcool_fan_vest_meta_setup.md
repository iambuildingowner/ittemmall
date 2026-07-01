# 2026-07-01 잇템몰 선풍기조끼 Meta 광고 세팅

## 목적

- 상품: 윈드쿨 에어 팬 베스트
- 상품 ID: product-003
- 상품 슬러그: windcool-vest
- 판매가: 48,900원
- 검증 목표: Meta 유입 후 상품 상세 진입과 N pay 버튼 클릭 의향 확인
- 실제 결제: 이번 검증 범위 아님

## 캠페인 구조

- 캠페인명: 잇템몰_아이템검증
- 학습/판단 단위: 광고 세트
- 캠페인 예산 최적화: 사용하지 않음
- 상품별 예산: 광고 세트 예산으로 분리

## 광고 세트

- 광고 세트명: 선풍기조끼_KR_M25-54_야외작업_캠핑낚시_10000
- 예산: 10,000원
- 기간: 24시간 테스트
- 예산 방식: 총액 10,000원. Meta UI에서 총액 예산이 맞지 않으면 일예산 10,000원 + 종료일 24시간으로 설정
- 목적: 트래픽 / 랜딩 페이지 조회
- 전환 최적화: NpayPurchaseClick은 운영 도메인 수신 확인 후 2차 테스트에서 사용
- 지역: 대한민국
- 성별: 남성
- 연령: 25-54
- 관심사 후보: 야외작업, 작업복, 낚시, 캠핑, 등산, 물류/배송, 건설 현장

## 광고

- 광고명: 윈드쿨팬베스트_착용컷_폭염소구
- 이미지: assets/ittemmall/fan-vest/windcool-vest-hero.jpg
- 랜딩 URL: https://ittemmall.com/?utm_source=meta&utm_medium=paid_social&utm_campaign={{campaign.name}}&utm_content={{ad.name}}&utm_term={{adset.name}}#/product/windcool-vest
- Primary text: 한여름 야외작업, 낚시, 캠핑 전에 준비하세요. 조끼 안쪽 공기 흐름을 도와주는 듀얼 팬 베스트. 보조배터리 연결 방식으로 필요한 용량을 직접 선택할 수 있습니다.
- Headline: 여름 야외활동용 팬 베스트
- Description: 듀얼 팬 · 메쉬 원단 · 다중 포켓
- CTA: 더 알아보기

## 게시 상태

- 상태: 로컬 검증 완료, 라이브 배포 대기
- 로컬 검증:
  - 가격 48,900원 표시 확인
  - 79,000원 / 99,000원 / 20% 할인 미노출 확인
  - 이미지 4개 로딩 확인
  - NpayPurchaseClick 이벤트 value 48900 확인
  - Meta UTM attribution 저장 확인
- 라이브 URL 확인 필요: https://ittemmall.com/?codex_test=1#/product/windcool-vest
- 게시 전 필수 확인:
  - 라이브 상세에서 48,900원 표시
  - 79,000원 / 99,000원 / 20% 할인 미노출
  - 이미지 4개 로딩
  - N pay 버튼 표시
  - NpayPurchaseClick 이벤트에 value 48900 기록
  - track.php 운영 서버 수신 확인

## 판단 기준

- CTR, CPC, 랜딩 조회, N pay 클릭 수를 함께 본다.
- 10,000원 소진 후 N pay 클릭이 0이면 가격, 상세 첫 화면, 소재 중 병목을 재점검한다.
- 클릭은 있는데 N pay 클릭이 없으면 상세페이지 첫 화면과 CTA를 먼저 수정한다.
