<?php
declare(strict_types=1);

require_once __DIR__ . '/payment/server-config-lib.php';
require_once __DIR__ . '/payment/rate-limit-lib.php';

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

function ittemmallTrackResponse(int $status, array $payload): void
{
    http_response_code($status);
    echo json_encode($payload, JSON_UNESCAPED_UNICODE);
    exit;
}

function ittemmallTrackEnv(string $key): string
{
    return ittemmallConfigValue($key);
}

function ittemmallTrackCleanString(string $value, int $maxLength = 500): string
{
    $value = trim($value);
    if (function_exists('mb_substr')) {
        return mb_substr($value, 0, $maxLength, 'UTF-8');
    }
    return substr($value, 0, $maxLength);
}

function ittemmallTrackCleanPayload(mixed $value, int $depth = 0): mixed
{
    if ($depth > 4) {
        return null;
    }
    if (is_array($value)) {
        $clean = [];
        foreach ($value as $key => $item) {
            if (count($clean) >= 80) {
                break;
            }
            $clean[ittemmallTrackCleanString((string)$key, 100)] = ittemmallTrackCleanPayload($item, $depth + 1);
        }
        return $clean;
    }
    if (is_bool($value) || is_int($value) || is_float($value) || $value === null) {
        return $value;
    }
    return ittemmallTrackCleanString((string)$value, 1000);
}

function ittemmallTrackKstTimestamp(DateTimeImmutable $utcNow): string
{
    return $utcNow->setTimezone(new DateTimeZone('Asia/Seoul'))->format('c');
}

function ittemmallTrackTestRunId(array $payload): string
{
    $testRunId = ittemmallTrackCleanString((string)($payload['testRunId'] ?? $payload['test_run_id'] ?? ''), 120);
    if (!preg_match('/^[A-Za-z0-9._:-]{12,120}$/', $testRunId)) {
        return '';
    }
    return $testRunId;
}

function ittemmallTrackDedupeKey(array $entry, array $payload, int $fallbackIndex): string
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
        $text = ittemmallTrackCleanString((string)($value ?? ''), 120);
        if ($text !== '') {
            return $text;
        }
    }
    return 'fallback-' . (string)$fallbackIndex;
}

function ittemmallTrackIsButtonEventName(string $eventName): bool
{
    return $eventName === 'NpayPurchaseClick'
        || $eventName === 'PurchaseCtaClick'
        || str_starts_with($eventName, 'NpayPurchaseClick_')
        || str_starts_with($eventName, 'PurchaseCtaClick_');
}

