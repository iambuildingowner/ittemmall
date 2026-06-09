# 잇템몰

`ittemmall.com` 상위 쇼핑몰 프로젝트입니다. 현재 검증 범위는 러닝 액세서리 상품군과 전환 구조입니다.

## Routes

- Home: hero, brand story, new arrivals, category navigation, race list, footer
- Category/list/search: persisted sort state, loading/empty/error/success states
- Product detail: option selection, quantity preservation, detail sections, sample reviews, shared guide module
- Cart: persisted cart, quantity update, checkout
- Order history/account/board/about/policy: no orphan and no dead-end navigation

## Image Workflow

Original product references are kept only under `output/originals/` for transformation. Production UI must use only transformed assets under `assets/images/` or non-original placeholders until those transformed assets are ready.
