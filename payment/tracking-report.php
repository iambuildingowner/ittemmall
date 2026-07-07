<?php
declare(strict_types=1);

require_once __DIR__ . '/server-config-lib.php';

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

function reportResponse(int $status, array $payload): void
{
    http_response_code($status);
    echo json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

function reportClean(mixed $value, int $max = 240): string
{
    $text = trim((string)$value);
    $text = preg_replace('/\s+/', ' ', $text) ?? $text;
    if (function_exists('mb_substr')) {
        return mb_substr($text, 0, $max, 'UTF-8');
    }
    return substr($text, 0, $max);
}

function reportCounterAdd(array &$counter, string $key): void
{
    $key = $key !== '' ? $key : '(empty)';
    $counter[$key] = ($counter[$key] ?? 0) + 1;
}

function reportIsButtonEvent(string $eventName): bool
{
    return $eventName === 'NpayPurchaseClick'
        || $eventName === 'PurchaseCtaClick'
        || str_starts_with($eventName, 'NpayPurchaseClick_')
        || str_starts_with($eventName, 'PurchaseCtaClick_');
}

function reportAttribution(array $entry, array $payload, string $key): string
{
    $payloadAttribution = is_array($payload['attribution'] ?? null) ? $payload['attribution'] : [];
    $entryAttribution = is_array($entry['attribution'] ?? null) ? $entry['attribution'] : [];
    return reportClean($payloadAttribution[$key] ?? $entryAttribution[$key] ?? '', 200);
}

function reportIsTruthyParam(string $value): bool
{
    return in_array(strtolower(trim($value)), ['1', 'true', 'yes', 'on'], true);
}

function reportIsTestEntry(array $entry, array $payload): bool
{
    $url = (string)($entry['url'] ?? '');
    return ($payload['__test'] ?? false) === true
        || ($payload['testRunId'] ?? '') !== ''
        || ($payload['test_run_id'] ?? '') !== ''
        || str_contains($url, 'pixel_test=1')
        || str_contains($url, 'test_run_id=');
}

function reportDedupeKey(array $entry, array $payload, int $fallbackIndex): string
{
    $values = [
        $entry['visitor_id'] ?? null,
        $payload['visitorId'] ?? null,
        $entry['visit_id'] ?? null,
        $payload['visitId'] ?? null,
        $entry['click_id'] ?? null,
        $payload['clickId'] ?? null,
        $entry['event_id'] ?? null,
        $payload['pixelEventId'] ?? null,
        $entry['server_record_id'] ?? null,
        $entry['request']['ip_hash'] ?? null,
        $entry['ipHash'] ?? null,
    ];
    foreach ($values as $value) {
        $text = reportClean($value ?? '', 120);
        if ($text !== '') {
            return $text;
        }
    }
    return 'fallback-' . (string)$fallbackIndex;
}

function reportMatchesTargetProduct(string $eventName, string $product, array $payload, string $targetSlug, string $targetId): bool
{
    $targetSuffix = str_replace('-', '_', $targetSlug);
    $payloadSlug = reportClean($payload['productSlug'] ?? '', 160);
    $payloadId = reportClean($payload['productId'] ?? $payload['product_id'] ?? '', 160);
    return $product === $targetSlug
        || $product === $targetId
        || $payloadSlug === $targetSlug
        || $payloadId === $targetId
        || str_ends_with($eventName, '_' . $targetSuffix);
}

$adminToken = ittemmallConfigValue('ITTEMMALL_ADMIN_TOKEN');
$givenToken = (string)($_GET['token'] ?? ($_SERVER['HTTP_X_ITTEMMALL_ADMIN_TOKEN'] ?? ''));
if ($adminToken === '' || !hash_equals($adminToken, $givenToken)) {
    reportResponse(404, ['ok' => false, 'error' => 'not_found']);
}

$date = (string)($_GET['date'] ?? '');
if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $date)) {
    $date = (new DateTimeImmutable('now', new DateTimeZone('Asia/Seoul')))->format('Y-m-d');
}

$sinceRaw = (string)($_GET['since'] ?? '');
$sinceTs = $sinceRaw !== '' ? strtotime($sinceRaw) : false;
$untilRaw = (string)($_GET['until'] ?? '');
$untilTs = $untilRaw !== '' ? strtotime($untilRaw) : false;
$includeTest = reportIsTruthyParam((string)($_GET['include_test'] ?? ''));
$targetSlug = reportClean((string)($_GET['product_slug'] ?? 'windcool-vest'), 160);
$targetId = reportClean((string)($_GET['product_id'] ?? 'product-003'), 160);
$logPath = ittemmallEffectiveTrackLogPath($date);
$result = [
    'ok' => true,
    'date' => $date,
    'since_kst' => $sinceRaw,
    'until_kst' => $untilRaw,
    'include_test' => $includeTest,
    'target_product_slug' => $targetSlug,
    'target_product_id' => $targetId,
    'log_exists' => is_file($logPath),
    'log_readable' => is_readable($logPath),
    'log_read_status' => is_file($logPath) && is_readable($logPath) ? 'LOG_READ_OK' : 'LOG_PATH_NOT_FOUND',
    'rows_total' => 0,
    'rows_excluded_test' => 0,
    'rows_included' => 0,
    'unique_visitors' => 0,
    'button_rows_count' => 0,
    'target_intent_summary' => [
        'total_button_clicks' => 0,
        'unique_order_intents' => 0,
        'npay_clicks' => 0,
        'purchase_cta_clicks' => 0,
        'battery_add_on_selected' => 0,
        'vest_only_selected' => 0,
    ],
    'event_counts' => [],
    'product_counts' => [],
    'path_counts' => [],
    'button_rows' => [],
    'latest_rows' => [],
];

