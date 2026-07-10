<?php
declare(strict_types=1);

require_once __DIR__ . '/server-config-lib.php';

function ittemmallStoreEnv(string $key, string $default = ''): string
{
    return ittemmallConfigValue($key, $default);
}

function ittemmallOrderStorePath(): string
{
    return ittemmallStoreEnv('ITTEMMALL_ORDER_STORE_PATH');
}

function ittemmallOrderStoreReady(): bool
{
    return ittemmallOrderStorePath() !== '';
}

function ittemmallEnsureOrderStoreDirectory(string $path): void
{
    $dir = dirname($path);
    if (!is_dir($dir) && !mkdir($dir, 0700, true)) {
        throw new RuntimeException('ORDER_STORE_DIRECTORY_CREATE_FAILED');
    }
}

function ittemmallOrderStoreLockPath(): string
{
    $path = ittemmallOrderStorePath();
    return $path === '' ? '' : $path . '.lock';
}

function ittemmallWithOrderStoreLock(callable $callback)
{
    $path = ittemmallOrderStorePath();
    if ($path === '') {
        throw new RuntimeException('ITTEMMALL_ORDER_STORE_PATH_MISSING');
    }

    ittemmallEnsureOrderStoreDirectory($path);
    $lockPath = ittemmallOrderStoreLockPath();
    $lock = fopen($lockPath, 'c');
    if ($lock === false) {
        throw new RuntimeException('ORDER_STORE_LOCK_OPEN_FAILED');
    }

    try {
        if (!flock($lock, LOCK_EX)) {
            throw new RuntimeException('ORDER_STORE_LOCK_FAILED');
        }
        return $callback();
    } finally {
        flock($lock, LOCK_UN);
        fclose($lock);
        @chmod($lockPath, 0600);
    }
}

function ittemmallProductCatalog(): array
{
    return [
        'product-005' => [
            'name' => '아쿠아글로우 테니스 브레이슬릿',
            'price' => 49900,
        ],
        'product-003' => [
            'name' => '빙하기 선풍기조끼',
            'price' => 59900,
            'optionAddOnPrices' => [
                '추가상품' => [
                    '보조배터리 10,000mAh 추가 (+9,900원)' => 9900,
                ],
            ],
        ],
        'product-006' => [
            'name' => '나이트클린 LED 모기트랩',
            'price' => 49900,
        ],
        'product-007' => [
            'name' => '썸머쿨 냉감패드',
            'price' => 39900,
        ],
        'product-010' => [
            'name' => '모닝핏 접이식 스팀다리미',
            'price' => 59900,
        ],
        'product-009' => [
            'name' => '쿨터치 냉각 손선풍기',
            'price' => 29900,
        ],
    ];
}

function ittemmallSelectedAddOnUnitTotal(array $product, array $selectedOptions): int
{
    $priceMap = is_array($product['optionAddOnPrices'] ?? null) ? $product['optionAddOnPrices'] : [];
    $total = 0;
    foreach ($priceMap as $label => $values) {
        if (!is_array($values)) {
            continue;
        }
        $selectedValue = (string)($selectedOptions[(string)$label] ?? '');
        $total += (int)($values[$selectedValue] ?? 0);
    }
    return max(0, $total);
}

function ittemmallCleanString(string $value, int $maxLength = 500): string
{
    $value = trim($value);
    if (function_exists('mb_substr')) {
        return mb_substr($value, 0, $maxLength, 'UTF-8');
    }
    return substr($value, 0, $maxLength);
}

function ittemmallCleanMap(array $input, int $maxItems = 20, int $maxLength = 200): array
{
    $output = [];
    foreach ($input as $key => $value) {
        if (count($output) >= $maxItems) {
            break;
        }
        if (!is_scalar($value)) {
            continue;
        }
        $output[ittemmallCleanString((string)$key, 80)] = ittemmallCleanString((string)$value, $maxLength);
    }
    return $output;
}

