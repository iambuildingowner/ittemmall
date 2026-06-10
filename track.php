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

$event = [
    'event' => $eventName,
    'payload' => ittemmallTrackCleanPayload($body['payload'] ?? []),
    'brand' => ittemmallTrackCleanString((string)($body['brand'] ?? 'ITTEMMALL'), 80),
    'path' => ittemmallTrackCleanString((string)($body['path'] ?? ''), 500),
    'url' => ittemmallTrackCleanString((string)($body['url'] ?? ''), 1000),
    'referrer' => ittemmallTrackCleanString((string)($body['referrer'] ?? ''), 1000),
    'attribution' => ittemmallTrackCleanPayload($body['attribution'] ?? []),
    'userAgent' => ittemmallTrackCleanString((string)($_SERVER['HTTP_USER_AGENT'] ?? ''), 500),
    'ipHash' => hash('sha256', (string)($_SERVER['REMOTE_ADDR'] ?? '') . ':' . ittemmallTrackEnv('ITTEMMALL_TRACK_SALT')),
    'createdAt' => gmdate('c'),
];

$logPath = ittemmallTrackEnv('ITTEMMALL_TRACK_LOG_PATH');
if ($logPath === '') {
    ittemmallTrackResponse(200, ['ok' => true, 'stored' => false]);
}

$dir = dirname($logPath);
if (!is_dir($dir) && !mkdir($dir, 0700, true)) {
    ittemmallTrackResponse(500, ['ok' => false, 'error' => 'TRACK_DIRECTORY_CREATE_FAILED']);
}

$line = json_encode($event, JSON_UNESCAPED_UNICODE) . PHP_EOL;
if (file_put_contents($logPath, $line, FILE_APPEND | LOCK_EX) === false) {
    ittemmallTrackResponse(500, ['ok' => false, 'error' => 'TRACK_WRITE_FAILED']);
}
@chmod($logPath, 0600);

ittemmallTrackResponse(200, ['ok' => true, 'stored' => true]);
