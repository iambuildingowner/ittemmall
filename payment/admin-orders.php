<?php
declare(strict_types=1);

require_once __DIR__ . '/order-store-lib.php';

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

function adminOrdersResponse(int $status, array $payload): void
{
    http_response_code($status);
    echo json_encode($payload, JSON_UNESCAPED_UNICODE);
    exit;
}

function adminOrdersRequestToken(): string
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

$adminToken = ittemmallConfigValue('ITTEMMALL_ADMIN_TOKEN');
if ($adminToken === '') {
    adminOrdersResponse(501, [
        'ok' => false,
        'error' => 'ADMIN_TOKEN_NOT_CONFIGURED',
        'message' => 'ITTEMMALL_ADMIN_TOKEN을 private config 또는 서버 환경변수에 설정해야 주문 조회 API가 활성화됩니다.',
    ]);
}

$requestToken = adminOrdersRequestToken();
if ($requestToken === '' || !hash_equals($adminToken, $requestToken)) {
    adminOrdersResponse(401, ['ok' => false, 'error' => 'UNAUTHORIZED']);
}

try {
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $rawBody = file_get_contents('php://input') ?: '';
        $body = json_decode($rawBody, true);
        if (!is_array($body)) {
            adminOrdersResponse(400, ['ok' => false, 'error' => 'INVALID_JSON']);
        }

        $action = ittemmallCleanString((string)($body['action'] ?? ''), 80);
        if ($action !== 'update_fulfillment') {
            adminOrdersResponse(400, ['ok' => false, 'error' => 'UNKNOWN_ACTION']);
        }

        $id = ittemmallCleanString((string)($body['orderId'] ?? ''), 120);
        $fulfillmentStatus = ittemmallCleanString((string)($body['fulfillmentStatus'] ?? ''), 80);
        $adminNote = ittemmallCleanString((string)($body['adminNote'] ?? ''), 1000);
        $shipment = is_array($body['shipment'] ?? null) ? $body['shipment'] : [];
        if ($id === '' || $fulfillmentStatus === '') {
            adminOrdersResponse(400, ['ok' => false, 'error' => 'MISSING_REQUIRED_FIELDS']);
        }

        $order = ittemmallUpdateServerOrderFulfillment($id, $fulfillmentStatus, $adminNote, $shipment);
        adminOrdersResponse(200, ['ok' => true, 'order' => $order]);
    }

    if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
        adminOrdersResponse(405, ['ok' => false, 'error' => 'METHOD_NOT_ALLOWED']);
    }

    $id = ittemmallCleanString((string)($_GET['id'] ?? ''), 120);
    if ($id !== '') {
        $order = ittemmallFindServerOrder($id);
        if ($order === null) {
            adminOrdersResponse(404, ['ok' => false, 'error' => 'ORDER_NOT_FOUND']);
        }
        adminOrdersResponse(200, ['ok' => true, 'order' => $order]);
    }

    $limit = (int)($_GET['limit'] ?? 100);
    adminOrdersResponse(200, [
        'ok' => true,
        'orders' => ittemmallRecentServerOrders($limit),
    ]);
} catch (Throwable $error) {
    adminOrdersResponse(500, [
        'ok' => false,
        'error' => 'ADMIN_ORDERS_FAILED',
        'message' => $error->getMessage(),
    ]);
}