if (!is_file($logPath) || !is_readable($logPath)) {
    reportResponse(200, $result);
}

$lines = file($logPath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
$visitors = [];
$targetIntentKeys = [];
$lineIndex = 0;
foreach ($lines === false ? [] : $lines as $line) {
    $lineIndex++;
    $entry = json_decode($line, true);
    if (!is_array($entry)) {
        continue;
    }
    $eventName = reportClean($entry['event'] ?? '', 120);
    if ($eventName === '') {
        continue;
    }

    $result['rows_total']++;
    $payload = is_array($entry['payload'] ?? null) ? $entry['payload'] : [];
    if (!$includeTest && reportIsTestEntry($entry, $payload)) {
        $result['rows_excluded_test']++;
        continue;
    }

    $timeKst = reportClean($entry['server_time_kst'] ?? '', 80);
    $timeTs = $timeKst !== '' ? strtotime($timeKst) : false;
    if ($sinceTs !== false && ($timeTs === false || $timeTs < $sinceTs)) {
        continue;
    }
    if ($untilTs !== false && ($timeTs === false || $timeTs > $untilTs)) {
        continue;
    }

    $product = reportClean($entry['product_focus'] ?? $payload['productSlug'] ?? $payload['productId'] ?? $payload['content_name'] ?? '(unknown)', 160);
    $path = reportClean($entry['path'] ?? '', 260);
    if ($path === '' && !empty($entry['url'])) {
        $urlPath = parse_url((string)$entry['url'], PHP_URL_PATH);
        $path = reportClean($urlPath ?: (string)$entry['url'], 260);
    }

    $visitor = reportClean($entry['visitor_id'] ?? $payload['visitorId'] ?? '', 80);
    $visitorKey = reportDedupeKey($entry, $payload, $lineIndex);
    if ($visitorKey !== '') {
        $visitors[$visitorKey] = true;
    }

    $row = [
        'time_kst' => str_replace('T', ' ', substr($timeKst, 0, 19)),
        'event' => $eventName,
        'product' => $product,
        'product_name' => reportClean($payload['productName'] ?? $payload['content_name'] ?? '', 180),
        'source' => reportAttribution($entry, $payload, 'utm_source'),
        'campaign' => reportAttribution($entry, $payload, 'utm_campaign'),
        'content' => reportAttribution($entry, $payload, 'utm_content'),
        'term' => reportAttribution($entry, $payload, 'utm_term'),
        'visitor_id' => $visitor,
        'visit_id' => reportClean($entry['visit_id'] ?? $payload['visitId'] ?? '', 80),
        'click_id' => reportClean($entry['click_id'] ?? $payload['clickId'] ?? '', 80),
        'event_id' => reportClean($entry['event_id'] ?? $payload['pixelEventId'] ?? '', 80),
        'server_record_id' => reportClean($entry['server_record_id'] ?? '', 80),
        'meta_pixel_id' => reportClean($entry['meta_pixel_id'] ?? $payload['metaPixelId'] ?? '', 80),
        'fbclid' => reportAttribution($entry, $payload, 'fbclid'),
        'test_id' => reportClean($payload['testRunId'] ?? $payload['test_run_id'] ?? '-', 140),
        'path' => $path,
    ];

    $result['rows_included']++;
    reportCounterAdd($result['event_counts'], $eventName);
    reportCounterAdd($result['product_counts'], $product);
    reportCounterAdd($result['path_counts'], $path);
    $result['latest_rows'][] = $row;
    if (count($result['latest_rows']) > 100) {
        array_shift($result['latest_rows']);
    }
    if (reportIsButtonEvent($eventName)) {
        $result['button_rows'][] = $row + [
            'options' => reportClean(json_encode($payload['selectedOptions'] ?? [], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES), 240),
        ];
        if (reportMatchesTargetProduct($eventName, $product, $payload, $targetSlug, $targetId)) {
            $optionText = json_encode($payload['selectedOptions'] ?? [], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
            $result['target_intent_summary']['total_button_clicks']++;
            if (str_starts_with($eventName, 'NpayPurchaseClick')) {
                $result['target_intent_summary']['npay_clicks']++;
            }
            if (str_starts_with($eventName, 'PurchaseCtaClick')) {
                $result['target_intent_summary']['purchase_cta_clicks']++;
            }
            if (is_string($optionText) && str_contains($optionText, '보조배터리 10,000mAh 추가')) {
                $result['target_intent_summary']['battery_add_on_selected']++;
            } else {
                $result['target_intent_summary']['vest_only_selected']++;
            }
            $targetIntentKeys[reportDedupeKey($entry, $payload, $lineIndex)] = true;
        }
    }
}

arsort($result['event_counts']);
arsort($result['product_counts']);
arsort($result['path_counts']);
$result['unique_visitors'] = count($visitors);
$result['button_rows_count'] = count($result['button_rows']);
$result['target_intent_summary']['unique_order_intents'] = count($targetIntentKeys);
$result['button_rows'] = array_slice($result['button_rows'], -100);
reportResponse(200, $result);