function ittemmallTrackCleanupTestEvents(string $testRunId): array
{
    $logPath = ittemmallEffectiveTrackLogPath();
    if (!is_file($logPath)) {
        return ['removed' => 0, 'events' => [], 'dedupe' => ['uniqueRows' => 0, 'uniqueButtonIntents' => 0], 'samples' => []];
    }

    $lines = file($logPath, FILE_IGNORE_NEW_LINES);
    if ($lines === false) {
        ittemmallTrackResponse(500, ['ok' => false, 'error' => 'TRACK_READ_FAILED']);
    }

    $kept = [];
    $removed = 0;
    $events = [];
    $dedupeKeys = [];
    $buttonDedupeKeys = [];
    $samples = [];
    $lineIndex = 0;
    foreach ($lines as $line) {
        $lineIndex++;
        if (trim($line) === '') {
            continue;
        }
        $entry = json_decode($line, true);
        $payload = is_array($entry) && is_array($entry['payload'] ?? null) ? $entry['payload'] : [];
        $entryTestRunId = ittemmallTrackTestRunId($payload);
        $isTest = ($payload['__test'] ?? false) === true;
        if ($isTest && $entryTestRunId !== '' && hash_equals($testRunId, $entryTestRunId)) {
            $removed += 1;
            $eventName = (string)($entry['event'] ?? '');
            if ($eventName !== '') {
                $events[$eventName] = ($events[$eventName] ?? 0) + 1;
            }
            $dedupeKey = is_array($entry) ? ittemmallTrackDedupeKey($entry, $payload, $lineIndex) : 'fallback-' . (string)$lineIndex;
            $dedupeKeys[$dedupeKey] = true;
            if (ittemmallTrackIsButtonEventName($eventName)) {
                $buttonDedupeKeys[$dedupeKey] = true;
            }
            if (is_array($entry) && count($samples) < 10) {
                $samples[] = [
                    'event' => $eventName,
                    'product' => ittemmallTrackCleanString((string)($entry['product_focus'] ?? $payload['productSlug'] ?? $payload['productId'] ?? ''), 120),
                    'visitorId' => ittemmallTrackCleanString((string)($entry['visitor_id'] ?? $payload['visitorId'] ?? ''), 120),
                    'visitId' => ittemmallTrackCleanString((string)($entry['visit_id'] ?? $payload['visitId'] ?? ''), 120),
                    'clickId' => ittemmallTrackCleanString((string)($entry['click_id'] ?? $payload['clickId'] ?? ''), 120),
                    'eventId' => ittemmallTrackCleanString((string)($entry['event_id'] ?? $payload['pixelEventId'] ?? ''), 120),
                    'serverRecordId' => ittemmallTrackCleanString((string)($entry['server_record_id'] ?? ''), 120),
                    'dedupeKey' => $dedupeKey,
                ];
            }
            continue;
        }
        $kept[] = $line;
    }

    $dir = dirname($logPath);
    $tmpPath = $dir . '/.' . basename($logPath) . '.tmp';
    $content = $kept === [] ? '' : implode(PHP_EOL, $kept) . PHP_EOL;
    if (file_put_contents($tmpPath, $content, LOCK_EX) === false) {
        ittemmallTrackResponse(500, ['ok' => false, 'error' => 'TRACK_CLEANUP_WRITE_FAILED']);
    }
    if (!rename($tmpPath, $logPath)) {
        @unlink($tmpPath);
        ittemmallTrackResponse(500, ['ok' => false, 'error' => 'TRACK_CLEANUP_RENAME_FAILED']);
    }
    @chmod($logPath, 0600);
    ksort($events);
    return [
        'removed' => $removed,
        'events' => $events,
        'dedupe' => [
            'uniqueRows' => count($dedupeKeys),
            'uniqueButtonIntents' => count($buttonDedupeKeys),
            'order' => 'visitorId -> visitId -> clickId -> eventId/pixelEventId -> serverRecordId -> ipHash',
        ],
        'samples' => $samples,
    ];
}

function ittemmallTrackIsDisabledValue(string $value): bool
{
    return in_array(strtolower(trim($value)), ['0', 'false', 'no', 'off', 'disabled'], true);
}

function ittemmallTrackNotificationRecipient(): string
{
    $email = ittemmallConfigValue('ITTEMMALL_NOTIFY_EMAIL', 'staysiaofficial@gmail.com');
    return filter_var($email, FILTER_VALIDATE_EMAIL) ? $email : '';
}

function ittemmallTrackNotificationFrom(): string
{
    $email = ittemmallConfigValue('ITTEMMALL_NOTIFY_FROM', 'no-reply@ittemmall.com');
    return filter_var($email, FILTER_VALIDATE_EMAIL) ? $email : 'no-reply@ittemmall.com';
}

function ittemmallTrackNotificationEnabled(): bool
{
    $enabled = ittemmallConfigValue('ITTEMMALL_NOTIFY_ENABLED', '1');
    return !ittemmallTrackIsDisabledValue($enabled) && ittemmallTrackNotificationRecipient() !== '';
}

function ittemmallTrackIsPurchaseNotificationEvent(string $eventName, array $payload): bool
{
    if (($payload['__test'] ?? false) === true) {
        $allowsTestNotification = ($payload['notifyTest'] ?? false) === true && ittemmallTrackTestRunId($payload) !== '';
        if (!$allowsTestNotification) {
            return false;
        }
    }
    return str_starts_with($eventName, 'NpayPurchaseClick_') || str_starts_with($eventName, 'PurchaseCtaClick_');
}

function ittemmallTrackMoney(mixed $value): string
{
    $amount = is_numeric($value) ? (float)$value : 0.0;
    return number_format($amount) . '원';
}