function ittemmallCleanCustomer(array $input): array
{
    return [
        'name' => ittemmallCleanString((string)($input['name'] ?? ''), 80),
        'phone' => ittemmallCleanString((string)($input['phone'] ?? ''), 40),
        'email' => ittemmallCleanString((string)($input['email'] ?? ''), 160),
        'fulfillmentPrimary' => ittemmallCleanString((string)($input['fulfillmentPrimary'] ?? ''), 300),
        'request' => ittemmallCleanString((string)($input['request'] ?? ''), 1000),
        'agreeNotice' => (bool)($input['agreeNotice'] ?? false),
        'agreeTermsPrivacy' => (bool)($input['agreeTermsPrivacy'] ?? false),
        'agreeContact' => (bool)($input['agreeContact'] ?? false),
    ];
}

function ittemmallValidateCustomer(array $customer): void
{
    if ((string)($customer['name'] ?? '') === '') {
        throw new InvalidArgumentException('CUSTOMER_NAME_REQUIRED');
    }

    $phone = (string)($customer['phone'] ?? '');
    $phoneDigits = preg_replace('/\D+/', '', $phone) ?? '';
    if (strlen($phoneDigits) < 9) {
        throw new InvalidArgumentException('CUSTOMER_PHONE_REQUIRED');
    }

    $email = (string)($customer['email'] ?? '');
    if ($email === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
        throw new InvalidArgumentException('CUSTOMER_EMAIL_INVALID');
    }

    if ((string)($customer['fulfillmentPrimary'] ?? '') === '') {
        throw new InvalidArgumentException('FULFILLMENT_PRIMARY_REQUIRED');
    }

    if (empty($customer['agreeNotice'])) {
        throw new InvalidArgumentException('ORDER_NOTICE_CONSENT_REQUIRED');
    }

    if (empty($customer['agreeTermsPrivacy'])) {
        throw new InvalidArgumentException('TERMS_PRIVACY_CONSENT_REQUIRED');
    }
}

function ittemmallOrderPaymentLocked(array $order): bool
{
    $status = (string)($order['status'] ?? '');
    $paymentStatus = (string)($order['paymentStatus'] ?? '');
    return in_array($status, [
        'payment_approved',
        'payment_canceled',
        'payment_cancel_pending',
    ], true) || in_array($paymentStatus, [
        'approved',
        'canceled',
        'cancel_pending',
    ], true);
}

