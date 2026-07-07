#!/usr/bin/env python3
"""Ittemmall ad tracking preflight.

Checks Meta ad stats, Meta Pixel custom event counts, live server health,
protected server report availability, and optional test click storage.
Never prints access tokens.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_META_ENV = Path("/Users/oceanblue/.codex/meta_ads.env")
DEFAULT_BASE_URL = "https://ittemmall.com"
GRAPH_VERSION = "v23.0"


def parse_env_file(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.is_file():
        return env
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            env[key] = value
    return env


def first_env_value(env: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = os.environ.get(key) or env.get(key) or ""
        if value.strip():
            return value.strip()
    return ""


def parse_time(value: str) -> dt.datetime:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    if len(normalized) >= 5 and normalized[-5] in ["+", "-"] and normalized[-2] != ":":
        normalized = normalized[:-2] + ":" + normalized[-2:]
    parsed = dt.datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def kst_now_id() -> str:
    now = dt.datetime.now(dt.timezone.utc).astimezone(dt.timezone(dt.timedelta(hours=9)))
    return now.strftime("%Y%m%d-%H%M%S")


def request_json(
    method: str,
    url: str,
    *,
    query: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 25,
) -> dict[str, Any]:
    final_url = url
    if query:
        query_string = urllib.parse.urlencode({k: v for k, v in query.items() if v is not None})
        final_url = f"{url}?{query_string}"
    body = None
    request_headers = {"Accept": "application/json"}
    if headers:
        request_headers.update(headers)
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request_headers["Content-Type"] = "application/json; charset=utf-8"
    request = urllib.request.Request(final_url, data=body, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8", errors="replace")
            try:
                return {
                    "ok": True,
                    "status": response.status,
                    "data": json.loads(text) if text else None,
                }
            except json.JSONDecodeError:
                return {
                    "ok": False,
                    "status": response.status,
                    "error": "NON_JSON_RESPONSE",
                    "body_preview": text[:240],
                }
    except urllib.error.HTTPError as error:
        text = error.read().decode("utf-8", errors="replace")
        parsed: Any
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = text[:240]
        return {"ok": False, "status": error.code, "error": "HTTP_ERROR", "data": parsed}
    except Exception as error:  # noqa: BLE001 - command-line diagnostic tool
        return {"ok": False, "status": None, "error": type(error).__name__, "message": str(error)}


def graph_get(path: str, token: str, params: dict[str, Any]) -> dict[str, Any]:
    safe_params = dict(params)
    safe_params["access_token"] = token
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{path.lstrip('/')}"
    result = request_json("GET", url, query=safe_params)
    if result.get("data") and isinstance(result["data"], dict):
        result["data"].pop("paging", None)
    return result


def numeric(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def extract_action_count(actions: Any, action_type: str) -> float:
    if not isinstance(actions, list):
        return 0.0
    for action in actions:
        if isinstance(action, dict) and action.get("action_type") == action_type:
            return numeric(action.get("value"))
    return 0.0


def summarize_insights(result: dict[str, Any]) -> dict[str, Any]:
    if not result.get("ok"):
        return {"ok": False, "error": result.get("data") or result.get("message") or result.get("error")}
    rows = result.get("data", {}).get("data") if isinstance(result.get("data"), dict) else None
    first = rows[0] if isinstance(rows, list) and rows else {}
    actions = first.get("actions", []) if isinstance(first, dict) else []
    return {
        "ok": True,
        "spend": int(round(numeric(first.get("spend")))),
        "impressions": int(round(numeric(first.get("impressions")))),
        "clicks": int(round(numeric(first.get("clicks")))),
        "inline_link_clicks": int(round(numeric(first.get("inline_link_clicks")))),
        "unique_clicks": int(round(numeric(first.get("unique_clicks")))),
        "unique_inline_link_clicks": int(round(numeric(first.get("unique_inline_link_clicks")))),
        "landing_page_views": int(round(extract_action_count(actions, "landing_page_view"))),
        "raw_date_start": first.get("date_start"),
        "raw_date_stop": first.get("date_stop"),
    }


def pixel_event_count(result: dict[str, Any]) -> int | None:
    if not result.get("ok"):
        return None
    data = result.get("data", {}).get("data") if isinstance(result.get("data"), dict) else None
    if not isinstance(data, list):
        return None
    total = 0.0
    for row in data:
        if not isinstance(row, dict):
            continue
        nested = row.get("data")
        if isinstance(nested, list):
            for nested_row in nested:
                if not isinstance(nested_row, dict):
                    continue
                total += numeric(nested_row.get("count"))
            continue
        if "value" in row:
            total += numeric(row.get("value"))
        elif "count" in row:
            total += numeric(row.get("count"))
    return int(round(total))


def meta_checks(args: argparse.Namespace, token: str) -> dict[str, Any]:
    if not token:
        return {"ok": False, "error": "META_ACCESS_TOKEN_MISSING"}

    since = parse_time(args.since_utc)
    until = parse_time(args.until_utc)
    kst = dt.timezone(dt.timedelta(hours=9))
    time_range = {
        "since": since.astimezone(kst).date().isoformat(),
        "until": until.astimezone(kst).date().isoformat(),
    }
    insights_raw = graph_get(
        f"{args.ad_id}/insights",
        token,
        {
            "fields": "spend,impressions,clicks,inline_link_clicks,unique_clicks,unique_inline_link_clicks,actions",
            "time_range": json.dumps(time_range, separators=(",", ":")),
        },
    )

    event_suffix = args.product_slug.replace("-", "_")
    events = [
        f"NpayPurchaseClick_{event_suffix}",
        "NpayPurchaseClick",
        f"PurchaseCtaClick_{event_suffix}",
        "PurchaseCtaClick",
    ]
    pixel_stats: dict[str, Any] = {}
    for event_name in events:
        raw = graph_get(
            f"{args.pixel_id}/stats",
            token,
            {
                "event": event_name,
                "aggregation": "event",
                "since": str(int(since.timestamp())),
                "until": str(int(until.timestamp())),
            },
        )
        pixel_stats[event_name] = {
            "ok": bool(raw.get("ok")),
            "count": pixel_event_count(raw),
            "error": None if raw.get("ok") else raw.get("data") or raw.get("message") or raw.get("error"),
        }
        time.sleep(0.2)

    return {
        "ok": True,
        "ad_insights": summarize_insights(insights_raw),
        "pixel_stats": pixel_stats,
    }


def server_click_test(args: argparse.Namespace) -> dict[str, Any]:
    event_suffix = args.product_slug.replace("-", "_")
    test_run_id = args.test_run_id or f"preflight-{args.product_slug}-{kst_now_id()}"
    base_url = (
        f"{args.base_url}/?pixel_test=1"
        f"&test_run_id={urllib.parse.quote(test_run_id)}#/product/{args.product_slug}"
    )
    same_visitor = f"preflight-visitor-same-{test_run_id}"
    other_visitor = f"preflight-visitor-other-{test_run_id}"

    def build_payload(event_name: str, visitor_id: str, index: int) -> dict[str, Any]:
        return {
            "event": event_name,
            "product_focus": args.product_slug,
            "path": f"#/product/{args.product_slug}",
            "url": base_url,
            "payload": {
                "__test": True,
                "notifyTest": bool(args.notify_test),
                "testRunId": test_run_id,
                "productSlug": args.product_slug,
                "productId": args.product_id,
                "productName": args.product_name,
                "price": args.price,
                "value": args.price,
                "amount": args.price,
                "quantity": 1,
                "selectedOptions": args.selected_options,
                "visitorId": visitor_id,
                "visitId": f"preflight-visit-{visitor_id}",
                "clickId": f"preflight-click-{test_run_id}-{index}",
                "pixelEventId": f"preflight-pixel-{test_run_id}-{index}",
                "metaPixelId": args.pixel_id,
                "attribution": {"utm_source": "preflight", "utm_campaign": args.campaign_id},
            },
        }

    test_events = [
        build_payload(f"NpayPurchaseClick_{event_suffix}", same_visitor, 1),
        build_payload(f"NpayPurchaseClick_{event_suffix}", same_visitor, 2),
        build_payload(f"PurchaseCtaClick_{event_suffix}", other_visitor, 3),
    ]
    store_results = [
        request_json("POST", f"{args.base_url.rstrip('/')}/track.php", payload=payload)
        for payload in test_events
    ]
    cleanup = request_json(
        "POST",
        f"{args.base_url.rstrip('/')}/track.php",
        payload={"event": "__cleanup_test_events", "payload": {"__test": True, "testRunId": test_run_id}},
    )
    cleanup_data = cleanup.get("data", {}) if isinstance(cleanup.get("data"), dict) else {}
    dedupe = cleanup_data.get("dedupe", {}) if isinstance(cleanup_data.get("dedupe"), dict) else {}
    expected = {
        "stored_events": 3,
        "unique_button_intents": 2,
        "npay_clicks": 2,
        "purchase_cta_clicks": 1,
    }
    actual_events = cleanup_data.get("events", {}) if isinstance(cleanup_data.get("events"), dict) else {}
    actual = {
        "stored_events": cleanup_data.get("removed"),
        "unique_button_intents": dedupe.get("uniqueButtonIntents"),
        "npay_clicks": actual_events.get(f"NpayPurchaseClick_{event_suffix}", 0),
        "purchase_cta_clicks": actual_events.get(f"PurchaseCtaClick_{event_suffix}", 0),
    }
    return {
        "test_run_id": test_run_id,
        "store_results": store_results,
        "cleanup": cleanup,
        "stored_true": len(store_results) == 3
        and all(
            isinstance(result.get("data"), dict) and result.get("data", {}).get("stored") is True
            for result in store_results
        ),
        "cleanup_removed": cleanup_data.get("removed"),
        "dedupe_proof": {
            "expected": expected,
            "actual": actual,
            "passed": expected == actual,
            "meaning": "Two N pay clicks from the same visitor should count as one buyer intent, and one direct-buy click from another visitor should count as the second buyer intent.",
        },
    }


def server_checks(args: argparse.Namespace, admin_token: str) -> dict[str, Any]:
    healthcheck = request_json("GET", f"{args.base_url.rstrip('/')}/payment/healthcheck.php")
    report: dict[str, Any]
    if admin_token:
        report = request_json(
            "GET",
            f"{args.base_url.rstrip('/')}/payment/tracking-report.php",
            query={
                "token": admin_token,
                "date": parse_time(args.since_utc).astimezone(dt.timezone(dt.timedelta(hours=9))).date().isoformat(),
                "since": args.since_utc,
                "until": args.until_utc,
                "product_slug": args.product_slug,
                "product_id": args.product_id,
            },
        )
    else:
        report = {"ok": False, "status": "ADMIN_TOKEN_MISSING"}

    result: dict[str, Any] = {
        "healthcheck": healthcheck,
        "tracking_report": report,
    }
    if args.server_click_test:
        result["server_click_test"] = server_click_test(args)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Ittemmall ad tracking before judging results.")
    parser.add_argument("--product-slug", required=True)
    parser.add_argument("--product-id", required=True)
    parser.add_argument("--product-name", default="윈드쿨 에어 선풍기 조끼")
    parser.add_argument("--price", type=int, default=59900)
    parser.add_argument("--ad-id", required=True)
    parser.add_argument("--adset-id", required=True)
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--pixel-id", required=True)
    parser.add_argument("--since-utc", required=True)
    parser.add_argument("--until-utc", required=True)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--meta-env", default=str(DEFAULT_META_ENV))
    parser.add_argument("--admin-token", default="")
    parser.add_argument("--server-click-test", action="store_true")
    parser.add_argument("--notify-test", action="store_true")
    parser.add_argument("--test-run-id", default="")
    parser.add_argument("--write-json", default="")
    parser.add_argument(
        "--selected-options-json",
        default='{"사이즈":"L","추가상품":"보조배터리 10,000mAh 추가"}',
    )
    args = parser.parse_args()

    try:
        args.selected_options = json.loads(args.selected_options_json)
    except json.JSONDecodeError:
        print("selected-options-json must be valid JSON", file=sys.stderr)
        return 2

    meta_env = parse_env_file(Path(args.meta_env))
    token = first_env_value(
        meta_env,
        "META_ACCESS_TOKEN",
        "META_ADS_ACCESS_TOKEN",
        "FACEBOOK_ACCESS_TOKEN",
        "FB_ACCESS_TOKEN",
    )
    admin_token = args.admin_token or first_env_value(meta_env, "ITTEMMALL_ADMIN_TOKEN")

    output = {
        "ok": True,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "product": {"slug": args.product_slug, "id": args.product_id, "name": args.product_name},
        "window": {"since_utc": args.since_utc, "until_utc": args.until_utc},
        "meta": meta_checks(args, token),
        "server": server_checks(args, admin_token),
        "notes": [
            "Meta Pixel custom event count is event count, not server deduped visitors.",
            "If server tracking report is unavailable, do not call server purchase intent zero.",
            "When server-click-test is used, the tool sends two N pay clicks from the same visitor and one direct-buy click from another visitor, then cleanup must prove 3 clicks become 2 unique buyer intents.",
        ],
    }

    text = json.dumps(output, ensure_ascii=False, indent=2)
    if args.write_json:
        Path(args.write_json).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
