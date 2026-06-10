# 잇템몰

`ittemmall.com` 상위 쇼핑몰 프로젝트입니다. 현재 작업 방향은 완성도가 높은 `마르세 스포츠` 구조를 잇템몰 기준으로 리브랜딩해, 기존 사업자의 통신판매업 신고 및 Toss PG/네이버페이 심사용 대표몰로 쓰는 것입니다.

## Current Structure

- Home: 상품 탐색, 옵션 선택, 주문 흐름, 정책/사업자정보 진입
- Payment: 주문 저장, Toss PG 우선 심사 placeholder, 네이버페이 준비, 관리자 주문 확인, 결제 상태 복귀
- Legal: 사업자정보, 이용약관, 개인정보처리방침, 배송/교환/환불 정책
- Deployment scripts: 공개 패키지 생성, private config 생성, smoke/live readiness 점검

## Owner Gate

사업자정보, 통신판매업 신고번호, Toss PG 키/MID, 네이버페이 키, 관리자 토큰, private server path는 실제 값 없이 placeholder로만 둡니다. 실제 심사 신청/키 발급 후 값만 주입하면 재검증할 수 있게 준비합니다.
