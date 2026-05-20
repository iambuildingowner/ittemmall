<?php
declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode([
        'ok' => true,
        'service' => 'ittemmall pixel logger',
        'methods' => ['POST'],
    ], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

$raw = file_get_contents('php://input') ?: '';
$data = json_decode($raw, true);

if (!is_array($data)) {
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'invalid_json'], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

$allowedEvents = [
    'ViewContent',
    'AddToCart',
    'CheckoutStartClick',
    'CheckoutPageView',
    'InitiateCheckout',
    'NpayClick',
    'CheckoutFormStart',
    'PaymentGatewayClick',
    'PaymentPageView',
    'OptionSelect',
];

$eventName = preg_replace('/[^A-Za-z0-9_:-]/', '', (string)($data['event'] ?? ''));
if (!in_array($eventName, $allowedEvents, true)) {
    http_response_code(202);
    echo json_encode(['ok' => true, 'ignored' => true], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

$payload = is_array($data['payload'] ?? null) ? $data['payload'] : [];
$isTest = !empty($payload['__test']);
$kstZone = new DateTimeZone('Asia/Seoul');
$nowKst = new DateTimeImmutable('now', $kstZone);
$baseDir = __DIR__ . '/data';
$logDir = $baseDir . ($isTest ? '/pixel-events-test' : '/pixel-events');

ensureDirectory($baseDir);
ensureDirectory($logDir);
protectDataDirectory($baseDir);

$entry = [
    'server_time_utc' => gmdate('c'),
    'server_time_kst' => $nowKst->format(DateTimeInterface::ATOM),
    'event' => $eventName,
    'is_test' => $isTest,
    'meta_pixel_id' => cleanString($data['meta_pixel_id'] ?? ''),
    'brand' => cleanString($data['brand'] ?? ''),
    'product_focus' => cleanString($data['product_focus'] ?? ''),
    'path' => cleanString($data['path'] ?? ''),
    'url' => cleanString($data['url'] ?? ''),
    'referrer' => cleanString($data['referrer'] ?? ($_SERVER['HTTP_REFERER'] ?? '')),
    'attribution' => is_array($data['attribution'] ?? null) ? sanitizeArray($data['attribution']) : [],
    'payload' => sanitizeArray($payload),
    'request' => [
        'ip_hash' => hash('sha256', (string)($_SERVER['REMOTE_ADDR'] ?? '') . '|ittemmall-20260519'),
        'user_agent' => substr((string)($_SERVER['HTTP_USER_AGENT'] ?? ''), 0, 500),
        'accept_language' => substr((string)($_SERVER['HTTP_ACCEPT_LANGUAGE'] ?? ''), 0, 200),
    ],
];

$file = $logDir . '/' . $nowKst->format('Y-m-d') . '.ndjson';
$line = json_encode($entry, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . PHP_EOL;

if (file_put_contents($file, $line, FILE_APPEND | LOCK_EX) === false) {
    http_response_code(500);
    echo json_encode(['ok' => false, 'error' => 'write_failed'], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

echo json_encode([
    'ok' => true,
    'event' => $eventName,
    'stored' => !$isTest,
    'server_time_kst' => $entry['server_time_kst'],
], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);

function ensureDirectory(string $dir): void
{
    if (is_dir($dir)) return;
    if (!mkdir($dir, 0755, true) && !is_dir($dir)) {
        http_response_code(500);
        echo json_encode(['ok' => false, 'error' => 'mkdir_failed'], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        exit;
    }
}

function protectDataDirectory(string $baseDir): void
{
    $htaccess = $baseDir . '/.htaccess';
    if (!file_exists($htaccess)) {
        file_put_contents($htaccess, "Require all denied\nDeny from all\n");
    }
    $index = $baseDir . '/index.html';
    if (!file_exists($index)) {
        file_put_contents($index, '');
    }
}

function cleanString(mixed $value): string
{
    return substr(trim((string)$value), 0, 1000);
}

function sanitizeArray(array $value): array
{
    $result = [];
    foreach ($value as $key => $item) {
        $safeKey = substr(preg_replace('/[^A-Za-z0-9_:-]/', '', (string)$key), 0, 80);
        if ($safeKey === '') continue;
        if (is_array($item)) {
            $result[$safeKey] = sanitizeArray($item);
        } elseif (is_bool($item) || is_int($item) || is_float($item) || $item === null) {
            $result[$safeKey] = $item;
        } else {
            $result[$safeKey] = substr((string)$item, 0, 1000);
        }
    }
    return $result;
}
