<?php
declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');

require_once __DIR__ . '/order-store-lib.php';
require_once __DIR__ . '/rate-limit-lib.php';

function jsonResponse(int $status, array $payload): void
{
    http_response_code($status);
    echo json_encode($payload, JSON_UNESCAPED_UNICODE);
    exit;
}

function envValue(string $key, string $default = ''): string
{
    return ittemmallConfigValue($key, $default);
}

function naverPayApiDomain(string $mode): string
{
    return $mode === 'production' ? 'pay.paygate.naver.com' : 'dev-pay.paygate.naver.com';
}

function naverPayApproveEndpoint(string $mode): string
{
    $override = envValue('NAVER_PAY_APPROVE_URL');
    if ($override !== '') {
        if (stripos($override, 'https://') !== 0) {
            jsonResponse(500, [
                'ok' => false,
                'error' => 'NAVER_PAY_APPROVE_URL_INVALID',
                'message' => 'NAVER_PAY_APPROVE_URL은 HTTPS 전체 URL이어야 합니다.',
            ]);
        }
        return $override;
    }

    return 'https://' . naverPayApiDomain($mode) . '/naverpay-partner/naverpay/payments/v2.2/apply/payment';
}

function loadExpectedOrder(string $merchantPayKey): ?array
{
    return ittemmallFindServerOrder($merchantPayKey);
}

function approveNaverPayPayment(
    string $endpoint,
    string $clientId,
    string $clientSecret,
    string $chainId,
    string $paymentId,
    string $merchantPayKey
): array {
    if (!function_exists('curl_init')) {
        jsonResponse(500, ['ok' => false, 'error' => 'PHP_CURL_NOT_AVAILABLE']);
    }

    $idempotencyKey = substr(hash('sha256', $merchantPayKey . ':' . $paymentId), 0, 64);
    $curl = curl_init($endpoint);
    curl_setopt_array($curl, [
        CURLOPT_POST => true,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_CONNECTTIMEOUT => 10,
        CURLOPT_TIMEOUT => 60,
        CURLOPT_HTTPHEADER => [
            'X-Naver-Client-Id: ' . $clientId,
            'X-Naver-Client-Secret: ' . $clientSecret,
            'X-NaverPay-Chain-Id: ' . $chainId,
            'X-NaverPay-Idempotency-Key: ' . $idempotencyKey,
            'Content-Type: application/x-www-form-urlencoded',
        ],
        CURLOPT_POSTFIELDS => http_build_query(['paymentId' => $paymentId], '', '&', PHP_QUERY_RFC3986),
    ]);

    $responseBody = curl_exec($curl);
    $curlError = curl_error($curl);
    $httpStatus = (int)curl_getinfo($curl, CURLINFO_HTTP_CODE);
    curl_close($curl);

    if ($responseBody === false) {
        jsonResponse(502, [
            'ok' => false,
            'error' => 'NAVER_PAY_APPROVE_REQUEST_FAILED',
            'message' => $curlError,
        ]);
    }

    $decoded = json_decode((string)$responseBody, true);
    if (!is_array($decoded)) {
        jsonResponse(502, [
            'ok' => false,
            'error' => 'NAVER_PAY_APPROVE_INVALID_JSON',
            'status' => $httpStatus,
        ]);
    }

    return ['status' => $httpStatus, 'body' => $decoded];
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    jsonResponse(405, ['ok' => false, 'error' => 'METHOD_NOT_ALLOWED']);
}

try {
    $rateLimit = ittemmallRateLimitCheck('naverpay-approve', 30, 600);
    if (!$rateLimit['allowed']) {
        header('Retry-After: ' . (string)$rateLimit['retryAfter']);
        jsonResponse(429, [
            'ok' => false,
            'error' => 'RATE_LIMITED',
            'retryAfter' => $rateLimit['retryAfter'],
        ]);
    }
} catch (Throwable $error) {
    jsonResponse(500, [
        'ok' => false,
        'error' => 'RATE_LIMIT_FAILED',
        'message' => $error->getMessage(),
    ]);
}

$rawBody = file_get_contents('php://input') ?: '';
$body = json_decode($rawBody, true);

if (!is_array($body)) {
    jsonResponse(400, ['ok' => false, 'error' => 'INVALID_JSON']);
}

$paymentId = trim((string)($body['paymentId'] ?? ''));
$merchantPayKey = trim((string)($body['merchantPayKey'] ?? $body['orderId'] ?? ''));

if ($paymentId === '' || $merchantPayKey === '') {
    jsonResponse(400, ['ok' => false, 'error' => 'MISSING_REQUIRED_FIELDS']);
}

$mode = envValue('NAVER_PAY_MODE', 'development');
$endpoint = naverPayApproveEndpoint($mode);

if (envValue('NAVER_PAY_APPROVE_ENABLED') !== '1') {
    jsonResponse(501, [
        'ok' => false,
        'error' => 'APPROVE_API_DISABLED',
        'message' => '공식 승인 API 호출 코드는 준비되어 있습니다. 가맹 심사, 서버 주문 저장소, 비밀키 설정 후 NAVER_PAY_APPROVE_ENABLED=1로 켜세요.',
        'endpoint' => $endpoint,
        'received' => [
            'paymentId' => $paymentId,
            'merchantPayKey' => $merchantPayKey,
        ],
    ]);
}

