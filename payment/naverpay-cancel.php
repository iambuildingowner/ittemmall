<?php
declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

require_once __DIR__ . '/order-store-lib.php';

function cancelResponse(int $status, array $payload): void
{
    http_response_code($status);
    echo json_encode($payload, JSON_UNESCAPED_UNICODE);
    exit;
}

function cancelConfig(string $key, string $default = ''): string
{
    return ittemmallConfigValue($key, $default);
}

function cancelRequestToken(): string
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

function naverPayCancelApiDomain(string $mode): string
{
    return $mode === 'production' ? 'pay.paygate.naver.com' : 'dev-pay.paygate.naver.com';
}

function naverPayCancelEndpoint(string $mode): string
{
    $override = cancelConfig('NAVER_PAY_CANCEL_URL');
    if ($override !== '') {
        if (stripos($override, 'https://') !== 0) {
            cancelResponse(500, [
                'ok' => false,
                'error' => 'NAVER_PAY_CANCEL_URL_INVALID',
                'message' => 'NAVER_PAY_CANCEL_URL은 HTTPS 전체 URL이어야 합니다.',
            ]);
        }
        return $override;
    }

    return 'https://' . naverPayCancelApiDomain($mode) . '/naverpay-partner/naverpay/payments/v1/cancel';
}

function requestNaverPayCancel(
    string $endpoint,
    string $clientId,
    string $clientSecret,
    string $chainId,
    string $orderId,
    string $paymentId,
    int $cancelAmount,
    int $expectedRestAmount,
    string $cancelReason
): array {
    if (!function_exists('curl_init')) {
        cancelResponse(500, ['ok' => false, 'error' => 'PHP_CURL_NOT_AVAILABLE']);
    }

    $idempotencyKey = substr(hash('sha256', $orderId . ':' . $paymentId . ':' . $cancelAmount . ':cancel'), 0, 64);
    $fields = [
        'paymentId' => $paymentId,
        'merchantPayTransactionKey' => $orderId . '-cancel-' . gmdate('YmdHis'),
        'cancelAmount' => $cancelAmount,
        'cancelReason' => $cancelReason,
        'cancelRequester' => '2',
        'taxScopeAmount' => $cancelAmount,
        'taxExScopeAmount' => 0,
        'doCompareRest' => 1,
        'expectedRestAmount' => $expectedRestAmount,
    ];

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
        CURLOPT_POSTFIELDS => http_build_query($fields, '', '&', PHP_QUERY_RFC3986),
    ]);

    $responseBody = curl_exec($curl);
    $curlError = curl_error($curl);
    $httpStatus = (int)curl_getinfo($curl, CURLINFO_HTTP_CODE);
    curl_close($curl);

    if ($responseBody === false) {
        cancelResponse(502, [
            'ok' => false,
            'error' => 'NAVER_PAY_CANCEL_REQUEST_FAILED',
            'message' => $curlError,
        ]);
    }

    $decoded = json_decode((string)$responseBody, true);
    if (!is_array($decoded)) {
        cancelResponse(502, [
            'ok' => false,
            'error' => 'NAVER_PAY_CANCEL_INVALID_JSON',
            'status' => $httpStatus,
        ]);
    }

    return ['status' => $httpStatus, 'body' => $decoded];
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    cancelResponse(405, ['ok' => false, 'error' => 'METHOD_NOT_ALLOWED']);
}

$adminToken = cancelConfig('ITTEMMALL_ADMIN_TOKEN');
if ($adminToken === '') {
    cancelResponse(501, [
        'ok' => false,
        'error' => 'ADMIN_TOKEN_NOT_CONFIGURED',
        'message' => 'ITTEMMALL_ADMIN_TOKEN을 private config 또는 서버 환경변수에 설정해야 결제 취소 API가 활성화됩니다.',
    ]);
}

$requestToken = cancelRequestToken();
if ($requestToken === '' || !hash_equals($adminToken, $requestToken)) {
    cancelResponse(401, ['ok' => false, 'error' => 'UNAUTHORIZED']);
}

