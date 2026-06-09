# 잇츠몰 GitHub / 배포 준비

Status: local-ready, remote GitHub repo not connected yet.

## Project

- Local folder: `/Users/oceanblue/Desktop/MONEY/개발/07_웹·서비스 제작/잇츠몰`
- Site context: `ittemmall.com`
- Source copied from: `러닝 용품 사이트(서머텍트 본)`

## GitHub Rule

GitHub should keep public source and documentation only.

Do not commit:

- `node_modules/`
- `.playwright-cli/`
- `output/`, `outputs/`
- deployment ZIP files
- secrets, API keys, tokens, credentials
- customer/order/session/runtime data

## Deployment Shape

For now, treat deployment as a static/PHP-capable hosting upload depending on the final server setup:

1. Edit source locally.
2. Commit and push public source to GitHub.
3. Build or prepare upload files if needed.
4. Upload only public files to the hosting web root.
5. Verify the live `ittemmall.com` URL and key routes.

## Next Owner Gate

To connect GitHub remote, provide or create the GitHub repository URL.

