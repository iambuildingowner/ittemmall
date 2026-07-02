# 2026-07-02 테니스 팔찌 아이템 검증 브리프

## 기본 정보

- 기준일: 2026-07-02
- 테스트 키워드: 테니스 팔찌
- 상품 성격: 실물 상품
- 원가 조사 방향 사용자 확인: 실물 상품으로 보고 알리바바/도매 유사 제품 평균 원가 조사 진행 승인
- 작업 단계: 아이템 검증 -> 상품 업로드 -> Meta 광고 검증 후보
- 상품명 초안: 아쿠아글로우 테니스 브레이슬릿
- 상품 slug: `tennis-bracelet`
- 상품 상세 URL: `https://ittemmall.com/tennis-bracelet/`

## 판매가 / 원가 판단

- 판매가 초안: 49,900원
- 허용 광고비: 49,900원 x 20% = 9,980원
- 목표 CPC: 49,900원 x 0.004 = 약 200원
- 원가 기준: 판매가 대비 30% 이하, 즉 14,970원 이하
- 소싱 방향: 925실버 정면 승부보다 5A 지르코니아 + 스테인리스 스틸 베이스 + 실버톤 도금 포지션 우선
- 원가 판단: 알리바바/도매 유사 제품 기준 스테인리스/CZ 테니스 팔찌는 제품 단가가 대략 3~6달러대 구간으로 확인되어, 포장/수입/검수 비용을 더해도 49,900원 판매가에서 원가율 30% 안에 들어올 가능성이 있다.
- 925실버/모이사나이트 제품은 18~40달러 이상 구간이 많아 49,900원 판매가와 맞지 않으므로 이번 잇템몰 테스트 기본 포지션에서는 제외한다.

## 네이버 쇼핑 / 경쟁가 메모

- 네이버 쇼핑 자동 접속은 비정상 접근 제한 화면으로 막혀 전체 상위 10개 카드 원문을 직접 수집하지 못했다.
- 공개 검색 결과와 판매자 페이지 기준으로 저가형 큐빅/패션 팔찌는 1만원대~3만원대, 925실버/브랜드형은 6만원대~10만원대 이상, 랩다이아/파인주얼리는 100만원 이상 구간까지 분리된다.
- 47베이지 테니스 팔찌류는 68,900원대 상품이 확인된다.
- ICEBALL Meta 광고는 10만원대/백화점 명품/최대 50% 할인 소구를 반복 사용한다.
- 잇템몰은 저가 최저가 정면 승부가 아니라 49,900원 선물형 패션 주얼리 포지션으로 테스트한다.

## Meta 광고 라이브러리 메모

- Meta 광고 라이브러리 `테니스팔찌` 검색 결과: 활성 광고 약 62개 확인
- 반복 광고주: ICEBALL.official 중심, 리틀골드, 파이브앤플러스, Cpikofficial 관련 광고도 확인
- 반복 소구:
  - 10만원대 백화점 명품 테니스 팔찌
  - 데일리룩부터 드레스업까지 착용
  - 시계/팔찌와 레이어드
  - 기간 한정 할인, 선물 증정, 당일 발송
  - 5A C-Zirconia, 로듐/도금, 변색 걱정 완화 같은 소재/마감 소구
- 광고 소재 방향:
  - 손목 착용컷 1장 중심
  - 민트 아쿠아 배경의 선물형 무드
  - 이번 광고 이미지는 이미지 안에 글씨를 넣지 않고, Meta 광고 문구/헤드라인에서 키워드와 가격을 처리한다.
- 최종 소재 방식:
  - 사용자가 선택/첨부한 글씨 없는 착용컷과 제품 단독컷 2개로 진행
  - 착용컷 파일: `assets/ittemmall/tennis-bracelet/tennis-bracelet-meta-ad-v2.png`
  - 제품 단독컷 파일: `assets/ittemmall/tennis-bracelet/tennis-bracelet-meta-ad-v3-product.png`

## Meta 광고 세팅 초안

