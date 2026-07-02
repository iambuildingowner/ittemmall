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

ittemmallTrackResponse(200, [
    'ok' => true,
    'stored' => true,
    'test' => ($payload['__test'] ?? false) === true,
    'event' => $eventName,
]);
