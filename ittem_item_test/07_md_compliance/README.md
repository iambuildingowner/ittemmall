# 잇템몰 MD 준수 검토 체계

목적: 잇템몰 아이템 작업이 끝났다고 보고하기 전에, 기존 MD 기준을 실제 산출물이 지켰는지 확인한다.

## 기본 흐름

1. 작업 대상 상품의 브리프와 상세페이지 템플릿을 확인한다.
2. 자동 검토 가능한 항목은 `scripts/check_ittemmall_md_compliance.py`로 확인한다.
3. 이미지 품질처럼 자동 확인이 어려운 항목은 수동 검토 항목으로 남긴다.
4. 실패 항목이 있으면 완료 보고 전에 먼저 고친다.
5. 검토 결과는 이 폴더에 날짜별 MD로 남긴다.

## 자동 검토 대상

- 상품 가격과 할인 표기
- 사이즈 영향 상품의 사이즈 옵션, 사이즈 설명 이미지, 사이즈표
- 상품 정보 중복 표시 방지 설정
- N pay 버튼 추적 기본 문구
- 상품별 N pay 이벤트명 `NpayPurchaseClick_{상품slug}`
- 광고 이미지 파일 존재와 정사각형 여부

## 수동 검토 대상

- 운영 URL에서 N pay 테스트 클릭이 서버 로그에 `stored:true`로 저장되는지
- 같은 `test_run_id` 테스트 로그를 삭제했을 때 삭제 건수가 1건 이상인지
- 테스트 클릭/삭제를 2회 반복했을 때 두 번 모두 성공하는지
- 광고 이미지가 참고 이미지 1개의 구도/톤/정보량 기준을 지켰는지
- 한 장 안에 두 컷/두 명/두 장면처럼 보이지 않는지
- 카피와 가격이 정확하고 자연스러운지
- AI 느낌이 강하거나 배경이 가짜처럼 보이지 않는지
- 상세페이지에서 사용 설명과 상품 정보가 반복되지 않는지

## 실행 예시

```bash
python3 scripts/check_ittemmall_md_compliance.py \
  --product windcool-vest \
  --size-sensitive \
  --ad-image assets/ittemmall/fan-vest/windcool-vest-meta-ad-generated-v6.png \
  --write-report ittem_item_test/07_md_compliance/2026-07-02_windcool_fan_vest_review.md
```