- 비즈니스 계정: 잇템몰 비즈니스 계정
- 캠페인: `잇템몰_아이템검증`
- 광고 세트: `테니스팔찌_KR_F25-54_데일리주얼리_9980`
- 예산: 9,980원. Meta UI 운영 편의상 10,000원으로 반올림 가능하되, 기준 공식은 판매가 49,900원 x 20%.
- 목표 CPC: 약 200원
- 랜딩 URL: `https://ittemmall.com/tennis-bracelet/?utm_source=meta&utm_medium=paid_social&utm_campaign={{campaign.name}}&utm_content={{ad.name}}&utm_term={{adset.name}}`
- 광고명 A: `아쿠아글로우테니스팔찌_착용컷_49900`
- 광고명 B: `아쿠아글로우테니스팔찌_제품컷_49900`
- 광고 이미지 A: `assets/ittemmall/tennis-bracelet/tennis-bracelet-meta-ad-v2.png`
- 광고 이미지 B: `assets/ittemmall/tennis-bracelet/tennis-bracelet-meta-ad-v3-product.png`
- Primary text: `테니스 팔찌를 데일리룩에 부담 없이 더해보세요. 3mm 실버톤 라인과 맑은 지르코니아 반짝임으로 시계 옆 레이어드나 선물용으로 고르기 좋습니다.`
- Headline: `테니스 팔찌 49,900원`
- Description: `3mm 슬림 라인 · 실버톤 · 사이즈 선택`
- CTA: `구매하기` 또는 `더 알아보기`

## 상품 업로드 계획

- 진입점: 홈 상품 카드, 직접 URL `/tennis-bracelet/`, 해시 URL `/#/product/tennis-bracelet`
- CTA: 바로 구매하기 / N pay 구매
- 상품별 픽셀 이벤트:
  - `PurchaseCtaClick_tennis_bracelet`
  - `NpayPurchaseClick_tennis_bracelet`
- 사이즈 영향 여부: 영향 있음
- 사이즈 옵션: 15cm, 16cm, 17cm, 18cm
- 상세페이지 사이즈 구성: 손목둘레 측정 이미지, 손목둘레별 추천 사이즈표, 선물용 기본 사이즈 안내
- 대표 이미지: 착용컷
- 상세 이미지: 제품 단독컷, 잠금/스톤 디테일컷
- 대표 컬러: 고급 민트 아쿠아 계열. 특정 브랜드 로고/상표/포장 오인은 피한다.

## 판단

- 결론: 테스트 게시 후보
- 이유:
  - Meta에서 활성 광고가 다수 확인되어 시장 반응 가능성이 있다.
  - 49,900원 가격이면 테스트 광고비 약 1만원, 목표 CPC 약 200원으로 잇템몰 공식에 맞춰 검증 가능하다.
  - 스테인리스/CZ 소싱 기준이면 원가율 30% 이하 가능성이 있다.
- 리스크:
  - 주얼리는 소재/알레르기/변색 기대치가 민감하므로 925실버처럼 오인될 표현을 쓰면 안 된다.
  - 저가 경쟁이 강해 이미지/선물감/상세 신뢰가 약하면 N pay 클릭이 낮을 수 있다.

## 배포 / 로그 테스트 기록

- GitHub Actions 배포: `Deploy to Hostinger` 성공
- 운영 상품 URL: `https://ittemmall.com/tennis-bracelet/`
- 운영 광고 이미지 URL A: `https://ittemmall.com/assets/ittemmall/tennis-bracelet/tennis-bracelet-meta-ad-v2.png`
- 운영 광고 이미지 URL B: `https://ittemmall.com/assets/ittemmall/tennis-bracelet/tennis-bracelet-meta-ad-v3-product.png`
- 운영 렌더 확인:
  - 상품명 `아쿠아글로우 테니스 브레이슬릿` 노출
  - 가격 `49,900원` 노출
  - 사이즈 선택 가이드와 사이즈표 노출
  - `바로 구매하기` / `N pay 구매` 버튼 노출
  - 테니스 팔찌 이미지 깨짐 없음
  - 공개 화면에 티파니/Tiffany, 테스트 의도 문구 없음
