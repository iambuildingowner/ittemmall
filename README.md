# Runnerwin Test Store

러닝 액세서리 전환 구조 검증용 정적 SPA입니다. 현재 검증 범위는 헤드밴드 2종과 러닝캡 1종입니다.

## Routes

- Home: hero, brand story, new arrivals, category navigation, race list, footer
- Category/list/search: persisted sort state, loading/empty/error/success states
- Product detail: option selection, quantity preservation, detail sections, sample reviews, shared guide module
- Cart: persisted cart, quantity update, checkout
- Order history/account/board/about/policy: no orphan and no dead-end navigation

## Image Workflow

Original product references are kept only under `output/originals/` for transformation. Production UI must use only transformed assets under `assets/images/` or non-original placeholders until those transformed assets are ready.
