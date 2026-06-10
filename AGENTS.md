# AGENTS.md - 잇템몰

## Scope

PROJECT_SCOPE=Ittemmall

이 폴더는 `ittemmall.com` 상위 쇼핑몰 프로젝트 범위다. `ittemmall.com/marce`와 `marcesports.com` 작업은 각각 `잇템몰 마르세`, `마르세 스포츠` 폴더에서 진행한다.

## First Line Rule

모든 구현 응답은 먼저 한 줄로 `TRIGGER=ON` 또는 `TRIGGER=OFF`를 선언한다.

- `TRIGGER=ON`: 저장, 제출, 추가, 삭제, 결제, 주문, 문의, 리스트, 히스토리, 새 라우트, 모달 플로우, 화면 왕복, 상태 복원이 필요한 기능 단위.
- `TRIGGER=OFF`: 버튼, 박스, 카드, 레이아웃, 스타일, 마크업 수정 같은 단순 UI 조각.

프로젝트 범위가 불분명하면 딱 한 번만 묻는다:

`어느 프로젝트 범위로 진행할까요? 잇템몰 / 잇템몰 마르세 / 마르세 스포츠`

## TRIGGER=ON Definition of Done

- Orphan 금지: 새 화면/라우트는 최소 1개 진입점과 최소 2개 출구를 가진다. 출구는 `Resume/Back to origin`과 `Next/Related action CTA`를 포함한다.
- Dead-end 금지: 완료, 빈상태, 에러 상태에도 의미 있는 다음 행동 CTA를 최소 2개 제공한다.
- State Preservation & Restoration: 폼 입력, 선택값, 스크롤, 필터, 정렬, origin을 저장하고 복귀 시 복구한다.
- 기능은 세트로 완성한다: Create/List/History/Detail/Edit/Return 흐름을 같이 본다.
- 데이터 없는 스텁 금지: 리스트/내역은 loading, empty, error, success 4상태와 persistence를 구현한다.
- 백엔드가 없으면 Mock API와 LocalStorage/IndexedDB를 쓰되 Repository/Service 레이어를 분리한다.

## TRIGGER=OFF Quality Bar

- 접근성, 반응형, disabled/error/focus/hover 상태를 챙긴다.
- 기존 디자인/컴포넌트 스타일을 우선한다.
- 단순 UI 작업에 Graph UX 절대조건을 과대 적용하지 않는다.

## Web Operations Guardrails

- 운영 URL, 라우트, 파일명, 폴더명을 임의로 바꾸지 않는다.
- SEO 필수 요소를 이유 없이 삭제하지 않는다: title, meta description, canonical, robots/noindex, H1/H2, image alt, 의미 있는 링크 텍스트, 404 링크, 모바일 렌더링.
- 광고/분석/전환 추적 코드는 운영 자산으로 본다. 이벤트명이나 `track.php`류 파일을 변경할 때 전환 측정 영향을 설명한다.
- 문의, 결제, 주문, 회원가입, 파일 업로드, 예약, 상담 신청 등 매출 연결 폼은 실제 흐름을 확인한다.
- 로컬, GitHub, 운영 서버를 구분해서 보고한다.
- 완료 전 실제 사용자 화면 기준으로 확인한다. 확인 못 한 범위는 확인했다고 말하지 않는다.

## Ittemmall-Specific Rules

- 이 프로젝트는 상위 몰이다. 마르세 전용 페이지를 기본 포함으로 보지 않는다.
- 공유 결제, 공유 추적, 공통 상품/회원/주문 구조를 바꿀 때 하위 브랜드 페이지 영향까지 점검한다.
- 사용자가 단순히 "잇템몰"이라고 말하면 `ittemmall.com/marce` 작업으로 넘겨짚지 않는다.
- 현재 이 폴더에는 마르세 스포츠 구조를 잇템몰 대표몰/PG 심사 허브 기준으로 리브랜딩한 소스가 들어와 있다. 이후 잇템몰 작업은 이 폴더를 기준으로 진행한다.

## Owner-Gated Delivery

계정 인증, 사업자 정보, API 키, 결제사 심사, 개인정보, 카드/통장/세금 정보가 필요한 일은 Codex가 할 수 있는 화면, 코드, 설정 자리, 검증 방법을 먼저 끝낸다. 사용자가 해야 할 게이트는 따로 명확히 말한다.

## Tool Honesty

- Codex 내부 `image_gen` 도구로 이미지를 만들었으면 그렇게 말한다.
- 덕테이프를 실제로 쓰지 않았으면 덕테이프로 했다고 말하지 않는다.
- 라이브 배포, GitHub 반영, 외부 업로드, 메일 전송은 실제 수행한 경우에만 완료로 말한다.