function ittemmallNormalizeOrder(array $input, ?array $existing = null): array
{
    $catalog = ittemmallProductCatalog();
    $id = ittemmallCleanString((string)($input['id'] ?? ''), 90);
    if (!preg_match('/^IT-[A-Za-z0-9-]{6,90}$/', $id)) {
        throw new InvalidArgumentException('INVALID_ORDER_ID');
    }

    if (is_array($existing) && ittemmallOrderPaymentLocked($existing)) {
        return $existing;
    }

    $productId = ittemmallCleanString((string)($input['productId'] ?? ''), 80);
    if (!isset($catalog[$productId])) {
        throw new InvalidArgumentException('UNKNOWN_PRODUCT_ID');
    }

    $quantity = max(1, min(10, (int)($input['quantity'] ?? 1)));
    $paymentMethod = (string)($input['paymentMethod'] ?? 'standard');
    if (!in_array($paymentMethod, ['standard', 'toss_pg', 'naver_pay'], true)) {
        $paymentMethod = 'standard';
    }

    $selectedOptions = is_array($input['selectedOptions'] ?? null)
        ? ittemmallCleanMap($input['selectedOptions'])
        : [];
    $product = $catalog[$productId];
    $addOnUnitTotal = ittemmallSelectedAddOnUnitTotal($product, $selectedOptions);
    $now = gmdate('c');
    $amount = ((int)$product['price'] + $addOnUnitTotal) * $quantity;
    $customer = is_array($input['customer'] ?? null) ? ittemmallCleanCustomer($input['customer']) : ittemmallCleanCustomer([]);
    ittemmallValidateCustomer($customer);
    $origin = is_array($input['origin'] ?? null) ? ittemmallCleanMap($input['origin'], 10, 300) : [];

    $normalized = [
        'id' => $id,
        'productId' => $productId,
        'productName' => $product['name'],
        'selectedOptions' => $selectedOptions,
        'quantity' => $quantity,
        'price' => (int)$product['price'],
        'unitPrice' => (int)$product['price'] + $addOnUnitTotal,
        'addOnUnitTotal' => $addOnUnitTotal,
        'addOnTotal' => $addOnUnitTotal * $quantity,
        'amount' => $amount,
        'currency' => 'KRW',
        'customer' => $customer,
        'paymentMethod' => $paymentMethod,
        'status' => $paymentMethod === 'naver_pay' ? 'payment_ready' : 'order_received',
        'paymentStatus' => $paymentMethod === 'naver_pay' ? 'ready' : ($paymentMethod === 'toss_pg' ? 'toss_pg_pending' : 'manual_followup'),
        'origin' => $origin,
        'clientCreatedAt' => ittemmallCleanString((string)($input['createdAt'] ?? ''), 80),
        'clientUpdatedAt' => ittemmallCleanString((string)($input['updatedAt'] ?? ''), 80),
        'createdAt' => (string)($existing['createdAt'] ?? $now),
        'updatedAt' => $now,
    ];

    if (is_array($existing)) {
        foreach ([
            'fulfillmentStatus',
            'shipment',
            'adminNote',
            'adminUpdatedAt',
            'paymentId',
            'approvedAmount',
            'approvedAt',
            'naverPay',
            'canceledAmount',
            'cancelReason',
            'canceledAt',
            'cancelHistory',
            'naverPayCancel',
            'notificationSentAt',
            'notificationLastTriedAt',
            'notificationError',
        ] as $key) {
            if (array_key_exists($key, $existing)) {
                $normalized[$key] = $existing[$key];
            }
        }

        if (in_array((string)($existing['status'] ?? ''), [
            'payment_approved',
            'payment_canceled',
            'payment_cancel_pending',
        ], true)) {
            $normalized['status'] = (string)$existing['status'];
        }
        if (in_array((string)($existing['paymentStatus'] ?? ''), [
            'approved',
            'canceled',
            'cancel_pending',
        ], true)) {
            $normalized['paymentStatus'] = (string)$existing['paymentStatus'];
        }
    }

    return $normalized;
}

function ittemmallReadServerOrders(): array
{
    $path = ittemmallOrderStorePath();
    if ($path === '' || !is_file($path)) {
        return [];
    }

    $raw = file_get_contents($path);
    if ($raw === false || trim($raw) === '') {
        return [];
    }

    $orders = json_decode($raw, true);
    if (!is_array($orders)) {
        throw new RuntimeException('ORDER_STORE_INVALID_JSON');
    }

    return array_values(array_filter($orders, 'is_array'));
}

