# ittemmall.com Deploy Notes

Static site root files:

- `index.html`
- `app.js`
- `styles.css`
- `.htaccess`
- `robots.txt`
- `sitemap.xml`
- `assets/images/*`

Primary QA path after deployment:

1. Open `https://ittemmall.com/product/coolfit-wide-headband/50/category/25/display/1/`
2. Confirm product detail loads directly.
3. Select `WHITE`, then `BLACK`.
4. Click `N pay 구매`; confirm no visible navigation.
5. Click `비회원으로 구매하기`.
6. Confirm order summary appears above shipping form.
7. Fill name, phone, email, address, detail address.
8. Check required notice.
9. Click `결제 페이지로 이동하기`.
10. Confirm there is no page movement and no order completion.
11. Confirm `PaymentGatewayClick` is recorded in browser storage/dataLayer.

Hostinger note:

`ittemmall.com` currently resolves to Hostinger parking. The SSH account already configured on this Mac does not list an `ittemmall.com` domain folder, so deployment needs the Hostinger account/server credentials for this specific domain or hPanel file upload.
