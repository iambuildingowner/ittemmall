# ittemmall.com Deploy Notes

잇템몰은 기존 사업자 `공간`의 대표 쇼핑몰이자 통신판매업/PG 심사용 허브로 운영한다. 공개 웹루트에는 `build/ittemmall-public/` 안의 파일만 업로드한다.

## Current Upload Package

- Public folder: `build/ittemmall-public/`
- Upload ZIP: `build/ittemmall-public.zip`
- Product: MARCE 스위트 피클볼 패들 2종
- Business info: 공간 / 안뜰에해듬 / 221-31-17043
- Domain: `https://ittemmall.com`

## Primary QA Path After Deployment

1. Open `https://ittemmall.com/`.
2. Confirm the header and footer show `ITTEMMALL`.
3. Confirm the MARCE pink and black products are visible.
4. Open product detail and confirm product images load.
5. Open the order form and confirm address, contact, agreement, and payment method fields render.
6. Open `https://ittemmall.com/legal/business.html`.
7. Confirm business info shows `공간`, `안뜰에해듬`, `221-31-17043`, and the business address.
8. Open `https://ittemmall.com/legal/refund.html`.
9. Confirm shipping/refund policy no longer has `ITTEMMALL_OWNER_TODO`.
10. Confirm mobile layout, images, and console are clean.

## Deployment Gate

The SSH account previously configured on this Mac does not list an `ittemmall.com` domain folder. Live deployment needs the Hostinger account/server credentials for this specific domain, or hPanel file upload access.

Do not mark production deployment complete until the live URL is verified after upload.
