<?php
declare(strict_types=1);

require_once __DIR__ . '/order-store-lib.php';
require_once __DIR__ . '/rate-limit-lib.php';

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

function orderLookupResponse(int $status, array $payload): void
{
    http_response_code($status);
    echo json_encode($payload, JSON_UNESCAPED_UNICODE);
    exit;
}

function orderLookupDigits(string $value): string
{
    return preg_replace('/\D+/', '', $value) ?? '';
}

function orderLookupContactMatches(array $order, string $contact): bool
{
    $customer = is_array($order['customer'] ?? null) ? $order['customer'] : [];
    $contact = trim($contact);
    if ($contact === '') {
        return false;
    }
    if (strpos($contact, '@') !== false) {
        return strcasecmp($contact, (string)($customer['email'] ?? '')) === 0;
    }
    $givenDigits = orderLookupDigits($contact);
    $storedDigits = orderLookupDigits((string)($customer['phone'] ?? ''));
    return $givenDigits !== '' && $storedDigits !== '' && hash_equals($storedDigits, $givenDigits);
}

function orderLookupPaymentLabel(array $order): string
{
    $status = (string)($order['status'] ?? '');
    $paymentStatus = (string)($order['paymentStatus'] ?? '');
    if ($paymentStatus === 'canceled' || $status === 'payment_canceled') {
        return '결제 취소';
    }
    if ($paymentStatus === 'cancel_pending' || $status === 'payment_cancel_pending') {
        return '취소 대기';
    }
    if ($paymentStatus === 'approved' || $status === 'payment_approved') {
        return '결제 승인';
    }
    if (($order['paymentMethod'] ?? '') === 'naver_pay') {
        return '네이버페이 대기';
    }
    if (($order['paymentMethod'] ?? '') === 'toss_pg') {
        return '토스 PG 대기';
    }
    if ($status === 'order_received') {
        return '주문 접수';
    }
    return $status !== '' ? $status : '상태 확인';
}

function orderLookupFulfillmentLabel(string $value): string
{
    $labels = [
        'new' => '신규',
        'contacted' => '연락 완료',
        'manual_payment_confirmed' => '수동 입금 확인',
        'preparing' => '발송 준비',
        'shipped' => '발송 완료',
        'completed' => '처리 완료',
        'closed' => '종결',
    ];
    return $labels[$value] ?? '신규';
}

function orderLookupPublicOrder(array $order): array
{
    $shipment = is_array($order['shipment'] ?? null) ? $order['shipment'] : [];
    $trackingUrl = ittemmallCleanString((string)($shipment['trackingUrl'] ?? ''), 500);
    if ($trackingUrl !== '' && stripos($trackingUrl, 'https://') !== 0) {
        $trackingUrl = '';
    }

    return [
        'id' => (string)($order['id'] ?? ''),
        'productName' => (string)($order['productName'] ?? ''),
        'quantity' => (int)($order['quantity'] ?? 1),
        'amount' => (int)($order['amount'] ?? 0),
        'currency' => (string)($order['currency'] ?? 'KRW'),
        'paymentMethod' => (string)($order['paymentMethod'] ?? ''),
        'paymentStatus' => (string)($order['paymentStatus'] ?? ''),
        'paymentLabel' => orderLookupPaymentLabel($order),
        'fulfillmentStatus' => (string)($order['fulfillmentStatus'] ?? 'new'),
        'fulfillmentLabel' => orderLookupFulfillmentLabel((string)($order['fulfillmentStatus'] ?? 'new')),
        'createdAt' => (string)($order['createdAt'] ?? ''),
        'updatedAt' => (string)($order['updatedAt'] ?? ''),
        'approvedAt' => (string)($order['approvedAt'] ?? ''),
        'canceledAt' => (string)($order['canceledAt'] ?? ''),
        'shipment' => [
            'carrier' => (string)($shipment['carrier'] ?? ''),
            'trackingNumber' => (string)($shipment['trackingNumber'] ?? ''),
            'trackingUrl' => $trackingUrl,
            'shippedAt' => (string)($shipment['shippedAt'] ?? ''),
        ],
    ];
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    orderLookupResponse(405, ['ok' => false, 'error' => 'METHOD_NOT_ALLOWED']);
}

try {
    $rateLimit = ittemmallRateLimitCheck('order-lookup', 30, 600);
    if (!$rateLimit['allowed']) {
        header('Retry-After: ' . (string)$rateLimit['retryAfter']);
        orderLookupResponse(429, [
            'ok' => false,
            'error' => 'RATE_LIMITED',
            'retryAfter' => $rateLimit['retryAfter'],
        ]);
    }
} catch (Throwable $error) {
    orderLookupResponse(500, [
        'ok' => false,
        'error' => 'RATE_LIMIT_FAILED',
        'message' => $error->getMessage(),
    ]);
}

if (!ittemmallOrderStoreReady()) {
    orderLookupResponse(501, [
        'ok' => false,
        'error' => 'ITTEMMALL_ORDER_STORE_PATH_MISSING',
        'message' => '운영 서버 주문 저장소가 아직 연결되지 않았습니다.',
    ]);
}

$rawBody = file_get_contents('php://input') ?: '';
$body = json_decode($rawBody, true);
if (!is_array($body)) {
    orderLookupResponse(400, ['ok' => false, 'error' => 'INVALID_JSON']);
}

$orderId = ittemmallCleanString((string)($body['orderId'] ?? ''), 120);
$contact = ittemmallCleanString((string)($body['contact'] ?? ''), 160);
if ($orderId === '' || $contact === '') {
    orderLookupResponse(400, ['ok' => false, 'error' => 'MISSING_REQUIRED_FIELDS']);
}

try {
    $order = ittemmallFindServerOrder($orderId);
    if ($order === null || !orderLookupContactMatches($order, $contact)) {
        orderLookupResponse(404, [
            'ok' => false,
            'error' => 'ORDER_NOT_FOUND',
            'message' => '주문번호와 연락처가 일치하는 주문을 찾지 못했습니다.',
        ]);
    }

    orderLookupResponse(200, [
        'ok' => true,
        'order' => orderLookupPublicOrder($order),
    ]);
} catch (Throwable $error) {
    orderLookupResponse(500, [
        'ok' => false,
        'error' => 'ORDER_LOOKUP_FAILED',
        'message' => $error->getMessage(),
    ]);
}