$clientId = envValue('NAVER_PAY_CLIENT_ID');
$clientSecret = envValue('NAVER_PAY_CLIENT_SECRET');
$chainId = envValue('NAVER_PAY_CHAIN_ID');

if ($clientId === '' || $clientSecret === '' || $chainId === '') {
    jsonResponse(500, ['ok' => false, 'error' => 'NAVER_PAY_CONFIG_MISSING']);
}

$order = loadExpectedOrder($merchantPayKey);
if ($order === null) {
    jsonResponse(501, [
        'ok' => false,
        'error' => 'SERVER_ORDER_STORAGE_NOT_CONNECTED',
        'message' => '승인 전 서버 주문 저장소에서 주문번호와 금액을 검증해야 합니다.',
        'received' => [
            'paymentId' => $paymentId,
            'merchantPayKey' => $merchantPayKey,
        ],
    ]);
}

$expectedAmount = (int)($order['amount'] ?? 0);
$existingPaymentId = trim((string)($order['paymentId'] ?? ''));
$paymentMethod = (string)($order['paymentMethod'] ?? '');
$paymentStatus = (string)($order['paymentStatus'] ?? '');
$orderStatus = (string)($order['status'] ?? '');

if ($paymentMethod !== 'naver_pay') {
    jsonResponse(409, [
        'ok' => false,
        'error' => 'ORDER_NOT_NAVER_PAY',
        'message' => '네이버페이 결제 주문만 승인 API를 호출할 수 있습니다.',
    ]);
}

if ($expectedAmount <= 0) {
    jsonResponse(409, [
        'ok' => false,
        'error' => 'ORDER_AMOUNT_INVALID',
        'message' => '서버 주문 금액이 유효하지 않습니다.',
    ]);
}

if ($paymentStatus === 'approved' || $orderStatus === 'payment_approved') {
    if ($existingPaymentId !== '' && hash_equals($existingPaymentId, $paymentId)) {
        jsonResponse(200, [
            'ok' => true,
            'paymentId' => $paymentId,
            'merchantPayKey' => $merchantPayKey,
            'amount' => (int)($order['approvedAmount'] ?? $expectedAmount),
            'orderStatus' => $orderStatus,
            'paymentStatus' => $paymentStatus,
            'idempotent' => true,
        ]);
    }

    jsonResponse(409, [
        'ok' => false,
        'error' => 'ORDER_ALREADY_APPROVED',
        'message' => '이미 다른 결제번호로 승인된 주문입니다.',
    ]);
}

if (in_array($paymentStatus, ['canceled', 'cancel_pending'], true) || in_array($orderStatus, ['payment_canceled', 'payment_cancel_pending'], true)) {
    jsonResponse(409, [
        'ok' => false,
        'error' => 'ORDER_NOT_APPROVABLE',
        'message' => '취소되었거나 취소 대기 중인 주문은 다시 승인할 수 없습니다.',
    ]);
}

if ($orderStatus !== 'payment_ready' || $paymentStatus !== 'ready') {
    jsonResponse(409, [
        'ok' => false,
        'error' => 'ORDER_NOT_READY_FOR_APPROVAL',
        'message' => '서버 주문이 네이버페이 승인 대기 상태가 아닙니다.',
        'current' => [
            'status' => $orderStatus,
            'paymentStatus' => $paymentStatus,
        ],
    ]);
}

$approval = approveNaverPayPayment($endpoint, $clientId, $clientSecret, $chainId, $paymentId, $merchantPayKey);
$naverBody = $approval['body'];
$detail = is_array($naverBody['body']['detail'] ?? null) ? $naverBody['body']['detail'] : [];
$approvedMerchantPayKey = (string)($detail['merchantPayKey'] ?? '');
$approvedAmount = (int)($detail['totalPayAmount'] ?? 0);

if (($naverBody['code'] ?? '') !== 'Success') {
    jsonResponse(502, [
        'ok' => false,
        'error' => 'NAVER_PAY_APPROVE_FAILED',
        'naverCode' => $naverBody['code'] ?? null,
        'naverMessage' => $naverBody['message'] ?? null,
    ]);
}

if ($approvedMerchantPayKey !== $merchantPayKey || ($expectedAmount > 0 && $approvedAmount !== $expectedAmount)) {
    jsonResponse(409, [
        'ok' => false,
        'error' => 'NAVER_PAY_APPROVAL_MISMATCH',
        'message' => '네이버페이 승인 응답이 서버 주문 정보와 일치하지 않습니다.',
        'expected' => [
            'merchantPayKey' => $merchantPayKey,
            'amount' => $expectedAmount,
        ],
        'approved' => [
            'merchantPayKey' => $approvedMerchantPayKey,
            'amount' => $approvedAmount,
        ],
    ]);
}

$savedOrder = ittemmallMarkServerOrderPaid($merchantPayKey, $paymentId, $approvedAmount, $detail);

jsonResponse(200, [
    'ok' => true,
    'paymentId' => $paymentId,
    'merchantPayKey' => $merchantPayKey,
    'amount' => $approvedAmount,
    'admissionState' => $detail['admissionState'] ?? null,
    'orderStatus' => $savedOrder['status'] ?? null,
    'paymentStatus' => $savedOrder['paymentStatus'] ?? null,
]);
