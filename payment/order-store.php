<?php
declare(strict_types=1);

require_once __DIR__ . '/order-store-lib.php';
require_once __DIR__ . '/rate-limit-lib.php';

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

function orderStoreResponse(int $status, array $payload): void
{
    http_response_code($status);
    echo json_encode($payload, JSON_UNESCAPED_UNICODE);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    orderStoreResponse(405, ['ok' => false, 'error' => 'METHOD_NOT_ALLOWED']);
}

try {
    $rateLimit = ittemmallRateLimitCheck('order-store', 20, 3600);
    if (!$rateLimit['allowed']) {
        header('Retry-After: ' . (string)$rateLimit['retryAfter']);
        orderStoreResponse(429, [
            'ok' => false,
            'error' => 'RATE_LIMITED',
            'retryAfter' => $rateLimit['retryAfter'],
        ]);
    }
} catch (Throwable $error) {
    orderStoreResponse(500, [
        'ok' => false,
        'error' => 'RATE_LIMIT_FAILED',
        'message' => $error->getMessage(),
    ]);
}

if (!ittemmallOrderStoreReady()) {
    orderStoreResponse(501, [
        'ok' => false,
        'error' => 'ITTEMMALL_ORDER_STORE_PATH_MISSING',
        'message' => 'ITTEMMALL_ORDER_STORE_PATH를 웹 공개 폴더 밖의 JSON 파일 경로로 설정해야 서버 주문 저장을 사용할 수 있습니다.',
    ]);
}

$rawBody = file_get_contents('php://input') ?: '';
$body = json_decode($rawBody, true);

if (!is_array($body)) {
    orderStoreResponse(400, ['ok' => false, 'error' => 'INVALID_JSON']);
}

$order = $body['order'] ?? $body;
if (!is_array($order)) {
    orderStoreResponse(400, ['ok' => false, 'error' => 'INVALID_ORDER_PAYLOAD']);
}

try {
    $savedOrder = ittemmallUpsertServerOrder($order);
    $notification = ittemmallSendOrderNotification($savedOrder);
    orderStoreResponse(200, [
        'ok' => true,
        'notification' => $notification,
        'order' => [
            'id' => $savedOrder['id'],
            'productId' => $savedOrder['productId'],
            'productName' => $savedOrder['productName'],
            'quantity' => $savedOrder['quantity'],
            'amount' => $savedOrder['amount'],
            'currency' => $savedOrder['currency'],
            'paymentMethod' => $savedOrder['paymentMethod'],
            'status' => $savedOrder['status'],
            'paymentStatus' => $savedOrder['paymentStatus'],
            'serverStoredAt' => $savedOrder['updatedAt'],
        ],
    ]);
} catch (InvalidArgumentException $error) {
    orderStoreResponse(400, [
        'ok' => false,
        'error' => $error->getMessage(),
    ]);
} catch (Throwable $error) {
    orderStoreResponse(500, [
        'ok' => false,
        'error' => 'ORDER_STORE_FAILED',
        'message' => $error->getMessage(),
    ]);
}