$rawBody = file_get_contents('php://input') ?: '';
$body = json_decode($rawBody, true);
if (!is_array($body)) {
    cancelResponse(400, ['ok' => false, 'error' => 'INVALID_JSON']);
}

$orderId = ittemmallCleanString((string)($body['orderId'] ?? ''), 120);
$cancelReason = ittemmallCleanString((string)($body['cancelReason'] ?? '관리자 요청 취소'), 256);
if ($orderId === '') {
    cancelResponse(400, ['ok' => false, 'error' => 'MISSING_ORDER_ID']);
}

$order = ittemmallFindServerOrder($orderId);
if ($order === null) {
    cancelResponse(404, ['ok' => false, 'error' => 'ORDER_NOT_FOUND']);
}

$paymentId = ittemmallCleanString((string)($order['paymentId'] ?? ($order['naverPay']['paymentId'] ?? '')), 120);
$approvedAmount = (int)($order['approvedAmount'] ?? $order['amount'] ?? 0);
$requestedCancelAmount = (int)($body['cancelAmount'] ?? 0);

if (($order['paymentStatus'] ?? '') !== 'approved' || $paymentId === '' || $approvedAmount <= 0) {
    cancelResponse(409, [
        'ok' => false,
        'error' => 'ORDER_NOT_CANCELABLE',
        'message' => '네이버페이 승인 완료 주문만 서버 취소를 요청할 수 있습니다.',
    ]);
}

if ($requestedCancelAmount > 0 && $requestedCancelAmount !== $approvedAmount) {
    cancelResponse(400, [
        'ok' => false,
        'error' => 'PARTIAL_CANCEL_NOT_SUPPORTED',
        'message' => '현재 관리자 취소 흐름은 전체 취소만 지원합니다. 부분취소는 별도 정책/화면을 만든 뒤 활성화하세요.',
    ]);
}

$cancelAmount = $approvedAmount;
$expectedRestAmount = 0;

$mode = cancelConfig('NAVER_PAY_MODE', 'development');
$endpoint = naverPayCancelEndpoint($mode);

if (cancelConfig('NAVER_PAY_CANCEL_ENABLED') !== '1') {
    cancelResponse(501, [
        'ok' => false,
        'error' => 'CANCEL_API_DISABLED',
        'message' => '네이버페이 취소 API 호출 코드는 준비되어 있습니다. 운영 키, 주문 저장소, 취소 정책 확인 후 NAVER_PAY_CANCEL_ENABLED=1로 켜세요.',
        'endpoint' => $endpoint,
        'received' => [
            'orderId' => $orderId,
            'paymentId' => $paymentId,
            'cancelAmount' => $cancelAmount,
        ],
    ]);
}

$clientId = cancelConfig('NAVER_PAY_CLIENT_ID');
$clientSecret = cancelConfig('NAVER_PAY_CLIENT_SECRET');
$chainId = cancelConfig('NAVER_PAY_CHAIN_ID');

if ($clientId === '' || $clientSecret === '' || $chainId === '') {
    cancelResponse(500, ['ok' => false, 'error' => 'NAVER_PAY_CONFIG_MISSING']);
}

$cancel = requestNaverPayCancel($endpoint, $clientId, $clientSecret, $chainId, $orderId, $paymentId, $cancelAmount, $expectedRestAmount, $cancelReason);
$naverBody = $cancel['body'];
$naverCode = (string)($naverBody['code'] ?? '');

if ($naverCode !== 'Success' && $naverCode !== 'CancelNotComplete') {
    cancelResponse(502, [
        'ok' => false,
        'error' => 'NAVER_PAY_CANCEL_FAILED',
        'naverCode' => $naverCode,
        'naverMessage' => $naverBody['message'] ?? null,
    ]);
}

$status = $naverCode === 'CancelNotComplete' ? 'payment_cancel_pending' : 'payment_canceled';
$savedOrder = ittemmallMarkServerOrderCanceled($orderId, $paymentId, $cancelAmount, $cancelReason, $naverBody, $status);

cancelResponse(200, [
    'ok' => true,
    'order' => $savedOrder,
    'naverCode' => $naverCode,
    'paymentId' => $paymentId,
    'cancelAmount' => $cancelAmount,
]);