function ittemmallTrackNotificationLabel(string $eventName): string
{
    if (str_starts_with($eventName, 'NpayPurchaseClick_')) {
        return 'N pay 버튼 클릭';
    }
    if (str_starts_with($eventName, 'PurchaseCtaClick_')) {
        return '바로 구매 버튼 클릭';
    }
    return $eventName;
}

function ittemmallTrackJsonLine(mixed $value): string
{
    return json_encode($value, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
}

function ittemmallTrackCreateId(string $prefix, DateTimeImmutable $utcNow): string
{
    $kstDate = $utcNow->setTimezone(new DateTimeZone('Asia/Seoul'))->format('Ymd');
    return sprintf('%s-%s-%s', $prefix, $kstDate, strtoupper(bin2hex(random_bytes(4))));
}

function ittemmallTrackReadableTime(string $timestamp): string
{
    if ($timestamp === '') {
        return '-';
    }
    $time = strtotime($timestamp);
    if ($time === false) {
        return str_replace('T', ' ', substr($timestamp, 0, 19));
    }
    return (new DateTimeImmutable('@' . $time))
        ->setTimezone(new DateTimeZone('Asia/Seoul'))
        ->format('Y-m-d H:i:s');
}

function ittemmallTrackOptionLabel(mixed $selectedOptions): string
{
    if (!is_array($selectedOptions) || $selectedOptions === []) {
        return '-';
    }
    $labels = [];
    foreach ($selectedOptions as $label => $value) {
        $labelText = ittemmallTrackCleanString((string)$label, 40);
        $valueText = ittemmallTrackCleanString((string)$value, 120);
        if ($valueText !== '') {
            $labels[] = $labelText . ': ' . $valueText;
        }
    }
    return $labels === [] ? '-' : implode(' / ', $labels);
}

function ittemmallTrackOptionSubject(mixed $selectedOptions): string
{
    if (!is_array($selectedOptions) || $selectedOptions === []) {
        return '';
    }
    $color = ittemmallTrackCleanString((string)($selectedOptions['색상'] ?? $selectedOptions['color'] ?? ''), 40);
    $size = ittemmallTrackCleanString((string)($selectedOptions['사이즈'] ?? $selectedOptions['size'] ?? ''), 40);
    return trim($color . ' ' . $size);
}

function ittemmallTrackShortValue(mixed $value, int $front = 18, int $back = 10): string
{
    $text = ittemmallTrackCleanString((string)$value, 1000);
    if ($text === '') {
        return '-';
    }
    if (function_exists('mb_strlen') && mb_strlen($text, 'UTF-8') > ($front + $back + 3)) {
        return mb_substr($text, 0, $front, 'UTF-8') . '...' . mb_substr($text, -$back, null, 'UTF-8');
    }
    if (!function_exists('mb_strlen') && strlen($text) > ($front + $back + 3)) {
        return substr($text, 0, $front) . '...' . substr($text, -$back);
    }
    return $text;
}

function ittemmallTrackAttributionValue(array $payload, array $event, string $key): string
{
    $payloadAttribution = is_array($payload['attribution'] ?? null) ? $payload['attribution'] : [];
    $eventAttribution = is_array($event['attribution'] ?? null) ? $event['attribution'] : [];
    return ittemmallTrackCleanString((string)($payloadAttribution[$key] ?? $eventAttribution[$key] ?? ''), 240);
}

function ittemmallTrackFirstNonEmpty(mixed ...$values): string
{
    foreach ($values as $value) {
        $text = ittemmallTrackCleanString((string)$value, 240);
        if ($text !== '') {
            return $text;
        }
    }
    return '';
}

function ittemmallTrackSendPurchaseNotification(array $event): array
{
    $eventName = (string)($event['event'] ?? '');
    $payload = is_array($event['payload'] ?? null) ? $event['payload'] : [];
    if (!ittemmallTrackNotificationEnabled() || !ittemmallTrackIsPurchaseNotificationEvent($eventName, $payload)) {
        return ['attempted' => false, 'sent' => false];
    }

    $recipient = ittemmallTrackNotificationRecipient();
    $from = ittemmallTrackNotificationFrom();
    $eventLabel = ittemmallTrackNotificationLabel($eventName);
    $productName = ittemmallTrackCleanString((string)($payload['productName'] ?? $payload['content_name'] ?? $event['product_focus'] ?? '상품명 미확인'), 160);
    $productSlug = ittemmallTrackCleanString((string)($payload['productSlug'] ?? $event['product_focus'] ?? ''), 120);
    $price = ittemmallTrackMoney($payload['price'] ?? $payload['value'] ?? 0);
    $amount = ittemmallTrackMoney($payload['amount'] ?? $payload['value'] ?? 0);
    $quantity = ittemmallTrackCleanString((string)($payload['quantity'] ?? '1'), 20);
    $url = ittemmallTrackCleanString((string)($event['url'] ?? ''), 1000);
    $kstTime = ittemmallTrackCleanString((string)($event['server_time_kst'] ?? ''), 80);
    $selectedOptions = $payload['selectedOptions'] ?? [];
    $attribution = is_array($payload['attribution'] ?? null) ? $payload['attribution'] : (is_array($event['attribution'] ?? null) ? $event['attribution'] : []);
    $metaBrowserIds = is_array($payload['metaBrowserIds'] ?? null) ? $payload['metaBrowserIds'] : (is_array($event['meta_browser_ids'] ?? null) ? $event['meta_browser_ids'] : []);
    $visitorId = ittemmallTrackFirstNonEmpty($payload['visitorId'] ?? '', $event['visitor_id'] ?? '');
    $visitId = ittemmallTrackFirstNonEmpty($payload['visitId'] ?? '', $event['visit_id'] ?? '');
    $clickId = ittemmallTrackFirstNonEmpty($payload['clickId'] ?? '', $event['click_id'] ?? '');
    $pixelEventId = ittemmallTrackFirstNonEmpty($payload['pixelEventId'] ?? '', $event['event_id'] ?? '');
    $serverRecordId = ittemmallTrackCleanString((string)($event['server_record_id'] ?? ''), 80);
    $metaPixelId = ittemmallTrackFirstNonEmpty($payload['metaPixelId'] ?? '', $event['meta_pixel_id'] ?? '');
    $utmSource = ittemmallTrackAttributionValue($payload, $event, 'utm_source');
    $utmCampaign = ittemmallTrackAttributionValue($payload, $event, 'utm_campaign');
    $utmContent = ittemmallTrackAttributionValue($payload, $event, 'utm_content');
    $utmTerm = ittemmallTrackAttributionValue($payload, $event, 'utm_term');
    $fbclid = ittemmallTrackAttributionValue($payload, $event, 'fbclid');
    $fbp = ittemmallTrackCleanString((string)($metaBrowserIds['fbp'] ?? ''), 180);
    $fbc = ittemmallTrackCleanString((string)($metaBrowserIds['fbc'] ?? ''), 240);

    $isTest = ($payload['__test'] ?? false) === true;
    $testRunId = ittemmallTrackTestRunId($payload);
    $optionLabel = ittemmallTrackOptionLabel($selectedOptions);
    $subjectOption = ittemmallTrackOptionSubject($selectedOptions);
    $shortOption = $subjectOption !== '' ? ' / ' . $subjectOption : '';
    $subject = sprintf(
        '[잇템몰%s] %s / %s%s',
        $isTest ? ' 테스트' : '',
        $eventLabel,
        $productName,
        $shortOption
    );
    $encodedSubject = '=?UTF-8?B?' . base64_encode($subject) . '?=';
    $body = implode("\n", [
        '잇템몰 구매 관련 버튼이 눌렸습니다.',
        '',
        '[바로 볼 내용]',
        '상태: 결제 완료가 아니라 구매 버튼 클릭입니다.',
        '버튼: ' . $eventLabel,
        '상품명: ' . $productName,
        '옵션: ' . $optionLabel,
        '수량: ' . $quantity,
        '계산 금액: ' . $amount,
        '시간: ' . ittemmallTrackReadableTime($kstTime),
        '유입: ' . ($utmSource !== '' ? $utmSource : '미확인'),
        '',
        '[같은 사람/같은 클릭 확인용]',
        '방문번호: ' . ($visitorId !== '' ? $visitorId : '-'),
        '이번 방문번호: ' . ($visitId !== '' ? $visitId : '-'),
        '클릭번호: ' . ($clickId !== '' ? $clickId : '-'),
        '픽셀 이벤트번호: ' . ($pixelEventId !== '' ? $pixelEventId : '-'),
        '서버 기록번호: ' . ($serverRecordId !== '' ? $serverRecordId : '-'),
        '',
        '[메타 광고/픽셀]',
        '메타 픽셀 ID: ' . ($metaPixelId !== '' ? $metaPixelId : '-'),
        '광고 클릭값 fbclid: ' . ittemmallTrackShortValue($fbclid, 24, 16),
        '브라우저값 _fbp: ' . ($fbp !== '' ? $fbp : '-'),
        '브라우저값 _fbc: ' . ittemmallTrackShortValue($fbc, 24, 16),
        '캠페인: ' . ($utmCampaign !== '' ? $utmCampaign : '-'),
        '소재: ' . ($utmContent !== '' ? $utmContent : '-'),
        '타깃/키워드: ' . ($utmTerm !== '' ? $utmTerm : '-'),
        '',
        '[상품 원본값]',
        '이벤트명: ' . $eventName,
        '상품 slug: ' . ($productSlug !== '' ? $productSlug : '-'),
        '상품 ID: ' . ittemmallTrackCleanString((string)($payload['productId'] ?? '-'), 80),
        '가격: ' . $price,
        '테스트 ID: ' . ($testRunId !== '' ? $testRunId : '-'),
        '',
        '[상세 원본]',
        'URL: ' . ($url !== '' ? $url : '-'),
        '유입 원본: ' . ($attribution !== [] ? ittemmallTrackJsonLine($attribution) : '-'),
    ]) . "\n";

    $headers = implode("\r\n", [
        'MIME-Version: 1.0',
        'Content-Type: text/plain; charset=UTF-8',
        'Content-Transfer-Encoding: 8bit',
        'From: ITTEMMALL <' . $from . '>',
    ]);

    $sent = @mail($recipient, $encodedSubject, $body, $headers);
    return [
        'attempted' => true,
        'sent' => $sent,
        'recipient' => $recipient,
    ];
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    ittemmallTrackResponse(405, ['ok' => false, 'error' => 'METHOD_NOT_ALLOWED']);
}

try {
    $rateLimit = ittemmallRateLimitCheck('track', 240, 300);
    if (!$rateLimit['allowed']) {
        header('Retry-After: ' . (string)$rateLimit['retryAfter']);
        ittemmallTrackResponse(429, [
            'ok' => false,
            'error' => 'RATE_LIMITED',
            'retryAfter' => $rateLimit['retryAfter'],
        ]);
    }
} catch (Throwable $error) {
    ittemmallTrackResponse(500, [
        'ok' => false,
        'error' => 'RATE_LIMIT_FAILED',
        'message' => $error->getMessage(),
    ]);
}

$rawBody = file_get_contents('php://input') ?: '';
$body = json_decode($rawBody, true);

if (!is_array($body)) {
    ittemmallTrackResponse(400, ['ok' => false, 'error' => 'INVALID_JSON']);
}

$eventName = ittemmallTrackCleanString((string)($body['event'] ?? ''), 80);
if ($eventName === '') {
    ittemmallTrackResponse(400, ['ok' => false, 'error' => 'MISSING_EVENT']);
}

$payload = ittemmallTrackCleanPayload($body['payload'] ?? []);
if (!is_array($payload)) {
    $payload = [];
}

if ($eventName === '__cleanup_test_events') {
    $testRunId = ittemmallTrackTestRunId($payload);
    if ($testRunId === '') {
        ittemmallTrackResponse(400, ['ok' => false, 'error' => 'MISSING_TEST_RUN_ID']);
    }
    $cleanup = ittemmallTrackCleanupTestEvents($testRunId);
    ittemmallTrackResponse(200, [
        'ok' => true,
        'cleanup' => true,
        'testRunId' => $testRunId,
        'removed' => $cleanup['removed'],
        'events' => $cleanup['events'],
        'dedupe' => $cleanup['dedupe'],
        'samples' => $cleanup['samples'],
    ]);
}

$salt = ittemmallEffectiveTrackSalt();
if ($salt === '') {
    ittemmallTrackResponse(500, ['ok' => false, 'error' => 'TRACK_SALT_CREATE_FAILED']);
}

$utcNow = new DateTimeImmutable('now', new DateTimeZone('UTC'));
$ipHash = hash('sha256', (string)($_SERVER['REMOTE_ADDR'] ?? '') . ':' . $salt);
$productFocus = ittemmallTrackCleanString(
    (string)($body['product_focus'] ?? $payload['productSlug'] ?? $payload['productId'] ?? 'ittemmall'),
    160
);
$serverRecordId = ittemmallTrackCreateId('SRV', $utcNow);
$eventId = ittemmallTrackFirstNonEmpty($body['event_id'] ?? '', $payload['pixelEventId'] ?? '', ittemmallTrackCreateId('EVT', $utcNow));
$visitorId = ittemmallTrackFirstNonEmpty($body['visitor_id'] ?? '', $payload['visitorId'] ?? '');
$visitId = ittemmallTrackFirstNonEmpty($body['visit_id'] ?? '', $payload['visitId'] ?? '');
$clickId = ittemmallTrackFirstNonEmpty($body['click_id'] ?? '', $payload['clickId'] ?? '');
$metaPixelId = ittemmallTrackFirstNonEmpty($body['meta_pixel_id'] ?? '', $payload['metaPixelId'] ?? '');
$metaBrowserIds = ittemmallTrackCleanPayload($body['meta_browser_ids'] ?? ($payload['metaBrowserIds'] ?? []));

$event = [
    'event' => $eventName,
    'payload' => $payload,
    'server_record_id' => $serverRecordId,
    'event_id' => $eventId,
    'visitor_id' => $visitorId,
    'visit_id' => $visitId,
    'click_id' => $clickId,
    'meta_pixel_id' => $metaPixelId,
    'meta_browser_ids' => is_array($metaBrowserIds) ? $metaBrowserIds : [],
    'brand' => ittemmallTrackCleanString((string)($body['brand'] ?? 'ITTEMMALL'), 80),
    'product_focus' => $productFocus,
    'path' => ittemmallTrackCleanString((string)($body['path'] ?? ''), 500),
    'url' => ittemmallTrackCleanString((string)($body['url'] ?? ''), 1000),
    'referrer' => ittemmallTrackCleanString((string)($body['referrer'] ?? ''), 1000),
    'attribution' => ittemmallTrackCleanPayload($body['attribution'] ?? []),
    'userAgent' => ittemmallTrackCleanString((string)($_SERVER['HTTP_USER_AGENT'] ?? ''), 500),
    'ipHash' => $ipHash,
    'request' => [
        'ip_hash' => $ipHash,
        'user_agent' => ittemmallTrackCleanString((string)($_SERVER['HTTP_USER_AGENT'] ?? ''), 500),
    ],
    'createdAt' => $utcNow->format('c'),
    'server_time_utc' => $utcNow->format('c'),
    'server_time_kst' => ittemmallTrackKstTimestamp($utcNow),
];

$logPath = ittemmallEffectiveTrackLogPath();
$dir = dirname($logPath);
if (!is_dir($dir) && !mkdir($dir, 0700, true)) {
    ittemmallTrackResponse(500, ['ok' => false, 'error' => 'TRACK_DIRECTORY_CREATE_FAILED']);
}

$line = json_encode($event, JSON_UNESCAPED_UNICODE) . PHP_EOL;
if (file_put_contents($logPath, $line, FILE_APPEND | LOCK_EX) === false) {
    ittemmallTrackResponse(500, ['ok' => false, 'error' => 'TRACK_WRITE_FAILED']);
}
@chmod($logPath, 0600);

$notification = ittemmallTrackSendPurchaseNotification($event);

ittemmallTrackResponse(200, [
    'ok' => true,
    'stored' => true,
    'test' => ($payload['__test'] ?? false) === true,
    'event' => $eventName,
    'serverRecordId' => $serverRecordId,
    'eventId' => $eventId,
    'visitorId' => $visitorId,
    'visitId' => $visitId,
    'clickId' => $clickId,
    'notification' => [
        'attempted' => $notification['attempted'],
        'sent' => $notification['sent'],
    ],
]);
