# 잇츠몰 GitHub / 배포 준비

Status: local Git baseline committed, remote GitHub repo not connected yet.

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

## Current Completion State

Done:

- Local project folder separated.
- `.gitignore` created.
- Local Git repository initialized.
- Initial baseline commit created: `ec23365 Initial project baseline`.

Not done yet:

- GitHub remote repo connection.
- GitHub push.
- Production server deployment.

## How To Resume

When resuming this project, continue from this folder:

`/Users/oceanblue/Desktop/MONEY/개발/07_웹·서비스 제작/잇츠몰`

Then:

1. Create or receive the GitHub repository URL.
2. Run `git remote add origin <GITHUB_REPO_URL>`.
3. Run `git push -u origin main`.
4. Decide the actual hosting/deployment route for `ittemmall.com`.
5. Upload only public deployment files to the server.
6. Verify the live URL, core routes, mobile rendering, SEO basics, and tracking.

Do not say GitHub or production deployment is complete until those steps are actually done.
