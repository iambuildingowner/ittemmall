<?php
declare(strict_types=1);

require_once __DIR__ . '/order-store-lib.php';

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

function notificationTestResponse(int $status, array $payload): void
{
    http_response_code($status);
    echo json_encode($payload, JSON_UNESCAPED_UNICODE);
    exit;
}

function notificationTestRequestToken(): string
{
    $headerToken = $_SERVER['HTTP_X_ITTEMMALL_ADMIN_TOKEN'] ?? '';
    if (trim((string)$headerToken) !== '') {
        return trim((string)$headerToken);
    }

    $authorization = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
    if (preg_match('/^Bearer\s+(.+)$/i', (string)$authorization, $matches)) {
        return trim($matches[1]);
    }

    return '';
}

function notificationTestMaskEmail(string $email): string
{
    $email = trim($email);
    $parts = explode('@', $email, 2);
    if (count($parts) !== 2) {
        return '';
    }
    $name = $parts[0];
    $domain = $parts[1];
    $visible = substr($name, 0, 2);
    return $visible . str_repeat('*', max(2, strlen($name) - strlen($visible))) . '@' . $domain;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    notificationTestResponse(405, ['ok' => false, 'error' => 'METHOD_NOT_ALLOWED']);
}

$adminToken = ittemmallConfigValue('ITTEMMALL_ADMIN_TOKEN');
if ($adminToken === '') {
    notificationTestResponse(501, [
        'ok' => false,
        'error' => 'ADMIN_TOKEN_NOT_CONFIGURED',
        'message' => 'ITTEMMALL_ADMIN_TOKEN을 private config 또는 서버 환경변수에 설정해야 알림 테스트를 사용할 수 있습니다.',
    ]);
}

$requestToken = notificationTestRequestToken();
if ($requestToken === '' || !hash_equals($adminToken, $requestToken)) {
    notificationTestResponse(401, ['ok' => false, 'error' => 'UNAUTHORIZED']);
}

if (ittemmallConfigValue('ITTEMMALL_NOTIFY_ENABLED') !== '1') {
    notificationTestResponse(501, [
        'ok' => false,
        'error' => 'NOTIFICATION_DISABLED',
        'message' => 'ITTEMMALL_NOTIFY_ENABLED=1로 설정한 뒤 알림 테스트를 실행하세요.',
    ]);
}

if (!function_exists('mail')) {
    notificationTestResponse(500, [
        'ok' => false,
        'error' => 'PHP_MAIL_NOT_AVAILABLE',
        'message' => '현재 PHP 서버에서 mail() 함수를 사용할 수 없습니다.',
    ]);
}

$to = ittemmallConfigValue('ITTEMMALL_NOTIFY_EMAIL');
if ($to === '' || filter_var($to, FILTER_VALIDATE_EMAIL) === false) {
    notificationTestResponse(500, [
        'ok' => false,
        'error' => 'NOTIFY_EMAIL_INVALID',
        'message' => 'ITTEMMALL_NOTIFY_EMAIL이 비어 있거나 이메일 형식이 아닙니다.',
    ]);
}

$from = ittemmallMailAddressOrDefault(ittemmallConfigValue('ITTEMMALL_NOTIFY_FROM', 'no-reply@ittemmall.com'), 'no-reply@ittemmall.com');
$rawBody = file_get_contents('php://input') ?: '';
$body = json_decode($rawBody, true);
$message = is_array($body) ? ittemmallCleanString((string)($body['message'] ?? ''), 500) : '';
$sentAt = gmdate('c');
$subject = ittemmallMailSubject('[ITTEMMALL] 주문 알림 테스트');
$siteBaseUrl = rtrim(ittemmallConfigValue('ITTEMMALL_SITE_BASE_URL', 'https://ittemmall.com'), '/');
$mailBody = implode("\n", [
    'ITTEMMALL 주문 알림 테스트입니다.',
    '',
    '발송 시각(UTC): ' . $sentAt,
    '사이트: ' . $siteBaseUrl,
    '관리자: ' . $siteBaseUrl . '/payment/admin.html',
    '운영점검: ' . $siteBaseUrl . '/payment/ops.html',
    '',
    '메시지: ' . ($message !== '' ? $message : '운영 서버 메일 발송 확인'),
]);
$headers = [
    'From: ITTEMMALL <' . $from . '>',
    'Reply-To: ' . $from,
    'Content-Type: text/plain; charset=UTF-8',
];

$sent = @mail($to, $subject, $mailBody, implode("\n", $headers));
if (!$sent) {
    notificationTestResponse(500, [
        'ok' => false,
        'error' => 'PHP_MAIL_SEND_FAILED',
        'message' => 'mail() 호출이 실패했습니다. 호스팅 메일 정책 또는 발신 주소를 확인하세요.',
    ]);
}

notificationTestResponse(200, [
    'ok' => true,
    'sentAt' => $sentAt,
    'recipient' => notificationTestMaskEmail($to),
]);
