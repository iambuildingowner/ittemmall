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

function ittemmallTrackCleanupTestEvents(string $testRunId): array
{
    $logPath = ittemmallEffectiveTrackLogPath();
    if (!is_file($logPath)) {
        return ['removed' => 0, 'events' => []];
    }

    $lines = file($logPath, FILE_IGNORE_NEW_LINES);
    if ($lines === false) {
        ittemmallTrackResponse(500, ['ok' => false, 'error' => 'TRACK_READ_FAILED']);
    }

    $kept = [];
    $removed = 0;
    $events = [];
    foreach ($lines as $line) {
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
    return ['removed' => $removed, 'events' => $events];
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
        return false;
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
    $attribution = $payload['attribution'] ?? ($event['attribution'] ?? []);

    $subject = sprintf('[잇템몰 클릭] %s / %s', $eventLabel, $productName);
    $encodedSubject = '=?UTF-8?B?' . base64_encode($subject) . '?=';
    $body = implode("\n", [
        '잇템몰 상품 클릭 로그가 들어왔습니다.',
        '',
        '종류: ' . $eventLabel,
        '이벤트: ' . $eventName,
        '상품명: ' . $productName,
        '상품 slug: ' . ($productSlug !== '' ? $productSlug : '-'),
        '상품 ID: ' . ittemmallTrackCleanString((string)($payload['productId'] ?? '-'), 80),
        '가격: ' . $price,
        '수량: ' . $quantity,
        '계산 금액: ' . $amount,
        '선택 옵션: ' . (is_array($selectedOptions) && $selectedOptions !== [] ? ittemmallTrackJsonLine($selectedOptions) : '-'),
        'URL: ' . ($url !== '' ? $url : '-'),
        '유입값: ' . (is_array($attribution) && $attribution !== [] ? ittemmallTrackJsonLine($attribution) : '-'),
        '서버 시간: ' . ($kstTime !== '' ? $kstTime : '-'),
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

$event = [
    'event' => $eventName,
    'payload' => $payload,
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
    'notification' => [
        'attempted' => $notification['attempted'],
        'sent' => $notification['sent'],
    ],
]);
