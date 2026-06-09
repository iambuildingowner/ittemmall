# 잇템몰 GitHub / 배포 준비

Status: local Git baseline committed, GitHub remote connected, safe baseline branch pushed.

## Project

- Local folder: `/Users/oceanblue/Desktop/MONEY/개발/07_웹·서비스 제작/잇템몰`
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

## GitHub Remote

- Remote URL: `https://github.com/iambuildingowner/ittemmall.git`
- GitHub repo: `https://github.com/iambuildingowner/ittemmall`
- Existing remote branch: `main`
- Safe baseline branch: `codex/ittemmall-baseline`

Important: remote `main` already had prior history before this local project was connected. Do not force-push or overwrite `main` unless the owner explicitly confirms that the existing remote history can be replaced.

## Next Owner Gate

Decide how the safe baseline branch should become the production source:

1. Review `codex/ittemmall-baseline`.
2. Choose whether to merge it into `main`, replace `main`, or keep it as a separate baseline branch.
3. Decide the actual hosting/deployment route for `ittemmall.com`.

## Current Completion State

Done:

- Local project folder separated.
- `.gitignore` created.
- Local Git repository initialized.
- Initial baseline commit created: `ec23365 Initial project baseline`.
- GitHub remote connected as `origin`.
- Existing remote `main` fetched and preserved.
- Safe baseline branch created: `codex/ittemmall-baseline`.
- Safe baseline branch pushed to GitHub.

Not done yet:

- Owner decision for remote `main` merge/replace strategy.
- Production server deployment.

## How To Resume

When resuming this project, continue from this folder:

`/Users/oceanblue/Desktop/MONEY/개발/07_웹·서비스 제작/잇템몰`

Then:

1. Confirm the current branch is `codex/ittemmall-baseline`.
2. Push/update the safe baseline branch if needed.
3. Review differences against `origin/main`.
4. Decide whether to merge, replace, or keep branches separate.
5. Decide the actual hosting/deployment route for `ittemmall.com`.
6. Upload only public deployment files to the server.
7. Verify the live URL, core routes, mobile rendering, SEO basics, and tracking.

Do not say GitHub or production deployment is complete until those steps are actually done.