- 운영 로그 테스트 1차:
  - 테스트 ID: `tennis-live-20260702-a01`
  - `PurchaseCtaClick_tennis_bracelet`: `stored:true`, `notification.sent:true`
  - `NpayPurchaseClick_tennis_bracelet`: `stored:true`, `notification.sent:true`
  - 테스트 로그 삭제: 8건 삭제 완료
- 운영 로그 테스트 2차:
  - 테스트 ID: `tennis-live-20260702-a02`
  - `PurchaseCtaClick_tennis_bracelet`: `stored:true`, `notification.sent:true`
  - `NpayPurchaseClick_tennis_bracelet`: `stored:true`, `notification.sent:true`
  - 테스트 로그 삭제: 8건 삭제 완료

## Meta 광고 관리자 실행 기록

- 확인 시각: 2026-07-02 20:21 KST
- 상태: 초안 저장 완료, 실제 게시 보류
- 캠페인: `잇템몰_아이템검증`
- 광고 세트: `테니스팔찌_KR_F25-54_데일리주얼리_9980`
- 광고 세트 설정:
  - 지역: 대한민국
  - 성별: 여성
  - 연령: 25-54
  - 예산: 총 예산 9,980원 기준
- 광고 초안:
  - 광고명: `아쿠아글로우테니스팔찌_착용컷_49900`
  - 현재 Meta UI에서는 단일 광고 안에 사용자 제공 착용컷과 제품 단독컷 2개를 함께 선택한 상태로 저장했다.
  - 선택 미디어:
    - `tennis-bracelet-meta-ad-v3-product.png`
    - `tennis-bracelet-meta-ad-v2.png`
  - Primary text: `테니스 팔찌를 데일리룩에 부담 없이 더해보세요. 3mm 실버톤 라인과 맑은 지르코니아 반짝임으로 시계 옆 레이어드나 선물용으로 고르기 좋습니다.`
  - Headline: `테니스 팔찌 49,900원`
  - Description: `3mm 슬림 라인 · 실버톤 · 사이즈 선택`
  - CTA: `구매하기`
  - 랜딩 URL: `https://ittemmall.com/tennis-bracelet/?utm_source=meta&utm_medium=paid_social&utm_campaign={{campaign.name}}&utm_content={{ad.name}}&utm_term={{adset.name}}`
- 게시 보류 이유:
  - 검토 화면에서 Facebook 페이지가 `Autorator`로 표시된다.
  - 페이지 선택 드롭다운에서 확인 가능한 선택지는 `Autorator`, `MICORE, 미코어`, `staysia_place`였고, `잇템몰` 페이지는 보이지 않았다.
  - 잇템몰 Meta 광고는 `잇템몰 비즈니스 계정/페이지` 기준으로 집행해야 하므로, `Autorator` 상태로는 게시하지 않는다.
- 재개 조건:
  - Meta 광고 관리자에서 `잇템몰` Facebook 페이지 또는 잇템몰 비즈니스 계정 권한이 보이게 만든 뒤, 같은 초안에서 Facebook 페이지를 잇템몰로 변경하고 검토 후 게시한다.
  - 이미지별 성과를 더 엄밀히 나누려면 계정 문제가 해결된 뒤 같은 광고 세트 안에서 착용컷 광고와 제품컷 광고를 별도 광고로 복제해 운영한다.

## 출처

- 네이버 쇼핑 검색 URL: https://search.shopping.naver.com/search/all?query=%ED%85%8C%EB%8B%88%EC%8A%A4%20%ED%8C%94%EC%B0%8C
- Meta 광고 라이브러리 검색 URL: https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=KR&is_targeted_country=false&media_type=all&q=%ED%85%8C%EB%8B%88%EC%8A%A4%ED%8C%94%EC%B0%8C&search_type=keyword_unordered
- 알리바바 검색 URL: https://www.alibaba.com/trade/search?SearchText=cubic+zirconia+tennis+bracelet+3mm
- 47베이지 테니스 팔찌 참고: https://47beige.co.kr/products/bracelet-03