function ittemmallWriteServerOrders(array $orders): void
{
    $path = ittemmallOrderStorePath();
    if ($path === '') {
        throw new RuntimeException('ITTEMMALL_ORDER_STORE_PATH_MISSING');
    }

    ittemmallEnsureOrderStoreDirectory($path);

    $json = json_encode(array_values($orders), JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    if ($json === false) {
        throw new RuntimeException('ORDER_STORE_JSON_ENCODE_FAILED');
    }

    $tmpPath = $path . '.' . getmypid() . '.tmp';
    if (file_put_contents($tmpPath, $json, LOCK_EX) === false) {
        throw new RuntimeException('ORDER_STORE_WRITE_FAILED');
    }

    @chmod($tmpPath, 0600);
    if (is_file($path)) {
        @copy($path, $path . '.bak');
        @chmod($path . '.bak', 0600);
    }
    if (!rename($tmpPath, $path)) {
        @unlink($tmpPath);
        throw new RuntimeException('ORDER_STORE_RENAME_FAILED');
    }
    @chmod($path, 0600);
}

function ittemmallFindServerOrder(string $id): ?array
{
    foreach (ittemmallReadServerOrders() as $order) {
        if (($order['id'] ?? '') === $id) {
            return $order;
        }
    }
    return null;
}

function ittemmallUpsertServerOrder(array $input): array
{
    return ittemmallWithOrderStoreLock(static function () use ($input): array {
        $orders = ittemmallReadServerOrders();
        $existing = null;
        foreach ($orders as $order) {
            if (($order['id'] ?? '') === ($input['id'] ?? '')) {
                $existing = $order;
                break;
            }
        }

        $normalized = ittemmallNormalizeOrder($input, $existing);
        $nextOrders = [$normalized];
        foreach ($orders as $order) {
            if (($order['id'] ?? '') !== $normalized['id']) {
                $nextOrders[] = $order;
            }
        }

        ittemmallWriteServerOrders(array_slice($nextOrders, 0, 500));
        return $normalized;
    });
}

function ittemmallPatchServerOrder(string $id, array $patch): array
{
    return ittemmallWithOrderStoreLock(static function () use ($id, $patch): array {
        $orders = ittemmallReadServerOrders();
        $patchedOrder = null;
        $nextOrders = [];
        $now = gmdate('c');

        foreach ($orders as $order) {
            if (($order['id'] ?? '') === $id) {
                $patchedOrder = array_merge($order, $patch, ['updatedAt' => $now]);
                $nextOrders[] = $patchedOrder;
                continue;
            }
            $nextOrders[] = $order;
        }

        if ($patchedOrder === null) {
            throw new RuntimeException('ORDER_NOT_FOUND');
        }

        ittemmallWriteServerOrders($nextOrders);
        return $patchedOrder;
    });
}

function ittemmallAllowedFulfillmentStatuses(): array
{
    return [
        'new',
        'contacted',
        'manual_payment_confirmed',
        'preparing',
        'shipped',
        'completed',
        'closed',
    ];
}

function ittemmallShipmentCarrierKey(string $carrier): string
{
    $carrier = ittemmallCleanString($carrier, 80);
    $carrier = strtolower($carrier);
    return preg_replace('/[\s\-_\.]+/', '', $carrier) ?? $carrier;
}

function ittemmallShipmentTrackingUrl(string $carrier, string $trackingNumber): string
{
    $carrierKey = ittemmallShipmentCarrierKey($carrier);
    $trackingNumber = ittemmallCleanString($trackingNumber, 120);
    if ($carrierKey === '' || $trackingNumber === '') {
        return '';
    }

    $encodedTrackingNumber = rawurlencode($trackingNumber);
    $templates = [
        'cj대한통운' => 'https://trace.cjlogistics.com/next/tracking.html?wblNo=%s',
        '대한통운' => 'https://trace.cjlogistics.com/next/tracking.html?wblNo=%s',
        'cjlogistics' => 'https://trace.cjlogistics.com/next/tracking.html?wblNo=%s',
        'cj' => 'https://trace.cjlogistics.com/next/tracking.html?wblNo=%s',
        '우체국' => 'https://service.epost.go.kr/iservice/usr/trace/usrtrc001k01.jsp?sid1=%s',
        '우체국택배' => 'https://service.epost.go.kr/iservice/usr/trace/usrtrc001k01.jsp?sid1=%s',
        'epost' => 'https://service.epost.go.kr/iservice/usr/trace/usrtrc001k01.jsp?sid1=%s',
        'ems' => 'https://service.epost.go.kr/iservice/usr/trace/usrtrc001k01.jsp?sid1=%s',
        '롯데택배' => 'https://www.lotteglogis.com/home/reservation/tracking/linkView?InvNo=%s',
        '롯데글로벌로지스' => 'https://www.lotteglogis.com/home/reservation/tracking/linkView?InvNo=%s',
        'lotte' => 'https://www.lotteglogis.com/home/reservation/tracking/linkView?InvNo=%s',
        'lotteglogis' => 'https://www.lotteglogis.com/home/reservation/tracking/linkView?InvNo=%s',
        '한진택배' => 'https://www.hanjin.com/kor/CMS/DeliveryMgr/WaybillSch.do?mCode=MN038&schLang=KR&wblnumText2=%s',
        '한진' => 'https://www.hanjin.com/kor/CMS/DeliveryMgr/WaybillSch.do?mCode=MN038&schLang=KR&wblnumText2=%s',
        'hanjin' => 'https://www.hanjin.com/kor/CMS/DeliveryMgr/WaybillSch.do?mCode=MN038&schLang=KR&wblnumText2=%s',
        '로젠택배' => 'https://www.ilogen.com/web/personal/trace/%s',
        '로젠' => 'https://www.ilogen.com/web/personal/trace/%s',
        'logen' => 'https://www.ilogen.com/web/personal/trace/%s',
    ];

    return isset($templates[$carrierKey]) ? sprintf($templates[$carrierKey], $encodedTrackingNumber) : '';
}

function ittemmallCleanShipment(array $input): array
{
    $carrier = ittemmallCleanString((string)($input['carrier'] ?? ''), 80);
    $trackingNumber = ittemmallCleanString((string)($input['trackingNumber'] ?? ''), 120);
    $trackingUrl = ittemmallCleanString((string)($input['trackingUrl'] ?? ''), 500);
    $trackingUrlAuto = false;
    if ($trackingUrl === '') {
        $trackingUrl = ittemmallShipmentTrackingUrl($carrier, $trackingNumber);
        $trackingUrlAuto = $trackingUrl !== '';
    }

    return [
        'carrier' => $carrier,
        'trackingNumber' => $trackingNumber,
        'trackingUrl' => $trackingUrl,
        'trackingUrlAuto' => $trackingUrlAuto,
        'memo' => ittemmallCleanString((string)($input['memo'] ?? ''), 500),
    ];
}

function ittemmallUpdateServerOrderFulfillment(string $id, string $fulfillmentStatus, string $adminNote = '', array $shipmentInput = []): array
{
    $fulfillmentStatus = ittemmallCleanString($fulfillmentStatus, 80);
    if (!in_array($fulfillmentStatus, ittemmallAllowedFulfillmentStatuses(), true)) {
        throw new InvalidArgumentException('INVALID_FULFILLMENT_STATUS');
    }

    $shipment = ittemmallCleanShipment($shipmentInput);
    $existing = ittemmallFindServerOrder($id) ?: [];
    $existingShipment = is_array($existing['shipment'] ?? null) ? $existing['shipment'] : [];
    $previousCarrier = (string)($existingShipment['carrier'] ?? '');
    $previousTrackingNumber = (string)($existingShipment['trackingNumber'] ?? '');
    $previousTrackingUrl = (string)($existingShipment['trackingUrl'] ?? '');
    $nextCarrier = (string)($shipment['carrier'] ?? '');
    $nextTrackingNumber = (string)($shipment['trackingNumber'] ?? '');
    $nextTrackingUrl = (string)($shipment['trackingUrl'] ?? '');
    $trackingChanged = $nextCarrier !== $previousCarrier || $nextTrackingNumber !== $previousTrackingNumber || $nextTrackingUrl !== $previousTrackingUrl;
    $shippedAt = (string)($existingShipment['shippedAt'] ?? '');
    if ($fulfillmentStatus === 'shipped' && $nextTrackingNumber !== '' && $shippedAt === '') {
        $shippedAt = gmdate('c');
    }

    return ittemmallPatchServerOrder($id, [
        'fulfillmentStatus' => $fulfillmentStatus,
        'shipment' => array_merge($shipment, [
            'shippedAt' => $shippedAt,
            'trackingUpdatedAt' => $trackingChanged ? gmdate('c') : (string)($existingShipment['trackingUpdatedAt'] ?? ''),
        ]),
        'adminNote' => ittemmallCleanString($adminNote, 1000),
        'adminUpdatedAt' => gmdate('c'),
    ]);
}

function ittemmallOrderNotificationEnabled(): bool
{
    return ittemmallStoreEnv('ITTEMMALL_NOTIFY_ENABLED') === '1' && ittemmallStoreEnv('ITTEMMALL_NOTIFY_EMAIL') !== '';
}

function ittemmallOrderAdminUrl(string $id): string
{
    $baseUrl = rtrim(ittemmallStoreEnv('ITTEMMALL_SITE_BASE_URL', 'https://ittemmall.com'), '/');
    return $baseUrl . '/payment/admin.html#' . rawurlencode($id);
}

function ittemmallOrderNotificationSubject(array $order): string
{
    return '[ITTEMMALL] 새 주문 접수 ' . (string)($order['id'] ?? '');
}

function ittemmallMailHeaderValue(string $value, int $maxLength = 300): string
{
    return ittemmallCleanString(str_replace(["\r", "\n"], ' ', $value), $maxLength);
}

function ittemmallMailAddressOrDefault(string $value, string $default): string
{
    $value = ittemmallMailHeaderValue($value, 200);
    return filter_var($value, FILTER_VALIDATE_EMAIL) ? $value : $default;
}

function ittemmallMailSubject(string $subject): string
{
    $subject = ittemmallMailHeaderValue($subject, 160);
    if (function_exists('mb_encode_mimeheader')) {
        return mb_encode_mimeheader($subject, 'UTF-8');
    }
    return '=?UTF-8?B?' . base64_encode($subject) . '?=';
}

function ittemmallOrderNotificationBody(array $order): string
{
    $customer = is_array($order['customer'] ?? null) ? $order['customer'] : [];
    $selectedOptions = is_array($order['selectedOptions'] ?? null)
        ? json_encode($order['selectedOptions'], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)
        : '{}';
    return implode("\n", [
        'ITTEMMALL 새 주문이 접수되었습니다.',
        '',
        '주문번호: ' . (string)($order['id'] ?? ''),
        '상품: ' . (string)($order['productName'] ?? ''),
        '옵션: ' . (string)$selectedOptions,
        '수량: ' . (string)($order['quantity'] ?? ''),
        '추가상품 금액: ' . number_format((int)($order['addOnTotal'] ?? 0)) . ' KRW',
        '금액: ' . number_format((int)($order['amount'] ?? 0)) . ' KRW',
        '결제수단: ' . (string)($order['paymentMethod'] ?? ''),
        '결제상태: ' . (string)($order['paymentStatus'] ?? ''),
        '',
        '주문자: ' . (string)($customer['name'] ?? ''),
        '연락처: ' . (string)($customer['phone'] ?? ''),
        '이메일: ' . (string)($customer['email'] ?? ''),
        '주소: ' . (string)($customer['fulfillmentPrimary'] ?? ''),
        '요청사항: ' . (string)($customer['request'] ?? ''),
        '약관/개인정보 동의: ' . (!empty($customer['agreeTermsPrivacy']) ? 'Y' : 'N'),
        '연락 안내 동의: ' . (!empty($customer['agreeContact']) ? 'Y' : 'N'),
        '',
        '관리자: ' . ittemmallOrderAdminUrl((string)($order['id'] ?? '')),
    ]);
}

function ittemmallSendOrderNotification(array $order): array
{
    if (!ittemmallOrderNotificationEnabled()) {
        return ['ok' => false, 'skipped' => true, 'reason' => 'NOTIFICATION_DISABLED'];
    }
    if (!empty($order['notificationSentAt'])) {
        return ['ok' => true, 'skipped' => true, 'reason' => 'ALREADY_SENT'];
    }
    if (!function_exists('mail')) {
        ittemmallPatchServerOrder((string)$order['id'], [
            'notificationLastTriedAt' => gmdate('c'),
            'notificationError' => 'PHP_MAIL_NOT_AVAILABLE',
        ]);
        return ['ok' => false, 'skipped' => false, 'reason' => 'PHP_MAIL_NOT_AVAILABLE'];
    }

    $from = ittemmallMailAddressOrDefault(ittemmallStoreEnv('ITTEMMALL_NOTIFY_FROM', 'no-reply@ittemmall.com'), 'no-reply@ittemmall.com');
    $to = ittemmallMailAddressOrDefault(ittemmallStoreEnv('ITTEMMALL_NOTIFY_EMAIL'), $from);
    $replyTo = ittemmallMailAddressOrDefault((string)($order['customer']['email'] ?? ''), $from);
    $subject = ittemmallMailSubject(ittemmallOrderNotificationSubject($order));
    $body = ittemmallOrderNotificationBody($order);
    $headers = [
        'From: ITTEMMALL <' . $from . '>',
        'Reply-To: ' . $replyTo,
        'Content-Type: text/plain; charset=UTF-8',
    ];

    $sent = @mail($to, $subject, $body, implode("\n", $headers));
    ittemmallPatchServerOrder((string)$order['id'], [
        'notificationLastTriedAt' => gmdate('c'),
        'notificationSentAt' => $sent ? gmdate('c') : '',
        'notificationError' => $sent ? '' : 'PHP_MAIL_SEND_FAILED',
    ]);

    return [
        'ok' => $sent,
        'skipped' => false,
        'reason' => $sent ? 'SENT' : 'PHP_MAIL_SEND_FAILED',
    ];
}

function ittemmallMarkServerOrderPaid(string $id, string $paymentId, int $amount, array $naverDetail): array
{
    return ittemmallPatchServerOrder($id, [
        'status' => 'payment_approved',
        'paymentStatus' => 'approved',
        'paymentId' => ittemmallCleanString($paymentId, 120),
        'approvedAmount' => $amount,
        'approvedAt' => gmdate('c'),
        'naverPay' => [
            'paymentId' => ittemmallCleanString($paymentId, 120),
            'merchantPayKey' => ittemmallCleanString((string)($naverDetail['merchantPayKey'] ?? $id), 120),
            'totalPayAmount' => $amount,
            'admissionState' => ittemmallCleanString((string)($naverDetail['admissionState'] ?? ''), 80),
            'primaryPayMeans' => ittemmallCleanString((string)($naverDetail['primaryPayMeans'] ?? ''), 80),
        ],
    ]);
}

function ittemmallMarkServerOrderCanceled(
    string $id,
    string $paymentId,
    int $cancelAmount,
    string $cancelReason,
    array $naverBody,
    string $status = 'payment_canceled'
): array {
    $body = is_array($naverBody['body'] ?? null) ? $naverBody['body'] : [];
    $paymentStatus = $status === 'payment_cancel_pending' ? 'cancel_pending' : 'canceled';
    $existing = ittemmallFindServerOrder($id) ?: [];
    $cancelHistory = is_array($existing['cancelHistory'] ?? null) ? $existing['cancelHistory'] : [];
    $cancelHistory[] = [
        'paymentId' => ittemmallCleanString($paymentId, 120),
        'cancelAmount' => $cancelAmount,
        'cancelReason' => ittemmallCleanString($cancelReason, 256),
        'naverCode' => ittemmallCleanString((string)($naverBody['code'] ?? ''), 80),
        'naverMessage' => ittemmallCleanString((string)($naverBody['message'] ?? ''), 300),
        'payHistId' => ittemmallCleanString((string)($body['payHistId'] ?? ''), 120),
        'cancelYmdt' => ittemmallCleanString((string)($body['cancelYmdt'] ?? ''), 80),
        'createdAt' => gmdate('c'),
    ];

    return ittemmallPatchServerOrder($id, [
        'status' => $status,
        'paymentStatus' => $paymentStatus,
        'canceledAmount' => $cancelAmount,
        'cancelReason' => ittemmallCleanString($cancelReason, 256),
        'canceledAt' => gmdate('c'),
        'cancelHistory' => $cancelHistory,
        'naverPayCancel' => [
            'paymentId' => ittemmallCleanString($paymentId, 120),
            'cancelAmount' => $cancelAmount,
            'resultCode' => ittemmallCleanString((string)($naverBody['code'] ?? ''), 80),
            'payHistId' => ittemmallCleanString((string)($body['payHistId'] ?? ''), 120),
            'totalRestAmount' => (int)($body['totalRestAmount'] ?? 0),
            'applyRestAmount' => (int)($body['applyRestAmount'] ?? 0),
            'cancelYmdt' => ittemmallCleanString((string)($body['cancelYmdt'] ?? ''), 80),
        ],
    ]);
}

function ittemmallRecentServerOrders(int $limit = 100): array
{
    $orders = ittemmallReadServerOrders();
    usort($orders, static function (array $a, array $b): int {
        return strcmp((string)($b['updatedAt'] ?? ''), (string)($a['updatedAt'] ?? ''));
    });
    return array_slice($orders, 0, max(1, min(500, $limit)));
}
